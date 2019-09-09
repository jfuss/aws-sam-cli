from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('cookiecutter') + ['jinja2_time']
