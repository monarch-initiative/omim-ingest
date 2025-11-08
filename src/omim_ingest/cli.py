"""Command line interface for omim-ingest."""
import logging

from pathlib import Path

from kghub_downloader.download_utils import download_from_yaml
from kghub_downloader.model import DownloadOptions

from koza.runner import KozaRunner
from koza.model.formats import OutputFormat
import typer

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.callback()
def callback(version: bool = typer.Option(False, "--version", is_eager=True),
):
    """omim-ingest CLI."""
    if version:
        from omim_ingest import __version__
        typer.echo(f"omim-ingest version: {__version__}")
        raise typer.Exit()


@app.command()
def download(force: bool = typer.Option(False, help="Force download of data, even if it exists")):
    """Download data for omim-ingest."""
    typer.echo("Downloading data for omim-ingest...")
    download_config = Path(__file__).parent / "download.yaml"
    download_options = DownloadOptions()
    download_options.ignore_cache = True
    download_from_yaml(yaml_file=download_config, output_dir=".", download_options=download_options)


@app.command()
def transform(
    output_dir: str = typer.Option("output", help="Output directory for transformed data"),
    row_limit: int = typer.Option(0, help="Number of rows to process (0 = all)"),
    output_format: OutputFormat = typer.Option(OutputFormat.tsv, help="Output format"),
    show_progress: bool = typer.Option(False, help="Display progress bar"),
):
    """Run the Koza transform for omim-ingest."""
    typer.echo("Transforming data for omim-ingest...")
    transform_config = Path(__file__).parent / "transform.yaml"

    config, runner = KozaRunner.from_config_file(
        str(transform_config),
        output_dir=output_dir,
        output_format=output_format,
        row_limit=row_limit,
        show_progress=show_progress,
    )
    runner.run()


if __name__ == "__main__":
    app()
