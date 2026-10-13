"""Shared fixtures for the voice-assistant test suite."""

from __future__ import annotations

import pytest

from voice_assistant.controller import MultimediaController
from voice_assistant.player import InMemoryPlayer


class ScriptedSpeechSource:
    """A `SpeechSource` that replays a fixed script of utterances.

    A script entry is either a transcript string or an exception instance, which
    is raised instead of being returned. That is how microphone and
    speech-recognition failures are simulated without hardware.
    """

    def __init__(self, *script: str | BaseException) -> None:
        self.script: list[str | BaseException] = list(script)
        self.listens = 0

    def listen(self) -> str:
        self.listens += 1
        if not self.script:
            raise AssertionError("listen() called more times than the script allows")
        utterance = self.script.pop(0)
        if isinstance(utterance, BaseException):
            raise utterance
        return utterance


@pytest.fixture
def player() -> InMemoryPlayer:
    """A player backend that records every operation it is asked to perform."""
    return InMemoryPlayer()


@pytest.fixture
def playing_player(player: InMemoryPlayer) -> InMemoryPlayer:
    """A player with media already playing, and its operation log cleared."""
    player.play()
    player.calls.clear()
    return player


@pytest.fixture
def controller(player: InMemoryPlayer) -> MultimediaController:
    return MultimediaController(player)
