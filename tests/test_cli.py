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
