"""Error hierarchy for the config object system project."""


class ConfigError(Exception):
    """Base class for project-specific configuration errors."""


class ValidationError(ConfigError):
    """Raised when a config field violates this project's invariants."""

