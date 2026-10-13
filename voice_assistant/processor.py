"""Command processor (SAD section 2.5, SRS FR-02/FR-10, SR-01/SR-02).

`process_command` is the single dispatch point between a recognized command and
the multimedia controller. A command reaches a controller method only if it is a
member of the predefined allow-list, so unsupported input cannot cause any
multimedia operation.
"""

from __future__ import annotations

from voice_assistant.commands import Command, is_supported
from voice_assistant.errors import UnsupportedCommandError
from voice_assistant.controller import MultimediaController
from voice_assistant.recognition import RecognitionResult

#: Command -> controller method name. The mapping is one-to-one by design
#: (NFR-03): one recognized command can only ever reach one operation.
COMMAND_ROUTES: dict[Command, str] = {
    Command.PLAY: "play_media",
    Command.PAUSE: "pause_media",
    Command.RESUME: "resume_media",
    Command.VOLUME_UP: "increase_volume",
    Command.VOLUME_DOWN: "decrease_volume",
    Command.NEXT: "next_media",
    Command.PREVIOUS: "previous_media",
}


def process_command(
    candidate: Command | RecognitionResult | None,
    controller: MultimediaController,
) -> str:
    """Validate `candidate` and dispatch its one matching operation.

    Accepts a `Command` or a `RecognitionResult`. Returns the name of the
    operation performed. Raises `UnsupportedCommandError` for an unrecognized or
    non-allow-listed candidate, without calling the controller at all.

    Note: the fuller allow-list validation layer is story #12; this function
    enforces the SR-01 invariant that dispatch requires a supported command.
    """
    transcript = ""
    command: Command | None
    if isinstance(candidate, RecognitionResult):
        transcript = candidate.transcript
        command = candidate.command
    else:
        command = candidate

    if not is_supported(command) or command not in COMMAND_ROUTES:
        raise UnsupportedCommandError(transcript or str(command))

    return getattr(controller, COMMAND_ROUTES[command])()
