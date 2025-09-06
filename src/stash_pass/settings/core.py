import json
import time
from pathlib import Path

APP_DIR = Path.home() / ".stash_pass"
SETTINGS_FILE = APP_DIR / "settings.json"
STATE_FILE = APP_DIR / "state.json"

# TODO: Implement persistent caching of unlock state
# For now, we just track in-memory (will ask for password each time)
DEFAULT_SETTINGS = {"password_timeout": 300}  # 5 minutes


def load_settings() -> dict:
    """
    Load the settings from the settings file. If the file does not exist, 
    create it with default settings.

    Returns:
        dict: The settings as a dictionary.
    """
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)


def save_settings(settings: dict) -> None:
    """
    Save the settings dictionary to the settings file as JSON.

    Args:
        settings (dict): The settings to save.
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_state() -> dict:
    """
    Load the state from the state file. Returns an empty dict if the file does not exist.

    Returns:
        dict: The state as a dictionary.
    """
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """
    Save the state dictionary to the state file as JSON.

    Args:
        state (dict): The state to save.
    """
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
