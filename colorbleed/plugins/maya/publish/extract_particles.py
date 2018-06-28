import os

import pyblish_maya
import pyblish_magenta.api


class ExtractParticlesMayaAscii(pyblish_magenta.api.Extractor):
    """Extract as Maya Ascii"""

    label = "Particles (Maya Ascii)"
    hosts = ["maya"]
    families = ["colorbleed.particles"]

    def process(self, instance):
        from maya import cmds

        # Define extract output file path
        dir_path = self.temp_dir(instance)
        filename = "{0}.ma".format(instance.name)
        path = os.path.join(dir_path, filename)

        export = instance.data("exactExportMembers")

        # TODO: Make Avalon compatible
        # TODO: Transfer cache files and relink temporarily on the particles

        # Perform extraction
        self.log.info("Performing extraction..")
        with pyblish_maya.maintained_selection():
            cmds.select(export, noExpand=True)
            cmds.file(path,
                      force=True,
                      typ="mayaAscii",
                      exportSelected=True,
                      preserveReferences=False,
                      constructionHistory=False,
                      channels=True,    # allow animation
                      constraints=False,
                      shader=False,
                      expressions=False)

        self.log.info("Extracted instance '{0}' to: {1}".format(
            instance.name, path))

        if "files" not in instance.data:
            instance.data["files"] = []

        instance.data["files"].append(path)
