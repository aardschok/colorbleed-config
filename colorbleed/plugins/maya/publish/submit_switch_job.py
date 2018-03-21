import os
import pprint

from avalon import api
from avalon.vendor import requests

import pyblish.api


def _get_script():
    """Get path to the image sequence script"""
    try:
        from colorbleed.scripts.fusion import switch_and_submit
    except Exception as e:
        raise RuntimeError("Expected module 'fusion_switch_shot'"
                           "to be available")

    module_path = switch_and_submit.__file__
    if module_path.endswith(".pyc"):
        module_path = module_path[:-len(".pyc")] + ".py"

    return module_path


class SubmitDependentSwitchJobDeadline(pyblish.api.ContextPlugin):
    """Run Switch Shot on specified comp as depending job

    """

    label = "Submit Switch Jobs to Deadline"
    order = pyblish.api.IntegratorOrder + 0.2
    hosts = ["maya"]
    families = ["colorbleed.renderlayer"]

    def process(self, context):

        instance = context[0]

        AVALON_DEADLINE = api.Session.get("AVALON_DEADLINE",
                                          "http://localhost:8082")
        assert AVALON_DEADLINE, "Requires AVALON_DEADLINE"

        job = instance.data.get("deadlineDependJob", None)
        if not job:
            self.log.warning("No dependent Job found")
            return True

        filepath = instance.data("flowFile", "")
        if not filepath:
            raise RuntimeError("No flow file (comp) chosen")

        shot = api.Session["AVALON_ASSET"]
        comment = instance.context.data["comment"]

        args = '--file_path "{}" --asset_name "{}" --render 1'.format(
            filepath, shot)
        payload_name = "{} SWITCH".format(os.path.basename(filepath))

        payload = {
            "JobInfo": {
                "Plugin": "Python",
                "BatchName": job["Props"]["Batch"],
                "Name": payload_name,
                "JobType": "Normal",
                "JobDependency0": job["_id"],
                "UserName": job["Props"]["User"],
                "Comment": comment,
                "InitialStatus": "Suspended"},
            "PluginInfo": {
                "Version": "3.6",
                "ScriptFile": _get_script(),
                "Arguments": args,
                "SingleFrameOnly": "True"
            },
            "AuxFiles": []
        }

        session = {}
        for index, key in enumerate(api.Session):
            dl_key = "EnvironmentKeyValue%d" % index
            value = "{key}={value}".format(key=key, value=api.Session[key])
            session[dl_key] = value

        payload.update(session)

        url = "{}/api/jobs".format(AVALON_DEADLINE)
        response = requests.post(url, json=payload)
        if not response.ok:
            raise Exception(response.text)

        # Temporary key name, deadlineSubmissionJob was already taken
        if instance.data("runSlapComp", False):
            instance.data["deadlineDependJob"] = response.json()

        self.log.info("Slap comp arguments: %s" % args)