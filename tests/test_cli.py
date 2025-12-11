from click.testing import CliRunner
from bookrag.cli import cli

def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert 'bookrag' in result.output.lower()
    assert 'build' in result.output.lower()

def test_build_command_requires_args():
    """Test that build command requires source and output args."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build'])

    assert result.exit_code != 0
    assert 'Missing argument' in result.output or 'Usage:' in result.output

def test_build_command_success(tmp_path):
    """Test successful build via CLI."""
    from pathlib import Path

    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    runner = CliRunner()
    result = runner.invoke(cli, ['build', str(source_dir), str(output_file)])

    assert result.exit_code == 0
    assert 'successfully' in result.output.lower()
    assert output_file.exists()

def test_build_command_missing_config(tmp_path):
    """Test error handling for missing config."""
    source_dir = tmp_path / "no-config"
    source_dir.mkdir()
    output_file = tmp_path / "output.html"

    runner = CliRunner()
    result = runner.invoke(cli, ['build', str(source_dir), str(output_file)])

    assert result.exit_code != 0
    assert 'Error' in result.output
