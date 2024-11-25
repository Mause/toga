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


class Camera:
    async def take_photo(self):
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
