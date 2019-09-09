from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('samcli')

datas = collect_data_files('samcli') + [('samcli/local/init/templates/cookiecutter-aws-sam-hello-nodejs', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-nodejs'), 
     ('samcli/local/init/templates/cookiecutter-aws-sam-hello-python', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-python'),
     ('samcli/local/init/templates/cookiecutter-aws-sam-hello-java-gradle', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-java-gradle'),
     ('samcli/local/init/templates/cookiecutter-aws-sam-hello-java-maven', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-java-maven'),
     ('samcli/local/init/templates/cookiecutter-aws-sam-hello-ruby', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-ruby'),
     ('samcli/local/init/templates/cookiecutter-aws-sam-hello-golang', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-golang'),
     ('samcli/local/init/templates/cookiecutter-aws-sam-hello-dotnet', 'samcli/local/init/templates/cookiecutter-aws-sam-hello-dotnet')]
