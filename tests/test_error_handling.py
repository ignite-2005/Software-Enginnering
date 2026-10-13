"""FR-11 — voice, hardware and player failures are handled safely (story #13)."""

from __future__ import annotations

import pytest

from voice_assistant.assistant import Status, VoiceAssistant
from voice_assistant.commands import Command
from voice_assistant.controller import MultimediaController
from voice_assistant.errors import (
    HardwareInterfaceError,
    MicrophoneUnavailableError,
    NoSpeechDetectedError,
    PlayerOperationError,
    UnrecognizedSpeechError,
    UnsupportedCommandError,
    user_feedback,
)
from voice_assistant.player import PLAYING, InMemoryPlayer
from voice_assistant.processor import process_command
from voice_assistant.recognition import recognize_command

from tests.conftest import ScriptedSpeechSource


def build(player: InMemoryPlayer, *script: str | BaseException) -> VoiceAssistant:
    return VoiceAssistant(ScriptedSpeechSource(*script), MultimediaController(player))


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (MicrophoneUnavailableError(), Status.MICROPHONE_ERROR),
        (NoSpeechDetectedError(), Status.NO_SPEECH),
        (UnrecognizedSpeechError(), Status.UNRECOGNIZED_SPEECH),
        (HardwareInterfaceError(), Status.HARDWARE_ERROR),
    ],
)
def test_capture_failures_are_reported_without_any_media_action(
    playing_player: InMemoryPlayer, error: Exception, expected_status: Status
) -> None:
    outcome = build(playing_player, error).handle_once()

    assert outcome.status is expected_status
    assert not outcome.performed
    assert outcome.operation is None
    assert outcome.message
    assert playing_player.calls == []
    assert playing_player.state == PLAYING


def test_unsupported_command_performs_no_operation(playing_player: InMemoryPlayer) -> None:
    outcome = build(playing_player, "shuffle everything").handle_once()

    assert outcome.status is Status.UNSUPPORTED_COMMAND
    assert playing_player.calls == []
    assert playing_player.state == PLAYING


def test_processor_rejects_an_unrecognized_candidate_before_dispatch(
    playing_player: InMemoryPlayer,
) -> None:
    controller = MultimediaController(playing_player)

    with pytest.raises(UnsupportedCommandError):
        process_command(recognize_command("do something"), controller)

    assert playing_player.calls == []


def test_player_failure_is_reported_as_a_player_error(player: InMemoryPlayer) -> None:
    player.fail_on = {"pause"}
    player.play()
    player.calls.clear()

    outcome = build(player, "Pause").handle_once()

    assert outcome.status is Status.PLAYER_ERROR
    assert not outcome.performed
    assert outcome.command is Command.PAUSE
    assert player.calls == ["pause"]  # the failing operation only, nothing else


def test_an_unbuilt_operation_does_not_fall_through_to_another_operation(
    playing_player: InMemoryPlayer,
) -> None:
    """Commands whose controller method is still a story stub stay inert."""
    outcome = build(playing_player, "Resume").handle_once()

    assert not outcome.performed
    assert playing_player.calls == []
    assert playing_player.state == PLAYING


def test_unexpected_exceptions_do_not_escape_or_dispatch(
    playing_player: InMemoryPlayer,
) -> None:
    outcome = build(playing_player, RuntimeError("driver crash")).handle_once()

    assert outcome.status is Status.INTERNAL_ERROR
    assert outcome.message == user_feedback(RuntimeError("driver crash"))
    assert playing_player.calls == []


def test_recoverable_failures_let_the_next_command_be_handled(
    playing_player: InMemoryPlayer,
) -> None:
    assistant = build(playing_player, NoSpeechDetectedError(), "nonsense", "Pause")

    statuses = [outcome.status for outcome in assistant.run(3)]

    assert statuses == [
        Status.NO_SPEECH,
        Status.UNSUPPORTED_COMMAND,
        Status.PERFORMED,
    ]
    assert playing_player.calls == ["pause"]


def test_microphone_failure_stops_the_listening_loop(playing_player: InMemoryPlayer) -> None:
    source = ScriptedSpeechSource(MicrophoneUnavailableError(), "Pause")
    assistant = VoiceAssistant(source, MultimediaController(playing_player))

    outcomes = assistant.run(5)

    assert [outcome.status for outcome in outcomes] == [Status.MICROPHONE_ERROR]
    assert source.listens == 1
    assert playing_player.calls == []


@pytest.mark.parametrize(
    "error",
    [
        MicrophoneUnavailableError(),
        NoSpeechDetectedError(),
        UnrecognizedSpeechError(),
        UnsupportedCommandError("whatever"),
        PlayerOperationError("pause"),
        HardwareInterfaceError(),
    ],
)
def test_every_handled_error_has_an_understandable_message(error: Exception) -> None:
    message = user_feedback(error)

    assert message and message[0].isupper() and message.endswith(".")
