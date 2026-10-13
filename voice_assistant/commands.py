"""Predefined multimedia command vocabulary (SRS FR-02).

This module owns the *vocabulary* only: the fixed set of commands the system
supports and the spoken phrases that map onto it. It performs no media
operations, so it can be tested on its own (Test Plan TC-01).
"""

from __future__ import annotations

from enum import Enum
import re
import unicodedata


class Command(Enum):
    """The predefined multimedia commands named in SRS FR-02."""

    PLAY = "play"
    PAUSE = "pause"
    RESUME = "resume"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    NEXT = "next"
    PREVIOUS = "previous"


#: The command allow-list referenced by SR-01/SR-02 and FR-10.
SUPPORTED_COMMANDS: frozenset[Command] = frozenset(Command)

#: Spoken phrase -> command. Keys must already be normalized (see `normalize`).
COMMAND_PHRASES: dict[str, Command] = {
    "play": Command.PLAY,
    "pause": Command.PAUSE,
    "resume": Command.RESUME,
    "volume up": Command.VOLUME_UP,
    "volume down": Command.VOLUME_DOWN,
    "next": Command.NEXT,
    "previous": Command.PREVIOUS,
}

_PUNCTUATION = re.compile(r"[^\w\s]+", re.UNICODE)
_WHITESPACE = re.compile(r"\s+", re.UNICODE)


def normalize(transcript: str) -> str:
    """Return `transcript` in the canonical form used to look up a command.

    Speech-to-text output varies in case, punctuation and spacing, so the
    comparison is done on a normalized string rather than the raw transcript.
    """
    text = unicodedata.normalize("NFKC", transcript)
    text = _PUNCTUATION.sub(" ", text.lower())
    return _WHITESPACE.sub(" ", text).strip()


def lookup(transcript: str) -> Command | None:
    """Map a spoken transcript to a `Command`, or `None` when unsupported."""
    return COMMAND_PHRASES.get(normalize(transcript))


def is_supported(command: Command | None) -> bool:
    """True only for members of the predefined command set (SR-01)."""
    return command in SUPPORTED_COMMANDS


def supported_phrases() -> tuple[str, ...]:
    """The spoken phrases a user may say, for help text and feedback (NFR-02)."""
    return tuple(sorted(COMMAND_PHRASES))
