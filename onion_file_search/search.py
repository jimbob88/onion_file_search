import os
import platform
import sys

try:
    import scandir_rs
except:
    pass


def os_walk_search(search_loc, search_var):
    return [
        os.path.join(root, filename)
        for root, directories, filenames in os.walk(search_loc)
        for filename in filenames
        if search_var in filename
    ]


def scandir_rs_search(search_loc, search_var):
    return [
        os.path.join(root, filename)
        for root, directories, filenames in scandir_rs.walk.Walk(search_loc)
        for filename in filenames
        if search_var in filename
    ]


def windows_cmd_search(search_loc, search_var):
    os.system(
        r"dir /s/b {search} > files.txt".format(
            search=os.path.join(
                search_loc, "*{file}*".format(file=search_var),)
        )
    )
    with open("files.txt", "r") as f:
        return f.read().splitlines()


def linux_cmd_search(search_var, search_loc):
    os.system(
        'find {location} -name "*{search_term}*" > ./files.txt'.format(
            location=search_loc, search_term=search_var,
        )
    )
    with open("files.txt", "r") as f:
        return f.read().splitlines()


def not_darwin_search(search_loc, search_var):
    if platform.system() == "Linux":
        return linux_cmd_search(search_loc, search_var)
    else:
        if "scandir_rs" in sys.modules:
            return scandir_rs_search(search_loc, search_var)
        else:
            return windows_cmd_search(search_loc, search_var)
