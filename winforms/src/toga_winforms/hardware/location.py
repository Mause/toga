from __future__ import annotations

from contextlib import contextmanager

from System import EventHandler
from System.Device.Location import (
    GeoCoordinate,
    GeoCoordinateWatcher,
    GeoPositionAccuracy,
    GeoPositionChangedEventArgs,
    GeoPositionPermission,
    GeoPositionStatus,
)

from toga import LatLng
from toga.handlers import AsyncResult


def toga_location(location: GeoCoordinate):
    """Convert a GeoCoordinate into a Toga LatLng and altitude."""

    if location.IsUnknown:
        return None

    return {
        "location": LatLng(location.Latitude, location.Longitude),
        "altitude": location.Altitude,
    }


class Location:
    def __init__(self, interface):
        self.interface = interface
        self.watcher = GeoCoordinateWatcher(GeoPositionAccuracy.Default)
        self._handler = EventHandler[GeoPositionChangedEventArgs[GeoCoordinate]](
            self._position_changed
        )
        self._has_background_permission = False

    def _position_changed(
        self, sender, event: GeoPositionChangedEventArgs[GeoCoordinate]
    ):
        location = toga_location(event.Position.Location)
        if location:
            self.interface.on_change(**location)

    def has_permission(self):
        return self.watcher.Permission == GeoPositionPermission.Granted

    def has_background_permission(self):
        return self._has_background_permission

    @contextmanager
    def context(self):
        already_started = self.watcher.Status == GeoPositionStatus.Ready
        self.watcher.Start(False)
        try:
            yield
        finally:
            if not already_started:  # don't want to stop if we're tracking
                self.watcher.Stop()

    def request_permission(self, future: AsyncResult[bool]) -> None:
        with self.context():
            future.set_result(self.has_permission())

    def request_background_permission(self, future: AsyncResult[bool]) -> None:
        if not self.has_permission():
            raise PermissionError()
        future.set_result(True)
        self._has_background_permission = True

    def current_location(self, result: AsyncResult[dict]) -> None:
        with self.context():
            loco = toga_location(self.watcher.Position.Location)
            # TODO: filter by horizontal accuracy?
            result.set_result(loco["location"] if loco else None)

    def start_tracking(self) -> None:
        self.watcher.Start()
        self.watcher.add_PositionChanged(self._handler)

    def stop_tracking(self) -> None:
        self.watcher.Stop()
        self.watcher.remove_PositionChanged(self._handler)
