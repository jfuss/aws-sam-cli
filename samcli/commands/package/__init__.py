"""
CLI command for "package" command
"""

from functools import partial
import click

from samcli.cli.main import pass_context, common_options, aws_creds_options
from samcli.commands._utils.options import get_or_default_template_file_name, _TEMPLATE_OPTION_DEFAULT_VALUE
from samcli.lib.samlib.cloudformation_command import execute_command
from samcli.commands.exceptions import UserException

from .package import PackageCommand


SHORT_HELP = "Package an AWS SAM application. This is an alias for 'aws cloudformation package'."


@click.command("package", short_help=SHORT_HELP, context_settings={"ignore_unknown_options": True})
@click.option('--template-file',
              default=_TEMPLATE_OPTION_DEFAULT_VALUE,
              type=click.Path(),
              callback=partial(get_or_default_template_file_name, include_build=True),
              show_default=False,
              help="The path where your AWS SAM template is located")
@click.option('--s3-bucket',
              required=True,
              help="The name of the S3 bucket where this command uploads the artifacts that "
                   "are referenced in your template.")
@click.option('--s3-prefix', help='A prefix name that the command adds to the artifacts\' name when it uploads them '
                                  'to the S3 bucket. The prefix name is a path name (folder name) for the S3 bucket.')
@click.option('--kms-key-id', help='The ID of an AWS KMS key that the command uses to encrypt artifacts that are at '
                                   'rest in the S3 bucket.')
@click.option('--output-template-file', help="The path to the file where the command writes the output AWS "
                                             "CloudFormation template. If you don't specify a path, the command writes "
                                             "the template to the standard output.")
@click.option('--use-json', help="Indicates whether to use JSON as the format for the output AWS CloudFormation "
                                 "template. YAML is used by default.", is_flag=True, default=False)
@click.option('--force-upload', help='Indicates whether to override existing files in the S3 bucket. Specify this '
                                      'flag to upload artifacts even if they match existing artifacts in the S3 '
                                      'bucket.')
# @click.argument("args", nargs=-1, type=click.UNPROCESSED)
@common_options
@aws_creds_options
@pass_context
def cli(ctx, template_file, s3_bucket, s3_prefix, kms_key_id, output_template_file, use_json, force_upload):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(ctx, template_file, s3_bucket, s3_prefix, kms_key_id, output_template_file, use_json, force_upload)  # pragma: no cover


def do_cli(ctx, template_file, s3_bucket, s3_prefix, kms_key_id, output_template_file, use_json, force_upload):
    PackageCommand()._run_main(template_file, s3_bucket, s3_prefix, kms_key_id, output_template_file, use_json, force_upload, ctx.region)

    # try:
    #     execute_command("package", args, template_file)
    # except OSError as ex:
    #     raise UserException(str(ex))
