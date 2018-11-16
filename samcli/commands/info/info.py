"""
CLI Command for Validating a SAM Template
"""
import json
import sys

import click
import docker

from samcli.cli.main import pass_context, common_options
from samcli import __version__ as version


@click.command("info",
               short_help="AWS SAM CLI system info")
@common_options
@pass_context
def cli(ctx):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(ctx)  # pragma: no cover


def do_cli(ctx):
    """
    Implementation of the ``cli`` method, just separated out for unit testing purposes
    """
    click.echo(json.dumps(
        {
            'Version': version,
            'PythonVerson': sys.version,
            'OS Platform': sys.platform,
            'Docker Version': docker.from_env().version()
        },
        indent=4))
