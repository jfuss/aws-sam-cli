from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('aws_lambda_builders.workflows')
