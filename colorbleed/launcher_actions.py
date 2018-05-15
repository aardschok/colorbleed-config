import os
from avalon import api, lib, pipeline


class FusionRenderNode(api.Action):

    name = "fusionrendernode9"
    label = "F9 Render Node"
    icon = "object-group"
    order = 997

    def is_compatible(self, session):
        """Return whether the action is compatible with the session"""
        if "AVALON_PROJECT" in session:
            return False
        return True

    def process(self, session, **kwargs):
        """Implement the behavior for when the action is triggered

        Args:
            session (dict): environment dictionary

        Returns:
            Popen instance of newly spawned process

        """

        # Update environment with session
        env = os.environ.copy()
        env.update(session)

        # Get executable by name
        app = lib.get_application(self.name)
        env.update(app["environment"])
        executable = lib.which(app["executable"])

        return lib.launch(executable=executable, args=[], environment=env)


class VrayRenderSlave(api.Action):

    name = "vrayrenderslave"
    label = "V-Ray Slave"
    icon = "object-group"
    order = 996

    def is_compatible(self, session):
        """Return whether the action is compatible with the session"""
        if "AVALON_PROJECT" in session:
            return False
        return True

    def process(self, session, **kwargs):
        """Implement the behavior for when the action is triggered

        Args:
            session (dict): environment dictionary

        Returns:
            Popen instance of newly spawned process

        """

        # Update environment with session
        env = os.environ.copy()
        env.update(session)

        # Get executable by name
        app = lib.get_application(self.name)
        env.update(app["environment"])
        executable = lib.which(app["executable"])

        # Run as server
        arguments = ["-server", "-portNumber=20207"]

        return lib.launch(executable=executable,
                          args=arguments,
                          environment=env)


class FilePublisher(api.Action):

    name = "filepublisher"
    label = "File Publisher"
    icon = "filter"
    order = 998

    def is_compatible(self, session):
        required = ["AVALON_PROJECT", "AVALON_SILO", "AVALON_ASSET"]
        if not all(x for x in required if x in session):
            return False
        return True

    def process(self, session, **kwargs):
        import os

        env = os.environ.copy()
        env.update(session)

        try:
            return lib.launch(executable="python",
                              args=["-m", "filepublisher"],
                              environment=env)
        except Exception as exc:
            print(exc)


def register_launcher_actions():
    """Register specific actions which should be accessible in the launcher"""

    pipeline.register_plugin(api.Action, FusionRenderNode)
    pipeline.register_plugin(api.Action, VrayRenderSlave)
    pipeline.register_plugin(api.Action, FilePublisher)
