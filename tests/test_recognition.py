"""FR-02 / TC-01 — recognition of the predefined voice command set (story #8)."""

from __future__ import annotations

import pytest

from voice_assistant.commands import Command, supported_phrases
from voice_assistant.player import InMemoryPlayer
from voice_assistant.recognition import CommandRecognizer, recognize_command

from tests.conftest import ScriptedSpeechSource

EXPECTED_VOCABULARY = {
    "play": Command.PLAY,
    "pause": Command.PAUSE,
    "resume": Command.RESUME,
    "volume up": Command.VOLUME_UP,
    "volume down": Command.VOLUME_DOWN,
    "next": Command.NEXT,
    "previous": Command.PREVIOUS,
}


@pytest.mark.parametrize(("phrase", "expected"), sorted(EXPECTED_VOCABULARY.items()))
def test_recognizes_every_predefined_command(phrase: str, expected: Command) -> None:
    result = recognize_command(phrase)

    assert result.recognized
    assert result.command is expected


def test_vocabulary_is_exactly_the_seven_srs_commands() -> None:
    assert set(supported_phrases()) == set(EXPECTED_VOCABULARY)
    assert len(Command) == 7


@pytest.mark.parametrize(
    "transcript",
    ["Play", "PLAY", " play ", "play.", "Volume   Up!", "volume up?"],
)
def test_transcript_formatting_does_not_prevent_recognition(transcript: str) -> None:
    assert recognize_command(transcript).recognized


@pytest.mark.parametrize(
    "transcript", ["", "   ", "open the playlist", "play something else", "pausa"]
)
def test_unsupported_transcript_returns_an_unrecognized_result(transcript: str) -> None:
    result = recognize_command(transcript)

    assert not result.recognized
    assert result.command is None


def test_none_transcript_is_unrecognized_rather_than_an_error() -> None:
    assert recognize_command(None).command is None


def test_result_keeps_the_normalized_transcript_for_feedback() -> None:
    assert recognize_command("  Volume   DOWN. ").transcript == "volume down"


def test_recognizer_reads_one_utterance_from_the_speech_source() -> None:
    source = ScriptedSpeechSource("Next", "Previous")
    recognizer = CommandRecognizer(source)

    assert recognizer.recognize_once().command is Command.NEXT
    assert source.listens == 1
    assert recognizer.recognize_once().command is Command.PREVIOUS


def test_recognition_never_operates_the_player() -> None:
    """Recognition returns a candidate only; dispatch is the processor's job."""
    player = InMemoryPlayer()
    recognizer = CommandRecognizer(ScriptedSpeechSource("Pause"))

    recognizer.recognize_once()

    assert player.calls == []
    assert player.state == "stopped"
