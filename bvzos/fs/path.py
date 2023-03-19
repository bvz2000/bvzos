import os
import stat


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


# ----------------------------------------------------------------------------------------------------------------------
def get_root():
    """
    Returns the root of the file system. Only works on Unix-like systems at the moment.

    :return:
        The root of the filesystem.
    """

    return os.sep


# ------------------------------------------------------------------------------------------------------------------

def is_hidden(file_p):
    """
    Returns whether the given file path is a hidden file. On Unix-type systems this is simply if the file name
    begins with a dot. On Windows there is some other mechanism at play that I don't feel like dealing with right
    now. But this method exists so that I can add Windows compatibility in the future.

    :param file_p:
        The path to the file that we want to determine whether it is hidden or not.

    :return:
        True if the file is hidden. False otherwise.
    """

    assert type(file_p) is str

    return os.path.split(file_p)[1][0] == "."


# ------------------------------------------------------------------------------------------------------------------
def has_file_read_permissions(st_mode,
                              file_uid,
                              file_gid,
                              uid,
                              gid):
    """
    Returns true if the uid and gid passed has read permissions for the passed file's st_mode, file_uid, and
    file_gid.

    :param st_mode:
        The results of an os.stat.st_mode on the file in question.
    :param file_uid:
        The user id of the file in question.
    :param file_gid:
        The group id of the file in question.
    :param uid:
        The user id of the user who we are testing against.
    :param gid:
        The group id of the user who we are testing against.

    :return:
        True if the user has read permissions.
    """

    assert type(st_mode) is int
    assert type(file_uid) is int
    assert type(file_gid) is int
    assert type(uid) is int
    assert type(gid) is int

    if file_uid == uid:
        return bool(stat.S_IRUSR & st_mode)

    if file_gid == gid:
        return bool(stat.S_IRGRP & st_mode)

    return bool(stat.S_IROTH & st_mode)
