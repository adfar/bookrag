import pytest
from pathlib import Path
from bookrag.config import load_config

def test_load_valid_config():
    """Test loading a valid config file."""
    config_path = Path(__file__).parent / "fixtures" / "valid-config.yaml"
    config = load_config(config_path)

    assert config["title"] == "Test Book"
    assert config["author"] == "Test Author"
    assert len(config["chapters"]) == 2
    assert config["chapters"][0]["id"] == "intro"
    assert config["chapters"][0]["title"] == "Introduction"
    assert config["chapters"][0]["folder"] == "01-intro"

def test_load_minimal_config():
    """Test loading config without optional AI settings."""
    config_path = Path(__file__).parent / "fixtures" / "minimal-config.yaml"
    config = load_config(config_path)

    assert config["title"] == "Minimal Book"
    assert "ai" not in config
    assert len(config["chapters"]) == 1

def test_missing_required_fields():
    """Test that missing title raises error."""
    config_path = Path(__file__).parent / "fixtures" / "invalid-config.yaml"
    with pytest.raises(ValueError, match="Missing required field: title"):
        load_config(config_path)
