"""Configuration file parsing and validation."""
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate configuration file.

    Args:
        config_path: Path to bookrag.yaml config file

    Returns:
        Validated config dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required fields are missing or invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if not config.get("title"):
        raise ValueError("Missing required field: title")

    if not config.get("chapters"):
        raise ValueError("Missing required field: chapters")

    # Validate chapters structure
    for i, chapter in enumerate(config["chapters"]):
        if not chapter.get("id"):
            raise ValueError(f"Chapter {i}: missing required field 'id'")
        if not chapter.get("title"):
            raise ValueError(f"Chapter {i}: missing required field 'title'")
        if not chapter.get("folder"):
            raise ValueError(f"Chapter {i}: missing required field 'folder'")

    # Validate AI config if present
    if "ai" in config:
        ai = config["ai"]
        if not ai.get("backend"):
            raise ValueError("AI config missing required field: backend")

        supported_backends = ["anthropic", "openai", "ollama"]
        if ai["backend"] not in supported_backends:
            raise ValueError(
                f"Unsupported AI backend: {ai['backend']}. "
                f"Supported: {', '.join(supported_backends)}"
            )

    return config
