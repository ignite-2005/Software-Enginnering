"""Orchestration and safe failure handling (SRS FR-11, SAD section 10).

`VoiceAssistant` wires the modules together in the order the security
architecture requires — capture, recognize, validate, dispatch — and turns every
failure into an understandable indication (NFR-02) instead of a crash or a
wrong operation.

The invariant this module exists to guarantee: when any step fails, no
multimedia operation is dispatched.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging

from voice_assistant.commands import Command
from voice_assistant.controller import MultimediaController
from voice_assistant.errors import (
    HardwareInterfaceError,
    MicrophoneUnavailableError,
    NoSpeechDetectedError,
    PlayerOperationError,
    UnrecognizedSpeechError,
    UnsupportedCommandError,
    VoiceAssistantError,
    user_feedback,
)
from voice_assistant.processor import process_command
from voice_assistant.recognition import CommandRecognizer, SpeechSource

logger = logging.getLogger(__name__)


class Status(Enum):
    """Outcome category for a single handled utterance."""

    PERFORMED = "performed"
    NO_SPEECH = "no_speech"
    UNRECOGNIZED_SPEECH = "unrecognized_speech"
    UNSUPPORTED_COMMAND = "unsupported_command"
    MICROPHONE_ERROR = "microphone_error"
    PLAYER_ERROR = "player_error"
    HARDWARE_ERROR = "hardware_error"
    INTERNAL_ERROR = "internal_error"


#: Error type -> status. Order matters: the first matching entry wins.
_STATUS_BY_ERROR: tuple[tuple[type[BaseException], Status], ...] = (
    (NoSpeechDetectedError, Status.NO_SPEECH),
    (UnrecognizedSpeechError, Status.UNRECOGNIZED_SPEECH),
    (UnsupportedCommandError, Status.UNSUPPORTED_COMMAND),
    (MicrophoneUnavailableError, Status.MICROPHONE_ERROR),
    (HardwareInterfaceError, Status.HARDWARE_ERROR),
    (PlayerOperationError, Status.PLAYER_ERROR),
)

#: Failures that stop the listening loop instead of waiting for a new command.
_FATAL_STATUSES = frozenset({Status.MICROPHONE_ERROR, Status.HARDWARE_ERROR})


@dataclass(frozen=True)
class Outcome:
    """What happened for one utterance, including the user-facing message."""

    status: Status
    message: str
    command: Command | None = None
    operation: str | None = None

    @property
    def performed(self) -> bool:
        """True only when a multimedia operation was actually carried out."""
        return self.status is Status.PERFORMED


def _status_for(error: BaseException) -> Status:
    for error_type, status in _STATUS_BY_ERROR:
        if isinstance(error, error_type):
            return status
    return Status.INTERNAL_ERROR


class VoiceAssistant:
    """Handles voice commands end to end, reporting failures safely (FR-11)."""

    def __init__(self, source: SpeechSource, controller: MultimediaController) -> None:
        self._recognizer = CommandRecognizer(source)
        self._controller = controller

    def handle_once(self) -> Outcome:
        """Capture, recognize and dispatch one command; never raise.

        Returns an `Outcome`. On any failure the outcome carries the error
        status and message, `operation is None`, and no controller method has
        been called.
        """
        try:
            result = self._recognizer.recognize_once()
        except VoiceAssistantError as exc:
            return self._failure(exc)
        except Exception as exc:  # unexpected capture fault
            logger.exception("unexpected error while capturing voice input")
            return self._failure(exc)

        try:
            operation = process_command(result, self._controller)
        except VoiceAssistantError as exc:
            return self._failure(exc, command=result.command)
        except NotImplementedError as exc:
            # A command whose operation is not built yet must not fall through
            # to a different operation.
            logger.warning("operation not implemented: %s", exc)
            return Outcome(
                status=Status.PLAYER_ERROR,
                message="That operation is not available yet.",
                command=result.command,
            )
        except Exception as exc:  # unexpected controller/player fault
            logger.exception("unexpected error while performing the operation")
            return self._failure(exc, command=result.command)

        logger.info("performed %s for command %s", operation, result.command)
        return Outcome(
            status=Status.PERFORMED,
            message=f"Performed {operation}.",
            command=result.command,
            operation=operation,
        )

    def run(self, max_commands: int | None = None) -> list[Outcome]:
        """Handle utterances until `max_commands` or an unrecoverable failure.

        No speech, unrecognized speech, unsupported commands and player errors
        are reported and the system waits for the next command (SAD case 1).
        Microphone and hardware failures end the loop, since further listening
        would be unreliable (SAD cases 4 and 6).
        """
        outcomes: list[Outcome] = []
        while max_commands is None or len(outcomes) < max_commands:
            outcome = self.handle_once()
            outcomes.append(outcome)
            if outcome.status in _FATAL_STATUSES:
                break
        return outcomes

    def _failure(self, error: BaseException, command: Command | None = None) -> Outcome:
        status = _status_for(error)
        logger.warning("%s: %s", status.value, error)
        return Outcome(status=status, message=user_feedback(error), command=command)
