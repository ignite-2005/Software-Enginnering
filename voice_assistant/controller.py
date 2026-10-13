"""Multimedia controller (SAD section 2.6, SRS FR-03 to FR-09).

The controller is the only module that talks to the media player. Each method
maps exactly one validated command to exactly one player operation, which is
what keeps NFR-03 (a valid command never triggers a different operation)
testable.

Implemented here: `pause_media` (FR-04, story #10). The remaining operations are
owned by other Sprint 1/2 stories and raise `NotImplementedError` until then, so
an unfinished operation can never silently perform the wrong action.
"""

from __future__ import annotations

from voice_assistant.errors import PlayerOperationError
from voice_assistant.player import MediaPlayerBackend, PAUSED, PLAYING


class MultimediaController:
    """Maps multimedia operations onto a `MediaPlayerBackend`."""

    def __init__(self, player: MediaPlayerBackend) -> None:
        self._player = player

    @property
    def player(self) -> MediaPlayerBackend:
        """The backend under control; exposed for state assertions and feedback."""
        return self._player

    # -- FR-04 ------------------------------------------------------------
    def pause_media(self) -> str:
        """Pause the currently playing item without closing the player (FR-04).

        Returns the operation name that was performed. Raises
        `PlayerOperationError` when nothing is playing or the player rejects the
        request; no other operation is attempted in that case (FR-11).
        """
        if self._player.state != PLAYING:
            raise PlayerOperationError(
                "pause", f"nothing is playing (player is {self._player.state})"
            )

        try:
            self._player.pause()
        except PlayerOperationError:
            raise
        except Exception as exc:  # backend/hardware fault, reported not retried
            raise PlayerOperationError("pause", str(exc)) from exc

        if self._player.state != PAUSED:
            raise PlayerOperationError(
                "pause", f"player did not pause (state is {self._player.state})"
            )
        return "pause"

    # -- Owned by other stories ------------------------------------------
    def play_media(self) -> str:
        """FR-03 — story #9."""
        raise NotImplementedError("FR-03 play_media is story #9")

    def resume_media(self) -> str:
        """FR-05 — story #11."""
        raise NotImplementedError("FR-05 resume_media is story #11")

    def increase_volume(self) -> str:
        """FR-06 — story #16."""
        raise NotImplementedError("FR-06 increase_volume is story #16")

    def decrease_volume(self) -> str:
        """FR-07 — story #16."""
        raise NotImplementedError("FR-07 decrease_volume is story #16")

    def next_media(self) -> str:
        """FR-08 — story #17."""
        raise NotImplementedError("FR-08 next_media is story #17")

    def previous_media(self) -> str:
        """FR-09 — story #18."""
        raise NotImplementedError("FR-09 previous_media is story #18")
