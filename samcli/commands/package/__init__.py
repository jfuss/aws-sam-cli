"""
CLI command for "package" command
"""

import click

from samcli.cli.main import pass_context, common_options
from samcli.lib.samlib.cloudformation_command import execute_command

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


SHORT_HELP = "Package an AWS SAM application. This is an alias for 'aws cloudformation package'."


@click.command("package", short_help=SHORT_HELP, context_settings={"ignore_unknown_options": True})
@click.option('--template-file',
                        default="template.[yaml|yml]",
                        type=click.Path(),
                        show_default=True,
                        help="AWS SAM template file")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@common_options
@pass_context
def cli(ctx, args, template_file):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(args, template_file)  # pragma: no cover


def do_cli(args, template_file):

    template = get_or_default_template_file_name(ctx=None, param=None, provided_value=template_file)

    execute_command("package", args, template_file=template)


_TEMPLATE_OPTION_DEFAULT_VALUE = "template.[yaml|yml]"


def get_or_default_template_file_name(ctx, param, provided_value, include_build=True):
    """
    Default value for the template file name option is more complex than what Click can handle.
    This method either returns user provided file name or one of the two default options (template.yaml/template.yml)
    depending on the file that exists
     :param ctx: Click Context
    :param param: Param name
    :param provided_value: Value provided by Click. It could either be the default value or provided by user.
    :return: Actual value to be used in the CLI
    """
    search_paths = [
        Path("template.yaml"),
        Path("template.yml"),
    ]
    if include_build:
        search_paths.insert(0, Path(".sam", "build", "template.yaml"))
    if str(provided_value) == _TEMPLATE_OPTION_DEFAULT_VALUE:
        # Default value was used. Value can either be template.yaml or template.yml. Decide based on which file exists
        # .yml is the default, even if it does not exist.
        provided_value = Path("template.yml")
        for option in search_paths:
            if option.exists():
                provided_value = option
                break

    result = provided_value.resolve()
    return result
