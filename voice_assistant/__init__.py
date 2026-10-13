"""Hardware-Based Voice Assistant for Multimedia Controls — Team H6.

The package follows the modular architecture in the Software Architecture &
Design Specification (NFR-05): voice recognition, command processing and
multimedia control are separate modules with their own public interfaces.
"""

from voice_assistant.commands import Command, SUPPORTED_COMMANDS

__all__ = ["Command", "SUPPORTED_COMMANDS"]
