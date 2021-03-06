import avalon.maya


class CreateVrayProxy(avalon.maya.Creator):
    """Alembic pointcache for animated data"""

    name = "vrayproxy"
    label = "VRay Proxy"
    family = "colorbleed.vrayproxy"
    icon = "gears"

    def __init__(self, *args, **kwargs):
        super(CreateVrayProxy, self).__init__(*args, **kwargs)

        self.data["animation"] = False
        self.data["startFrame"] = 1
        self.data["endFrame"] = 1

        # Write vertex colors
        self.data["vertexColors"] = False

