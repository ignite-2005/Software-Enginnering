"""Error types and user-facing feedback (SRS FR-11, SAD section 10).

Every failure the system can report is an explicit exception type carrying a
short, understandable message (NFR-02). The rule the whole package obeys:
a failure path reports the problem and dispatches **no** multimedia action.
"""

from __future__ import annotations


class VoiceAssistantError(Exception):
    """Base class for every handled voice-assistant failure.

    `user_message` is the understandable indication shown/spoken to the user;
    `str(error)` keeps the developer-facing detail.
    """

    user_message = "The command could not be completed."

    def __init__(self, detail: str = "", *, user_message: str | None = None) -> None:
        super().__init__(detail or self.user_message)
        if user_message is not None:
            self.user_message = user_message


class MicrophoneUnavailableError(VoiceAssistantError):
    """SAD case 4 — the microphone is missing, busy or failed to open."""

    user_message = "Voice input is unavailable: the microphone could not be used."


class NoSpeechDetectedError(VoiceAssistantError):
    """SAD case 1 — nothing was said; the system waits for another command."""

    user_message = "No speech was detected. Please say a command."


class UnrecognizedSpeechError(VoiceAssistantError):
    """SAD case 2 — audio was captured but could not be transcribed."""

    user_message = "The speech could not be recognized. Please repeat the command."


class UnsupportedCommandError(VoiceAssistantError):
    """SAD case 3 / FR-10 — the transcript is not in the predefined command set."""

    user_message = "That command is not supported."

    def __init__(self, transcript: str = "", **kwargs: object) -> None:
        self.transcript = transcript
        super().__init__(f"unsupported command: {transcript!r}", **kwargs)  # type: ignore[arg-type]


class PlayerOperationError(VoiceAssistantError):
    """SAD case 5 — the media player could not perform the requested action."""

    user_message = "The media player could not complete that operation."

    def __init__(self, operation: str = "", detail: str = "", **kwargs: object) -> None:
        self.operation = operation
        super().__init__(detail or f"player failed during {operation!r}", **kwargs)  # type: ignore[arg-type]


class HardwareInterfaceError(VoiceAssistantError):
    """SAD case 6 — the hardware interface is unavailable or unreliable."""

    user_message = "The hardware interface is unavailable. No action was performed."


def user_feedback(error: BaseException) -> str:
    """Return the understandable indication required by FR-11.

    Unexpected exceptions get a generic message instead of leaking internals.
    """
    if isinstance(error, VoiceAssistantError):
        return error.user_message
    return VoiceAssistantError.user_message
