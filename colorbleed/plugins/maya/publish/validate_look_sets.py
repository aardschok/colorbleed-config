import colorbleed.maya.action
from colorbleed.maya import lib

import pyblish.api
import colorbleed.api


class ValidateLookSets(pyblish.api.InstancePlugin):
    """Validate if any sets are missing from the instance and look data

    A shader can be assigned to a node that is missing a Colorbleed ID.
    Because it is missing the ID it has not been collected in the instance.
    This validator ensures no relationships and thus considers it invalid
    if a relationship was not collected.

    When the relationship needs to be maintained the artist might need to
    create a different* relationship or ensure the node has the Colorbleed ID.

    *The relationship might be too broad (assigned to top node of hierarchy).
    This can be countered by creating the relationship on the shape or its
    transform. In essence, ensure item the shader is assigned to has the
    Colorbleed ID!

    Examples:

    - Displacement objectSets (like V-Ray):

        It is best practice to add the transform group of the shape to the
        displacement objectSet.

        Example content:
            [asset_GRP|geometry_GRP|body_GES,
             asset_GRP|geometry_GRP|L_eye_GES,
             asset_GRP|geometry_GRP|R_eye_GES,
             asset_GRP|geometry_GRP|wings_GEO]

    """

    order = colorbleed.api.ValidateContentsOrder
    families = ['colorbleed.look']
    hosts = ['maya']
    label = 'Look Sets'
    actions = [colorbleed.maya.action.SelectInvalidAction]

    def process(self, instance):
        """Process all the nodes in the instance"""

        invalid = self.get_invalid(instance)
        if invalid:
            raise RuntimeError("'{}' has invalid look "
                               "content".format(instance.name))

    @classmethod
    def get_invalid(cls, instance):
        """Get all invalid nodes"""

        cls.log.info("Validating look content for "
                     "'{}'".format(instance.name))

        relationships = instance.data["lookData"]["relationships"]
        invalid = []

        renderlayer = instance.data.get("renderlayer", "defaultRenderLayer")
        with lib.renderlayer(renderlayer):
            for node in instance:
                # get the connected objectSets of the node
                sets = lib.get_related_sets(node)
                if not sets:
                    continue

                # check if any objectSets are not present ion the relationships
                missing_sets = [s for s in sets if s not in relationships]
                if missing_sets:
                    # A set of this node is not coming along, this is wrong!
                    cls.log.error("Missing sets '{}' for node "
                                  "'{}'".format(missing_sets, node))
                    invalid.append(node)
                    continue

                # Ensure the node is in the sets that are collected
                for shaderset, data in relationships.items():
                    if shaderset not in sets:
                        # no need to check for a set if the node
                        # isn't in it anyway
                        continue

                    member_nodes = [member['name'] for member in
                                    data['members']]
                    if node not in member_nodes:
                        # The node is not found in the collected set
                        # relationships
                        cls.log.error("Missing '{}' in collected set node "
                                      "'{}'".format(node, shaderset))
                        invalid.append(node)

                        continue

        return invalid
