class CliArgsError(Exception):
    """There was an error during CLI arguments parsing."""
    def __init__(self, reason: str):
        print(f"There was an error during CLI arguments parsing. Reason: {reason!r}.")

class ConfigError(Exception):
    """There was an error during configuration parsing."""

    def __init__(self, reason: str):
        print(f"There was an error during configuration parsing. Reason: {reason!r}.")

class CacheError(Exception):
    """There was an error during writing or loading cache."""

    def __init__(self, reason: str):
        print(f"There was an error during writing or loading cache. Reason: {reason!r}.")

class APIError(Exception):
    """There was an error with the API or with API unit conversion."""

    def __init__(self, reason: str):
        print(f"There was an error with the API or with API unit conversion. Reason: {reason!r}.")

class FormatError(Exception):
    """There was an error during formatting."""

    def __init__(self, reason: str):
        print(f"There was an error during formatting. Reason: {reason!r}.")