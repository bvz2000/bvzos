import os
import stat


# ----------------------------------------------------------------------------------------------------------------------
def get_metadata(file_p,
                 root_p):
    """
    Gets the metadata for the given file path.

    :param file_p:
        The path to the file to add.
    :param root_p:
        The path to the root against which a relative path is determined.

    :return:
        A dictionary of attributes.
    """

    assert type(file_p) is str
    assert type(root_p) is str

    attrs = dict()

    file_stat = os.stat(file_p, follow_symlinks=False)

    attrs["name"] = os.path.split(file_p)[1]
    attrs["file_type"] = os.path.splitext(attrs["name"])[1]
    attrs["parent"] = os.path.split(os.path.split(file_p)[0])[1]
    attrs["rel_path"] = os.path.relpath(file_p, root_p)
    attrs["size"] = file_stat.st_size
    attrs["ctime"] = file_stat.st_ctime  # Not always the creation time, but as close as it gets.
    attrs["mtime"] = file_stat.st_mtime
    attrs["isdir"] = stat.S_ISDIR(file_stat.st_mode)
    attrs["islink"] = stat.S_ISLNK(file_stat.st_mode)
    attrs["st_mode"] = file_stat.st_mode
    attrs["file_uid"] = file_stat.st_uid
    attrs["file_gid"] = file_stat.st_gid

    return attrs
