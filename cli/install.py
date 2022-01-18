from .run import get, run


def install(*packages, installer_command=None):
    import platform
    import warnings
    
    packages = parse_args(packages)
    
    if platform.system() == 'Linux':
        command = installer_command or get_install_command()
        for p in packages:
            cli.run(installer_command, p, root=True, check=False)
    else:        
        message = f'Required packages cannot be installed automatically because OS is not Linux'
        warnings.warn(message)


def get_install_command():
    commands = {
        'apt': 'apt install -y',
        'pacman': 'pacman -S --noconfirm'
    }
    for manager, command in commands.items():
        if cli.get('which', manager, check=False):
            return command
