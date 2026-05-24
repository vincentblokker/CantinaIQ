"""CantinaIQ Typer CLI entrypoint."""

import typer

app = typer.Typer(no_args_is_help=True, help="CantinaIQ pipeline CLI.")


@app.callback()
def main() -> None:
    """CantinaIQ pipeline CLI — Slurpini Partner Intelligence Engine."""


@app.command()
def version() -> None:
    """Print the package version."""
    from cantinaiq import __version__

    typer.echo(__version__)
