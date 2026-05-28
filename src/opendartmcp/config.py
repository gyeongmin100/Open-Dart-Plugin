import json
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_ENV_VAR = "OPENDARTMCP_CONFIG_FILE"
API_KEY_ENV_VAR = "DART_API_KEY"
API_KEY_FIELD = "dart_api_key"


@dataclass(frozen=True)
class ResolvedApiKey:
    api_key: str
    source: str
    config_path: Path | None = None


def get_config_path() -> Path:
    override = os.environ.get(CONFIG_ENV_VAR)
    if override:
        return Path(override).expanduser()

    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base / "opendartmcp" / "config.json"


def load_config() -> dict[str, Any]:
    path = get_config_path()
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid config file: {path}")
    return data


def save_config(config: dict[str, Any]) -> None:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)
        file.write("\n")

    if os.name != "nt":
        try:
            path.chmod(0o600)
        except OSError:
            pass


def save_api_key(api_key: str) -> None:
    config = load_config()
    config[API_KEY_FIELD] = api_key.strip()
    save_config(config)


def clear_api_key() -> bool:
    config = load_config()
    if API_KEY_FIELD not in config:
        return False

    del config[API_KEY_FIELD]
    save_config(config)
    return True


def resolve_api_key() -> ResolvedApiKey | None:
    env_value = os.environ.get(API_KEY_ENV_VAR, "").strip()
    if env_value:
        return ResolvedApiKey(api_key=env_value, source="environment")

    config = load_config()
    config_value = str(config.get(API_KEY_FIELD, "")).strip()
    if config_value:
        return ResolvedApiKey(
            api_key=config_value,
            source="user config",
            config_path=get_config_path(),
        )

    return None


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}********{api_key[-4:]}"
