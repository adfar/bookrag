import pytest
from pathlib import Path
from bookrag.config import load_config

def test_load_valid_config():
    """Test loading a valid config file."""
    config_path = Path(__file__).parent / "fixtures" / "valid-config.yaml"
    config = load_config(config_path)

    assert config["title"] == "Test Book"
    assert config["author"] == "Test Author"
    assert config["model"] == "llama3.2"
    assert config["embedding_model"] == "nomic-embed-text"
    assert config["system_prompt"] == "You are a helpful tutor."
    assert len(config["chapters"]) == 2
    assert config["chapters"][0]["id"] == "intro"
    assert config["chapters"][0]["title"] == "Introduction"
    assert config["chapters"][0]["folder"] == "01-intro"

def test_load_minimal_config():
    """Test loading config with minimal required fields."""
    config_path = Path(__file__).parent / "fixtures" / "minimal-config.yaml"
    config = load_config(config_path)

    assert config["title"] == "Minimal Book"
    assert config["model"] == "llama3.2"
    assert config["embedding_model"] == "nomic-embed-text"
    assert len(config["chapters"]) == 1

def test_missing_required_fields():
    """Test that missing title raises error."""
    config_path = Path(__file__).parent / "fixtures" / "invalid-config.yaml"
    with pytest.raises(ValueError, match="Missing required field: title"):
        load_config(config_path)

def test_missing_model_field(tmp_path):
    """Test that missing model raises error."""
    config_content = """title: "Test"
embedding_model: "nomic-embed-text"
system_prompt: "Test"
chapters:
  - id: "intro"
    title: "Intro"
    folder: "01-intro"
"""
    config_path = tmp_path / "bookrag.yaml"
    config_path.write_text(config_content)

    with pytest.raises(ValueError, match="Missing required field: model"):
        load_config(config_path)
