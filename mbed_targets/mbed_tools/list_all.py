"""Implementation of `list_all` cli command."""
import click

from mbed_targets import MbedTargets


@click.command(help="Lists all available targets.")
def list_all():
    """Output all board types."""
    output = "\n".join(target.board_type for target in MbedTargets())
    click.echo(output)
