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

    # Validate required AI fields (Ollama-only in v1)
    if not config.get("model"):
        raise ValueError("Missing required field: model")
    if not config.get("embedding_model"):
        raise ValueError("Missing required field: embedding_model")
    if not config.get("system_prompt"):
        raise ValueError("Missing required field: system_prompt")

    # Validate chapters structure
    for i, chapter in enumerate(config["chapters"]):
        if not chapter.get("id"):
            raise ValueError(f"Chapter {i}: missing required field 'id'")
        if not chapter.get("title"):
            raise ValueError(f"Chapter {i}: missing required field 'title'")
        if not chapter.get("folder"):
            raise ValueError(f"Chapter {i}: missing required field 'folder'")

    return config
