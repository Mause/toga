from asyncio import ensure_future
from collections.abc import Coroutine
from dataclasses import dataclass

from win32more.Windows.Devices.Enumeration import DeviceClass, DeviceInformation
from win32more.Windows.Graphics.Imaging import BitmapEncoder
from win32more.Windows.Media.Capture import (
    MediaCapture,
    MediaCaptureInitializationSettings,
)
from win32more.Windows.Media.MediaProperties import (
    ImageEncodingProperties,
    MediaPixelFormat,
)
from win32more.Windows.Security.Authorization.AppCapabilityAccess import (
    AppCapability,
    AppCapabilityAccessStatus,
)
from win32more.Windows.Storage.Streams import (
    Buffer,
    InMemoryRandomAccessStream,
    InputStreamOptions,
)

from toga import Image
from toga.constants import FlashMode
from toga.handlers import AsyncResult


def set_from(result: AsyncResult, coro: Coroutine):
    result.future = ensure_future(coro)


@dataclass
class DeviceInfo:
    id: str
    name: str
    has_flash: bool


class Camera:
    def __init__(self, interface):
        pass

    def get_devices(self, result: AsyncResult = None):
        async def _get():
            return [
                DeviceInfo(dev.id, dev.name, dev.flash_control.supported)
                for dev in await DeviceInformation.find_all_async(
                    DeviceClass.VIDEO_CAPTURE
                )
            ]

        if result is None:
            raise NotImplementedError()
        else:
            result.future = ensure_future(_get())

    def has_permission(self) -> bool:
        status = AppCapability.create("Webcam").check_access()

        return status == AppCapabilityAccessStatus.ALLOWED

    def request_permission(self, future: AsyncResult):
        set_from(future, AppCapability.create("Webcam").request_access_async())

    def take_photo(self, photo, device=None, flash: FlashMode = FlashMode.AUTO):
        set_from(photo, self._take_photo(device, flash))

    async def _take_photo(self, device, flash):
        mediaCapture = MediaCapture()

        settings = MediaCaptureInitializationSettings()
        if device:
            settings.video_device_id = device.id

        await mediaCapture.initialize_async(settings)

        flash_control = mediaCapture.video_device_controller
        if flash.supported:
            if flash == FlashMode.AUTO:
                flash_control.auto = True
            else:
                flash_control.enabled = flash == FlashMode.ON

        mediaCapture.add_failed(lambda obj, args: print(args.Message))

        lowLagCapture = await mediaCapture.prepare_low_lag_photo_capture_async(
            ImageEncodingProperties.create_uncompressed(MediaPixelFormat.BGRA8)
        )
        capturedPhoto = await lowLagCapture.capture_async()
        softwareBitmap = capturedPhoto.frame.software_bitmap
        await lowLagCapture.finish_async()
        with InMemoryRandomAccessStream() as stream:
            encoder = await BitmapEncoder.create_async(
                BitmapEncoder.png_encoder_id, stream
            )
            encoder.set_software_bitmap(softwareBitmap)
            await encoder.flush_async()
            buf = Buffer(stream.size)

            data = await stream.read_async(buf, stream.size, InputStreamOptions.NONE)

            return Image(data)
