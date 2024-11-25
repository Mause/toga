from asyncio import Task, get_event_loop

from winrt.windows.devices.enumeration import DeviceInformation
from winrt.windows.graphics.imaging import BitmapEncoder
from winrt.windows.media.capture import MediaCapture
from winrt.windows.media.mediaproperties import (
    ImageEncodingProperties,
    MediaPixelFormat,
)
from winrt.windows.storage.streams import (
    Buffer,
    InMemoryRandomAccessStream,
    InputStreamOptions,
)

from toga.handlers import AsyncResult


def set_from(result: AsyncResult, coro):
    task: Task = get_event_loop().create_task(coro)
    task.add_done_callback(
        lambda res: (
            result.set_exception(res.exception())
            if res.exception()
            else result.set_result(res.result())
        )
    )


class Camera:
    def __init__(self, interface):
        pass

    def get_devices(self, result: AsyncResult):
        async def _get():
            return list(await DeviceInformation.find_all_async())

        set_from(result, _get())

    def has_permission(self) -> bool:
        return True

    def take_photo(self, photo, device=None, flash=None):
        set_from(photo, self._take_photo(device, flash))

    async def _take_photo(self, device=None, flash=None):
        mediaCapture = MediaCapture()
        await mediaCapture.initialize_async()

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

            return memoryview(
                await stream.read_async(buf, stream.size, InputStreamOptions.NONE)
            ).tobytes()
