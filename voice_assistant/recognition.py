"""Voice command recognition (SRS FR-02, Test Plan TC-01).

The recognition module turns captured speech into a *command candidate*. It
never touches the media player: it returns data that the command processor
validates and dispatches (SAD security flow
`Voice Input -> Recognition -> Validation -> Multimedia Action`).

Audio capture itself (FR-01) lives behind the `SpeechSource` interface so the
microphone implementation can be developed and swapped independently (NFR-05).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from voice_assistant.commands import Command, lookup, normalize


@runtime_checkable
class SpeechSource(Protocol):
    """A source of transcribed speech, e.g. a microphone + STT engine (FR-01).

    `listen()` returns the transcript of a single utterance. Implementations
    raise `MicrophoneUnavailableError`, `NoSpeechDetectedError` or
    `UnrecognizedSpeechError` from `voice_assistant.errors` on failure so that
    the error paths required by FR-11 stay uniform.
    """

    def listen(self) -> str:  # pragma: no cover - interface declaration
        ...


@dataclass(frozen=True)
class RecognitionResult:
    """Outcome of recognizing one utterance.

    `command` is the recognized candidate, or `None` when the transcript is not
    part of the predefined vocabulary. `transcript` keeps the normalized text so
    that feedback and logs can quote what the system heard.
    """

    transcript: str
    command: Command | None

    @property
    def recognized(self) -> bool:
        """True when the utterance matched a predefined command."""
        return self.command is not None


def recognize_command(transcript: str | None) -> RecognitionResult:
    """Recognize `transcript` as one of the predefined commands (FR-02).

    Returns a `RecognitionResult`; an unsupported or empty transcript yields a
    result with `command is None` rather than raising, so the caller decides how
    to report it. No multimedia operation is performed here.
    """
    text = normalize(transcript or "")
    return RecognitionResult(transcript=text, command=lookup(text))


class CommandRecognizer:
    """Reads one utterance from a `SpeechSource` and recognizes it (FR-01/FR-02)."""

    def __init__(self, source: SpeechSource) -> None:
        self._source = source

    def recognize_once(self) -> RecognitionResult:
        """Capture a single utterance and return its recognition result.

        Capture failures propagate as `voice_assistant.errors` exceptions; they
        are handled by the orchestration layer, not here.
        """
        return recognize_command(self._source.listen())
