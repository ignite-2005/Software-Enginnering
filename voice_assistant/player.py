"""Media player interface and an in-process player used for development/tests.

`MediaPlayerBackend` is the seam between the multimedia controller and the real
player on the target hardware (SAD section 2.7). Keeping it an interface is what
lets the controller be tested without audio hardware and lets the Raspberry Pi
backend be added without touching the control logic (NFR-05, NFR-06).
"""

from __future__ import annotations

from typing import Protocol

from voice_assistant.errors import PlayerOperationError

#: Player states used by the in-process player.
STOPPED = "stopped"
PLAYING = "playing"
PAUSED = "paused"


class MediaPlayerBackend(Protocol):
    """The operations a media player must expose (SAD API design 9.3-9.9).

    Any operation that cannot be carried out raises
    `voice_assistant.errors.PlayerOperationError` so the controller can report
    it through FR-11 without performing a different action.
    """

    def play(self) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def next_item(self) -> None: ...
    def previous_item(self) -> None: ...
    def volume_up(self) -> None: ...
    def volume_down(self) -> None: ...

    @property
    def state(self) -> str: ...


class InMemoryPlayer:
    """A player backend that records operations instead of producing audio.

    It is the double used by the test suite and by development runs on a machine
    without the project hardware. `fail_on` makes a named operation raise, which
    is how the media-player failure path of FR-11 is exercised.
    """

    def __init__(
        self,
        playlist: list[str] | None = None,
        *,
        volume: int = 50,
        fail_on: set[str] | None = None,
    ) -> None:
        self.playlist = list(playlist or ["track-1", "track-2", "track-3"])
        self.index = 0
        self.volume = volume
        self.fail_on = set(fail_on or ())
        self.calls: list[str] = []
        self.is_open = True
        self._state = STOPPED

    @property
    def state(self) -> str:
        return self._state

    @property
    def current_item(self) -> str | None:
        if not self.playlist:
            return None
        return self.playlist[self.index]

    def _record(self, operation: str) -> None:
        """Log the operation and honour an injected failure."""
        self.calls.append(operation)
        if operation in self.fail_on:
            raise PlayerOperationError(operation, f"injected {operation} failure")

    def play(self) -> None:
        self._record("play")
        self._state = PLAYING

    def pause(self) -> None:
        self._record("pause")
        if self._state != PLAYING:
            raise PlayerOperationError("pause", f"cannot pause while {self._state}")
        # The player stays open so that Resume remains possible (FR-04).
        self._state = PAUSED

    def resume(self) -> None:
        self._record("resume")
        if self._state != PAUSED:
            raise PlayerOperationError("resume", f"cannot resume while {self._state}")
        self._state = PLAYING

    def next_item(self) -> None:
        self._record("next_item")
        if self.index + 1 >= len(self.playlist):
            raise PlayerOperationError("next_item", "no next media item")
        self.index += 1

    def previous_item(self) -> None:
        self._record("previous_item")
        if self.index == 0:
            raise PlayerOperationError("previous_item", "no previous media item")
        self.index -= 1

    def volume_up(self, step: int = 10) -> None:
        self._record("volume_up")
        self.volume = min(100, self.volume + step)

    def volume_down(self, step: int = 10) -> None:
        self._record("volume_down")
        self.volume = max(0, self.volume - step)
