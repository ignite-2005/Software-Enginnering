"""FR-04 / TC-03 — Pause pauses current playback only (story #10)."""

from __future__ import annotations

import pytest

from voice_assistant.commands import Command
from voice_assistant.controller import MultimediaController
from voice_assistant.errors import PlayerOperationError
from voice_assistant.player import PAUSED, PLAYING, InMemoryPlayer
from voice_assistant.processor import COMMAND_ROUTES, process_command
from voice_assistant.recognition import recognize_command


def test_pause_pauses_the_currently_playing_media(playing_player: InMemoryPlayer) -> None:
    controller = MultimediaController(playing_player)

    assert controller.pause_media() == "pause"
    assert playing_player.state == PAUSED


def test_pause_leaves_the_player_open_and_resumable(playing_player: InMemoryPlayer) -> None:
    controller = MultimediaController(playing_player)

    controller.pause_media()

    assert playing_player.is_open
    playing_player.resume()
    assert playing_player.state == PLAYING


def test_pause_keeps_the_current_media_item(playing_player: InMemoryPlayer) -> None:
    controller = MultimediaController(playing_player)
    current = playing_player.current_item

    controller.pause_media()

    assert playing_player.current_item == current


def test_pause_invokes_only_the_pause_operation(playing_player: InMemoryPlayer) -> None:
    MultimediaController(playing_player).pause_media()

    assert playing_player.calls == ["pause"]


def test_spoken_pause_command_routes_to_pause(playing_player: InMemoryPlayer) -> None:
    """TC-03 end to end from transcript to player operation."""
    controller = MultimediaController(playing_player)

    operation = process_command(recognize_command("Pause"), controller)

    assert operation == "pause"
    assert playing_player.calls == ["pause"]
    assert playing_player.state == PAUSED


def test_pause_is_routed_to_exactly_one_operation() -> None:
    assert COMMAND_ROUTES[Command.PAUSE] == "pause_media"
    assert sum(1 for route in COMMAND_ROUTES.values() if route == "pause_media") == 1


def test_pause_when_nothing_is_playing_is_reported_and_changes_nothing(
    player: InMemoryPlayer,
) -> None:
    controller = MultimediaController(player)

    with pytest.raises(PlayerOperationError):
        controller.pause_media()

    assert player.calls == []
    assert player.state == "stopped"


def test_pause_is_idempotent_from_the_user_s_point_of_view(
    playing_player: InMemoryPlayer,
) -> None:
    """A second Pause must not resume or otherwise change the operation."""
    controller = MultimediaController(playing_player)
    controller.pause_media()

    with pytest.raises(PlayerOperationError):
        controller.pause_media()

    assert playing_player.state == PAUSED
    assert playing_player.calls == ["pause"]
