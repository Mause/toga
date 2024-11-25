from pytest import xfail

from .hardware import HardwareProbe


class CameraProbe(HardwareProbe):
    def cleanup(self):
        pass

    def grant_permission(self):
        pass

    def reject_permission(self):
        xfail("Winforms does not support camera permissions")

    def disconnect_cameras(self):
        pass

    def allow_permission(self):
        pass

    def request_permission_on_first_se(self):
        pass
