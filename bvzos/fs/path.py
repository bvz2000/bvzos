import os


# ----------------------------------------------------------------------------------------------------------------------
def unix_path_to_os_path(path):
    """
    Given a path string (in a unix-like path format), converts it into an OS appropriate path format. Note, it does not
    check to see whether this path exists. It merely re-formats the string into the OS specific format.

    :param path:
        The path string to be reformatted.

    :return:
        An OS appropriate path string.
    """

    assert type(path) is str

    return os.path.join(*path.lstrip("/").split("/"))


# ----------------------------------------------------------------------------------------------------------------------
# TODO: Make windows friendly
def resolve_symlinks(symlinks_p):
    """
    Given a list of symbolic link files, return a list of their real paths. Only works on Unix-like systems for the
    moment.

    :param symlinks_p:
        A symlink or list of symlinks. If a file in this list is not a symlink, its path will be included unchanged.
        If a file in this list does not exist, it will be treated as though it is not a symlink. Accepts either a
        path to a symlink or a list of paths.

    :return:
        A list of the real paths being pointed to by the symlinks.
    """

    assert type(symlinks_p) in [list, set, tuple, str]

    if type(symlinks_p) != list:
        symlinks_p = list(symlinks_p)

    output = list()

    for symlink_p in symlinks_p:
        output.append(os.path.realpath(symlink_p))
    return output


# ----------------------------------------------------------------------------------------------------------------------
def is_root(path_p):
    """
    Returns True if the path given is the root of the filesystem. Only works on Unix-like systems at the moment.

    :param path_p:
        The path we are testing to see if it is the root path.

    :return:
        True if path_p is the root of the filesystem.
    """

    root = os.path.abspath(os.sep)
    return path_p == root
