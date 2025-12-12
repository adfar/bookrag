"""Command-line interface for bookrag."""
import click
import subprocess
from pathlib import Path
from bookrag.builder import build_book

@click.group()
@click.version_option()
def cli():
    """Bookrag - Convert markdown manuscripts into interactive web books."""
    pass

@cli.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
def build(source_dir: Path, output_file: Path):
    """Build a web book from markdown source.

    SOURCE_DIR: Directory containing bookrag.yaml and chapter folders
    OUTPUT_FILE: Path for the generated HTML file
    """
    try:
        build_book(source_dir, output_file)
        click.echo(f"✓ Book built successfully: {output_file}")
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()
