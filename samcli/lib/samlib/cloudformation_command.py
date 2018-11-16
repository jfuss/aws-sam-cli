"""
Utility to call cloudformation command with args
"""

import logging
import platform
import subprocess
import sys

LOG = logging.getLogger(__name__)


def execute_command(command, args, template_file=None):
    LOG.debug("%s command is called", command)

    aws_cmd = 'aws' if platform.system().lower() != 'windows' else 'aws.cmd'
    command_to_execute = [aws_cmd, 'cloudformation', command]

    if template_file:
        command_to_execute.extend(["--template-file", template_file])

    command_to_execute.extend(list(args))

    try:
        subprocess.check_call(command_to_execute)
        LOG.debug("%s command successful", command)
    except subprocess.CalledProcessError as e:
        # Underlying aws command will print the exception to the user
        LOG.debug("Exception: %s", e)
        sys.exit(e.returncode)
