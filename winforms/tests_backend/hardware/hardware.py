from abc import ABC, abstractmethod

from ..app import AppProbe


class HardwareProbe(AppProbe):

    def __init__(self, monkeypatch, app_probe):
        super().__init__(app_probe.app)

        self.monkeypatch = monkeypatch


class CameraProbeMixin(ABC):

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def known_cameras(self):
        pass

    @abstractmethod
    def select_other_camera(self):
        pass

    @abstractmethod
    def disconnect_cameras(self):
        pass

    @abstractmethod
    def reset_permission(self):
        pass

    @abstractmethod
    def grant_permission(self):
        pass

    @abstractmethod
    def allow_permission(self):
        pass

    @abstractmethod
    def reject_permission(self):
        pass

    @abstractmethod
    async def wait_for_camera(self, device_count=0):
        pass

    @property
    @abstractmethod
    def shutter_enabled(self):
        pass

    @abstractmethod
    async def press_shutter_button(self, photo) -> tuple[str, str, str]:
        pass

    @abstractmethod
    async def cancel_photo(self, photo):
        pass

    @abstractmethod
    def same_device(self, device, native) -> bool:
        pass

    @abstractmethod
    def same_flash_mode(self, expected, actual) -> bool:
        pass
