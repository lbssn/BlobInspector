import subprocess

packages = ['pyside6', 'scikit-image', 'numpy', 'matplotlib', 'scipy']

for package in packages:
    subprocess.check_call(['pip', 'install', package])
