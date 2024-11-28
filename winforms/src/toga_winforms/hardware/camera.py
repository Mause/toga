from asyncio import ensure_future, get_event_loop
from collections.abc import Coroutine
from dataclasses import dataclass
from io import BytesIO

from pillow import Image
from winrt.windows.devices.enumeration import DeviceClass, DeviceInformation
from winrt.windows.graphics.imaging import BitmapEncoder
from winrt.windows.media.capture import MediaCapture, MediaCaptureInitializationSettings
from winrt.windows.media.mediaproperties import (
    ImageEncodingProperties,
    MediaPixelFormat,
)
from winrt.windows.security.authorization.appcapabilityaccess import (
    AppCapability,
    AppCapabilityAccessStatus,
)
from winrt.windows.storage.streams import (
    Buffer,
    InMemoryRandomAccessStream,
    InputStreamOptions,
)

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

    def get_devices(self):
        # TODO: why isn't get_devices async?
        async def _get():
            return [
                DeviceInfo(dev.id, dev.name, dev.flash_control.supported)
                for dev in await DeviceInformation.find_all_async(
                    DeviceClass.VIDEO_CAPTURE
                )
            ]

        return get_event_loop().run_until_complete(_get())

    def has_permission(self) -> bool:
        status = AppCapability.create("Webcam").check_access()

        return status == AppCapabilityAccessStatus.ALLOWED

    def request_permission(self, future: AsyncResult):
        set_from(future, AppCapability.create("Webcam").request_access_async())

    def take_photo(self, photo, device=None, flash=None):
        set_from(photo, self._take_photo(device, flash))

    async def _take_photo(self, device=None, flash=None):
        mediaCapture = MediaCapture()

        settings = MediaCaptureInitializationSettings()
        if device:
            settings.video_device_id = device.id

        await mediaCapture.initialize_async(settings)

        if flash:
            mediaCapture.video_device_controller.flash_control.enabled = True

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

            data = memoryview(
                await stream.read_async(buf, stream.size, InputStreamOptions.NONE)
            ).tobytes()

            return Image.open(BytesIO(data), formats=("png",))
