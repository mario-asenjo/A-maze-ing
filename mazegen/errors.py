"""
Custom exceptions for the mazegen package.

The mazegen package should raise clear, domain-specific exceptions so the
entrypoint can handle them cleanly (print messages, exit codes, etc.).
"""


class MazeError(Exception):
    """Base class for all maze-related errors."""


class MazeConfigError(MazeError):
    """Raised when configuration parameters are invalid."""


class MazeGenerationError(MazeError):
    """Raised when a maze cannot be generated with the given constraints."""


class MazeUnsolvableError(MazeError):
    """Raised when the solver cannot find a path between entry and exit."""
