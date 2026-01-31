from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass(frozen=True, slots=True)
class CliOptions:
    """Strongly-typed container for command-line options.

    This model is the single source of truth for values parsed by the CLI layer.

    Fields:
    - city_name: Optional name of the city to query; if None, the app may fall back to IP lookup.
    - country_code: Optional ISO 3166-1 alpha-2 country code to disambiguate the city.
    - history_index: If provided, select a city from history by 1-based index; None means not requested.
    - bypass_cache: If True, skip reading from cache and force fresh API calls.
    - reinitialize_config: If True, recreate the configuration directory and files.
    - show_version: If True, print the program version and exit early.
    - verbose: If True, enable verbose logging.
    - quiet: If True, minimize non-essential output (conflicts with verbose; resolve in CLI).
    - temperature_unit_override: Optional override for temperature unit (e.g., "°C", "°F", "°K").
    - speed_unit_override: Optional override for wind speed unit (e.g., "km/h", "mph", "m/s", "knots").
    - precipitation_unit_override: Optional override for precipitation unit (e.g., "mm", "inch").
    - date_format_override: Optional override for date format (e.g., "YYYY-MM-DD").
    - time_format_override: Optional override for time format (e.g., "12", "24").
    """

    city_name: Optional[str]
    country_code: Optional[str]
    history_index: Optional[int]

    bypass_cache: bool
    reinitialize_config: bool
    show_version: bool

    verbose: bool
    quiet: bool
    refresh: bool

    temperature_unit_override: Optional[str]
    speed_unit_override: Optional[str]
    precipitation_unit_override: Optional[str]
    date_format_override: Optional[str]
    time_format_override: Optional[str]

@dataclass(frozen=True, slots=True)
class ConfigSettings:
    """Immutable snapshot of user configuration settings.

    Mirrors values loaded from the configuration store. Prefer constructing this
    from the config layer and passing it around rather than querying config
    globals in different places.
    """

    # Location
    city_name: Optional[str]
    country_code: Optional[str]

    # Units
    temperature_unit: str  # e.g., "°C", "°F", "°K"
    speed_unit: str        # e.g., "km/h", "mph", "m/s", "knots"
    precipitation_unit: str  # e.g., "mm", "inch"

    # Formats
    date_format: str       # e.g., "YYYY-MM-DD"
    time_format: int       # 12 or 24

    # Visibility toggles
    show_city: bool
    show_weather: bool
    show_temperature: bool
    show_apparent_temperature: bool
    show_max_and_min_temperature: bool
    show_wind_speed: bool
    show_wind_direction: bool
    show_sunrise: bool
    show_sunset: bool
    show_date: bool
    show_time: bool
    show_uv_index: bool
    show_humidity: bool
    show_precipitation: bool
    show_surface_pressure: bool
    show_air_quality: bool

    # Output
    use_emoji: bool
    show_ascii_art: bool

    # Misc
    cache_ttl: int
    max_cache_file_count: int


@dataclass(frozen=True, slots=True)
class Coordinates:
    """Geographic coordinates rounded to 2 decimal places as used by the API."""

    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class LocalDateTime:
    """Localized date/time information for the target location.

    All fields are pre-formatted strings suitable for display. Computation of
    these values (including time zone/offset handling) should happen elsewhere
    before constructing this model.
    """

    local_time: str      # e.g., "14:23:01" or "02:23:01 PM" depending on settings
    local_date: str      # e.g., "2025-02-03" depending on settings
    local_sunrise: str   # e.g., "14:23:01" or "02:23:01 PM" depending on settings
    local_sunset: str    # e.g., "14:23:01" or "02:23:01 PM" depending on settings


@dataclass(frozen=True, slots=True)
class Weather:
    """Unified weather model containing current and daily highlights.

    This combines fields that might otherwise be split across separate models
    (e.g., current vs. daily) so the rest of the application can consume a single
    cohesive object. All values are raw numeric/textual values without units;
    presentation/formatting is handled elsewhere.

    Required fields are based on the Open‑Meteo responses you already use.
    """

    # Context
    city_name: str
    coordinates: Coordinates
    utc_offset_seconds: int

    # Current conditions
    weather_code: int
    is_day: bool
    temperature: float
    apparent_temperature: float
    wind_speed: float
    wind_direction: int
    humidity_percent: int
    precipitation: float
    surface_pressure_hpa: float
    uv_index: float
    air_quality_index: Optional[int]

    # Daily highlights (for the current day)
    sunrise_local: str  # "HH:MM"
    sunset_local: str   # "HH:MM"
    temperature_min: float
    temperature_max: float


class TemperatureUnit(str, Enum):
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "°K"


class SpeedUnit(str, Enum):
    KILOMETERS_PER_HOUR = "km/h"
    MILES_PER_HOUR = "mph"
    METERS_PER_SECOND = "m/s"
    KNOTS = "knots"


class PrecipitationUnit(str, Enum):
    MILLIMETER = "mm"
    INCH = "inch"


class TimeFormat(int, Enum):
    TWELVE = 12
    TWENTY_FOUR = 24


class DateFormat(str, Enum):
    MM_DD_YYYY = "MM/DD/YYYY"
    DD_MM_YYYY = "DD/MM/YYYY"
    YYYY_MM_DD_SLASH = "YYYY/MM/DD"
    YYYY_MM_DD_DASH = "YYYY-MM-DD"
    DD_DOT_MM_DOT_YYYY = "DD.MM.YYYY"
