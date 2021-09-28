
from pathlib import Path


def default_homedir():
    """ Return default home directory, creating it if necessary

    Returns:
        pathlib.Path : Path to home directory
    """
    homedir = Path.home() / ('.telliot')
    homedir = homedir.resolve().absolute()
    if not homedir.is_dir():
        homedir.mkdir()

    return homedir
