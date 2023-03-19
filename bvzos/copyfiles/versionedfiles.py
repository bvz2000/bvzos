import os
import shutil

import bvzos.fs
import bvzos.compare

from . copydescriptor import Copydescriptor


# ----------------------------------------------------------------------------------------------------------------------
def verified_copy_file(src,
                       dst):
    """
    Given a source file and a destination, copies the file, and then performs a checksum on both files to ensure that
    the copied file matches the source. Raises an error if the copied file's md5 checksum does not match the source
    file's md5 checksum.

    :param src:
        The source file to be copied.
    :param dst:
        The destination file name where the file will be copied. If the destination file already exists, an error will
        be raised. You must supply the full destination file name, not just the destination dir.

    :return:
        Nothing.
    """

    assert type(src) is str
    assert type(dst) is str

    shutil.copy(src, dst)

    if not bvzos.compare.compare_files(src, dst):
        msg = "Verification of copied file failed (md5 checksums to not match): "
        raise IOError(msg + src + " --> " + dst)


# ----------------------------------------------------------------------------------------------------------------------
def copy_and_add_ver_num(source_p,
                         dest_p,
                         ver_prefix="v",
                         num_digits=4,
                         do_verified_copy=False):
    """
    Copies a source file to the dest dir, adding a version number to the file right before the extension. If a file with
    that version number already exists, the file being copied will have its version number incremented so as not to
    overwrite the existing file. Returns a full path to the file that was copied.

    :param source_p:
        The full path to the file to be copied.
    :param dest_p:
        The full path to the destination file (path plus name).
    :param ver_prefix:
        An optional prefix to put onto the version number. For example, if the prefix is "v", then the version number
        will be represented as "v####". Defaults to "v".
    :param num_digits:
        An optional amount of padding to use for the version numbers. For example, 4 would lead to versions like: v0001
        whereas 3 would lead to versions like: v001. Defaults to 4.
    :param do_verified_copy:
        An optional boolean to perform a verified copy. Defaults to False.

    :return:
        A full path to the file that was copied.
    """

    assert type(source_p) is str
    assert type(dest_p) is str
    assert type(ver_prefix) is str
    assert type(num_digits) is int
    assert type(do_verified_copy) is bool

    dest_d, dest_n = os.path.split(dest_p)
    base, ext = os.path.splitext(dest_n)

    version = 0
    while True:
        version += 1
        version = "." + ver_prefix + str(version).rjust(num_digits, "0")
        dest_p = os.path.join(dest_d, base + version + ext)
        if not os.path.exists(dest_p):
            break

    if do_verified_copy:
        verified_copy_file(source_p, dest_p)
    else:
        shutil.copy(source_p, dest_p)

    return dest_p


# ----------------------------------------------------------------------------------------------------------------------
def create_copydescriptor(file_p,
                          relative_p,
                          link_in_place):
    """
    Given a full path to a file, the relative path, the destination directory, and a boolean that describes whether the
    source file should be linked in place, returns a copydescriptor that stores this information.

    :param file_p:
        A full path to the file whose copy parameters are being stored in the copydescriptor.
    :param relative_p:
        The relative path to the symlink file. See the dir_to_copydescriptors method for more information on this
        relative path.
    :param link_in_place:
        Do not copy the file, but rather have the symlink file point to the original file_p.

    :return:
        A copydescriptor object.
    """

    assert type(file_p) is str
    assert type(relative_p) is str
    assert type(link_in_place) is bool

    return Copydescriptor(source_p=file_p,
                          dest_relative_p=relative_p,
                          link_in_place=link_in_place)


# ----------------------------------------------------------------------------------------------------------------------
def files_to_copydescriptors(files_p,
                             relative_d,
                             link_in_place):
    """
    Given a list of files, return a list of copydescriptors.

    :param files_p:
        A list, set, or tuple of full paths to files whose copy parameters are being stored in copydescriptors.
    :param relative_d:
        The relative path to where the symlinks will live. Do not include the name of the symlink files, just the path
        to the relative directory where they will be stored. See the dir_to_copydescriptors method for more information
        on this relative path.
    :param link_in_place:
        Do not copy the files, but rather have the symlink files point to the original files.

    :return:
        A list of copydescriptor objects.
    """

    assert type(files_p) in [list, set, tuple]
    assert type(relative_d) is str
    assert type(link_in_place) is bool

    copydescriptors = list()

    if relative_d is None:
        relative_d = ""

    for file_p in files_p:
        copydescriptors.append(create_copydescriptor(file_p=file_p,
                                                     relative_p=os.path.join(relative_d, os.path.split(file_p)[1]),
                                                     link_in_place=link_in_place))

    return copydescriptors


# ----------------------------------------------------------------------------------------------------------------------
def dir_to_copydescriptors(dir_d,
                           link_in_place):
    """
    Given a directory, return a recursive list of copydescriptors. The relative path for the symlink file (stored as
    dest_relative_p in the copydescriptor object) is calculated from the root given by dir_d.

    For example, if the dir_d has a structure like this:

    Dir_d
    |-FileA
    |-Subdir1
      |-Subdir2
        |-FileB

    Then FileA and FileB will have respective relative paths of:

    ./FileA
    ./Subdir1/Subdir2/FileB

    :param dir_d:
        A directory, all children of which will be (recursively) stored in copydescriptors.
    :param link_in_place:
        If True, then each file will be set to link in place.

    :return:
        A list of copydescriptor objects.
    """

    copydescriptors = list()

    for path, currentDirectory, files_n in os.walk(dir_d):
        for file_n in files_n:
            file_p = os.path.join(path, file_n)
            dest_relative_p = file_p.split(dir_d)[1]
            copydescriptors.append(create_copydescriptor(file_p=file_p,
                                                         relative_p=dest_relative_p,
                                                         link_in_place=link_in_place))

    return copydescriptors


# ----------------------------------------------------------------------------------------------------------------------
def copy_files_deduplicated(copydescriptors,
                            dest_d,
                            data_d,
                            ver_prefix="v",
                            num_digits=4,
                            do_verified_copy=False):
    """
    Given a list of copydescriptor objects, copy the files they represent into the dir given by data_d and make a
    symlink in the dir given by dest_d that points to these files. Does de-duplication so that if more than one file
    contains the same data (regardless of any other metadata like name or creation date) it will only be stored in
    data_d once. If the copydescriptor for a file has link_in_place set to True, then that file will not be copied to
    data_d, and the symlink in dest_d will instead point to the original source file.

    Example #1 _________________________________________________________________________________________________________

        If the copydescriptor is:
            source_p = "/another/path/to/a/source/file.txt"
            dest_relative_p = "relative/dir/new_file_name.txt"
            link_in_place = False

        and dest_d is:
            /path/to/destination/directory

        and data_d is:
            /path/to/data/directory

        Then the file will (appear) to be copied to:
            /path/to/destination/directory/relative/dir/new_file_name.txt

        but in actual fact, the above file will be a symlink that points to:
            /path/to/data/directory/new_file_name.v001.txt

    Example #2 _________________________________________________________________________________________________________

        If the copydescriptor is:
            source_p = "/another/path/to/a/source/file.txt"
            dest_relative_p = new_file_name.txt
            link_in_place = True

        and dest_d is:
            /path/to/destination/directory

        Then the file will (appear) to be copied to:
            /path/to/destination/directory/new_file_name.txt

        but in actual fact, the above file will be a symlink that points to the original source file:
            /another/path/to/a/source/file.txt

        Note: data_d is ignored in this case.

    :param copydescriptors:
        A list, set, or tuple of copydescriptor objects.
    :param dest_d:
        The full path of the root directory where the files given by sources_p will appear to be copied (they will
        appear to be copied to subdirectories of this directory, based on the relative paths given in the
        copydescriptor). They only "appear" to be copied to these locations because in actual fact they are symlinks to
        the actual file which is copied into data_d.
    :param data_d:
        The directory where the actual files will be stored.
    :param ver_prefix:
        An optional custom prefix to put onto the version number used inside the data_d dir to de-duplicate files.
        Note: This version number is NOT added to the symlink file so, as far as the end user is concerned, the version
        number does not exist. For example, if the prefix is "v", then the version number will be represented as
        "v####". But the symlinked file the end user sees does not contain this version number. Defaults to "v".
    :param num_digits:
        An optional custom amount of padding to use for the version numbers. For example, 4 would lead to versions like
        v0001 whereas 3 would lead to versions like v001. Defaults to 4.
    :param do_verified_copy:
        Optionally perform a verified copy. Defaults to False.

    :return:
        A dictionary where the key is the source file that was copied, and the value is a string representing the path
        to the actual de-duplicated file in data_d.
    """

    assert type(dest_d) is str
    assert type(data_d) is str
    assert type(copydescriptors) in [list, set, tuple]
    assert type(ver_prefix) is str
    assert type(num_digits) is int
    assert type(do_verified_copy) is bool

    if dest_d.startswith(data_d):
        raise ValueError("Destination directory may not be a child of the data directory")

    for copydescriptor in copydescriptors:

        if not os.path.exists(copydescriptor.source_p):
            raise ValueError(f"CopyDeduplicated failed: source file does not exist: {copydescriptor.source_p}")
        if not os.path.isfile(copydescriptor.source_p):
            raise ValueError(f"CopyDeduplicated failed: source file is not a file: {copydescriptor.source_p}")

    output = dict()

    compare_session_obj = bvzos.compare.Session(query_items=None, canonical_dir=data_d)
    compare_session_obj.do_canonical_scan()

    for copydescriptor in copydescriptors:

        dest_p = os.path.join(dest_d, copydescriptor.dest_relative_p.lstrip(os.sep))

        if not copydescriptor.link_in_place:
            output[copydescriptor.source_p] = copy_file_deduplicated(source_p=copydescriptor.source_p,
                                                                     dest_p=dest_p,
                                                                     data_d=data_d,
                                                                     compare_session_obj=compare_session_obj,
                                                                     ver_prefix=ver_prefix,
                                                                     num_digits=num_digits,
                                                                     do_verified_copy=do_verified_copy)
        else:
            os.makedirs(os.path.split(dest_p)[0], exist_ok=True)
            if os.path.exists(dest_p):
                os.unlink(dest_p)
            os.symlink(copydescriptor.source_p, dest_p)

    return output


# TODO: Not windows compatible!!
# ----------------------------------------------------------------------------------------------------------------------
def copy_file_deduplicated(source_p,
                           dest_p,
                           data_d,
                           compare_session_obj,
                           ver_prefix="v",
                           num_digits=4,
                           do_verified_copy=False):
    """
    Given a full path to a source file, copy that file into the data directory and make a symlink in dest_p that points
    to this file. Does de-duplication so that if more than one file contains the same data (regardless of name or any
    other file stats), it will only be stored in data_d once. See copy_files_deduplicated for more details.

    :param source_p:
            A full path to where the source file is.
    :param dest_p:
            The full path of where the file will appear to be copied. The file only appears to be copied to this
            location because in actual fact dest_p will be a symlink that points to the actual file which is copied to
            the directory data_d.
    :param data_d:
            The directory where the actual files will be stored.
    :param compare_session_obj:
        The compare session object that contains the canonical scan.
    :param ver_prefix:
            The prefix to put onto the version number used inside the data_d dir to de-duplicate files. This version
            number is NOT added to the symlink file so, as far as the end user is concerned, the version number does not
            exist. For example, if the prefix is "v", then the version number will be represented as "v####". Defaults
            to "v".
    :param num_digits:
            How much padding to use for the version numbers. For example, 4 would lead to versions like: v0001 whereas 3
            would lead to versions like: v001. Defaults to 4.
    :param do_verified_copy:
            If True, then a verified copy will be performed. Defaults to False.

    :return:
            The string representing the path to the actual de-duplicated file in data_d.
    """

    assert type(dest_p) is str
    assert type(data_d) is str
    assert type(source_p) is str
    assert type(ver_prefix) is str
    assert type(num_digits) is int
    assert type(do_verified_copy) is bool

    if dest_p.startswith(data_d):
        raise ValueError("Destination file may not be a child of the data directory")

    if not os.path.isfile(source_p):
        raise ValueError(f"copy_file_deduplicated failed: source file is not a file or does not exist: {source_p}")

    compare_session_obj.query_items = source_p
    compare_session_obj.do_query_scan()
    compare_session_obj.do_compare()

    if not compare_session_obj.duplicates:
        dest_n = os.path.split(dest_p)[1]
        data_file_p = copy_and_add_ver_num(source_p=source_p,
                                           dest_p=os.path.join(data_d, dest_n),
                                           ver_prefix=ver_prefix,
                                           num_digits=num_digits,
                                           do_verified_copy=do_verified_copy)
        compare_session_obj.append_to_canonical_scan(data_file_p)
    else:
        data_file_p = compare_session_obj.duplicates[source_p][0]

    # Create the directories where the symlink will be stored.
    os.makedirs(os.path.split(dest_p)[0], exist_ok=True)

    # Build a relative path from dest_p to the file we just copied into the data dir. Then create a symlink to this file
    # in the destination.
    relative_p = os.path.relpath(data_file_p, os.path.split(dest_p)[0])

    if os.path.exists(dest_p):
        os.unlink(dest_p)
    os.symlink(relative_p, dest_p)

    return data_file_p
