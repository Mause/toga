from unittest.mock import Mock

from pytest import xfail
from System.Device.Location import (
    GeoCoordinate,
    GeoCoordinateWatcher,
    GeoPosition,
    GeoPositionChangedEventArgs,
    GeoPositionPermission,
)

from toga.types import LatLng

from .hardware import HardwareProbe


class LocationProbe(HardwareProbe):
    supports_background_permission = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app.location._impl.watcher = Mock(spec=GeoCoordinateWatcher)
        self.reset_locations()

    def cleanup(self):
        # Delete the location service instance. This ensures that a freshly mocked
        # LocationManager is installed for each test.
        try:
            del self.app._location
        except AttributeError:
            pass

    def allow_permission(self):
        self.app.location._impl.watcher.Permission = GeoPositionPermission.Granted

    def grant_permission(self):
        self.app.location._impl.watcher.Permission = GeoPositionPermission.Granted

    def reject_permission(self):
        self.app.location._impl.watcher.Permission = GeoPositionPermission.Denied

    def add_location(self, location: LatLng, altitude, cached=False):
        position = GeoPosition[GeoCoordinate]()
        position.Location = (
            GeoCoordinate(location.lat, location.lng)
            if altitude is None
            else GeoCoordinate(location.lat, location.lng, altitude)
        )

        self._locations.append(GeoPositionChangedEventArgs[GeoCoordinate](position))
        self.app.location._impl.watcher.Position = position

    def reset_locations(self):
        self._locations = []

    def allow_background_permission(self):
        """
        winforms doesn't distinguish between foreground and background access
        """
        pass

    async def simulate_location_error(self, loco):
        await self.redraw("Wait for location error")

        xfail("Winforms's location service doesn't raise errors on failure")

    def setup_location_error(self):
        # location error simulation handled by ``simulate_location_error``
        pass

    def setup_tracking_start_error(self):
        xfail("Tracking start cannot fail on Winforms")

    async def simulate_current_location(self, location):
        await self.redraw("Wait for current location")

        watcher = self.app.location._impl.watcher
        call = watcher.add_PositionChanged.mock_calls[0]
        cb = call.args[0]

        cb(None, self._locations[0])

        self.reset_locations()

        return await location

    async def simulate_location_update(self):
        self.app.location._impl._position_changed(None, self._locations[-1])
