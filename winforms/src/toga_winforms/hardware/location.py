from __future__ import annotations

from concurrent.futures import Future

from System import EventHandler
from System.Device.Location import (
    GeoCoordinate,
    GeoCoordinateWatcher,
    GeoPositionAccuracy,
    GeoPositionChangedEventArgs,
)

from toga import LatLng


def toga_location(location: GeoCoordinate):
    """Convert a GeoCoordinate into a Toga LatLng and altitude."""

    return {
        "location": LatLng(location.Latitude, location.Longitude),
        "altitude": location.Altitude,
        "speed": location.Speed,
    }


class Location:
    _location: Future

    def __init__(self, interface):
        self.watcher = GeoCoordinateWatcher(GeoPositionAccuracy.Default)
        self.watcher.add_PositionChanged(
            EventHandler[GeoPositionChangedEventArgs[GeoCoordinate]](
                self._position_changed
            )
        )
        self.watcher.Start()
        self._location = Future()

    def _position_changed(
        self, sender, event: GeoPositionChangedEventArgs[GeoCoordinate]
    ):
        self._location.set_result(event.Position.Location)

    def has_permission(self):
        return True

    def has_background_permission(self):
        return True

    def request_permission(self, future: Future):
        future.set_result(True)

    def request_background_permission(self, future: Future):
        future.set_result(True)

    def current_location(self, result: Future):
        self._location.add_done_callback(
            lambda value: result.set_result(toga_location(value))
        )

    def start_tracking(self):
        self.watcher.Start()

    def stop_tracking(self):
        self.watcher.Stop()
