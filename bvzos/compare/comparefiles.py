#! /usr/bin/env python3
"""
A series of functions to compareFolders two files.
"""

import hashlib
import os.path


# ----------------------------------------------------------------------------------------------------------------------
def md5_hash_generator(file_p):
    """
    Generator that reads in a file and creates the md5 hash of that file. Yields the results as it progresses so that
    the checksum can be evaluated as the file is being inspected, and not just at the end.

    :param file_p:
        The file to hash

    :return:
        Nothing.
    """

    md5 = hashlib.md5()
    with open(file_p, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
            yield md5.hexdigest()


# ----------------------------------------------------------------------------------------------------------------------
def md5_hash(file_p):
    """
    Returns the md5 hash of the file in one pass.

    :param file_p:
        The file to hash

    :return:
        The md5 hash of the file.
    """

    md5 = hashlib.md5()
    with open(file_p, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


# ----------------------------------------------------------------------------------------------------------------------
def md5_parallel_match(file_a_p,
                       file_b_p):
    """
    Does a parallel md5 checksum on two files at the same time. The benefit of this technique is that if both files are
    different, the difference can be ascertained more quickly than if each file were checksummed in its entirety before
    being compared.

    :param file_a_p:
        The first file to be compared.
    :param file_b_p:
        The second file to be compared.

    :return:
        False if the files differ, the actual checksum if they are the same.
    """

    a_iter = md5_hash_generator(file_a_p)
    b_iter = md5_hash_generator(file_b_p)

    checksum_a = ""
    try:
        while True:
            checksum_a = next(a_iter)
            checksum_b = next(b_iter)
            if checksum_a != checksum_b:
                return False
    except StopIteration:
        return checksum_a


# ----------------------------------------------------------------------------------------------------------------------
def compare_files(file_a_p,
                  file_b_p,
                  file_a_checksum=None,
                  file_b_checksum=None):
    """
    Performs a full md5 checksum compare between two files. If the files match, the md5 hash is returned. If they
    do not match, False is returned. If either file_a_checksum or file_b_checksum are supplied, those will be used in
    place of calculating them from scratch. If neither checksum is supplied, then both files will be processed in
    parallel. Files that are different from each other will potentially process significantly faster depending on their
    size and how early in the file the difference shows up. If a file is compared with itself, it is still hashed a
    single time (so that the md5 checksum can be returned).

    :param file_a_p:
        The first file to compare
    :param file_b_p:
        The second file to compare
    :param file_a_checksum:
        If not None, then this will be used as the checksum for file A instead of calculating it. Defaults to None.
    :param file_b_checksum:
        If not None, then this will be used as the checksum for file B instead of calculating it. Defaults to None.

    :return:
        The checksum of the files if they match, False otherwise.
    """

    assert os.path.exists(file_a_p)
    assert not os.path.isdir(file_a_p)
    assert not os.path.islink(file_a_p)
    assert os.path.exists(file_b_p)
    assert not os.path.isdir(file_b_p)
    assert not os.path.islink(file_b_p)

    if file_a_p == file_b_p:
        return md5_hash(file_a_p)

    if os.stat(file_a_p, follow_symlinks=False).st_size != os.stat(file_b_p, follow_symlinks=False).st_size:
        return False

    if file_a_checksum is None and file_b_checksum is None:
        return md5_parallel_match(file_a_p, file_b_p)

    if file_a_checksum is None:
        checksum_a = md5_hash(file_a_p)
    else:
        checksum_a = file_a_checksum

    if file_b_checksum is None:
        checksum_b = md5_hash(file_b_p)
    else:
        checksum_b = file_b_checksum

    if checksum_a == checksum_b:
        return checksum_b
    else:
        return False
