import faulthandler

from pytest import xfail

from .hardware import CameraProbeMixin, HardwareProbe

faulthandler.enable()


class CameraProbe(HardwareProbe, CameraProbeMixin):
    def cleanup(self):
        pass

    def grant_permission(self):
        pass

    @property
    def shutter_enabled(self):
        # Shutter can't be disabled
        return True

    def reject_permission(self):
        xfail("Winforms does not support camera permissions")

    def disconnect_cameras(self):
        pass

    def allow_permission(self):
        pass

    async def press_shutter_button(self, photo):
        return "image", "device_used", "flash_mode"

    def request_permission_on_first_use(self):
        pass

    def cancel_photo(self, photo):
        pass

    def select_other_camera(self):
        pass

    async def wait_for_camera(self, device_count: int = 0):
        await self.redraw("Camera view displayed")

    @property
    def allow_no_camera(self):
        return True
