#!/usr/bin/env python
# A file folder scanner contributed by @holger 
#
# You can specify the scanned folder and file pattern by changing root_path
# and pattern variables
#
__author__ = 'holger'

import argparse
from hashlib import blake2b
from pathlib import Path

from ttree import tree

FILECOUNT = 0
DIRCOUNT = 0
DIR_ERRORLIST = []
FILE_ERRORLIST = []


parser = argparse.ArgumentParser(description='Scan the given folder and print '
                                             'its structure in a tree.')
parser.add_argument('path', nargs='?', type=Path,
                    help='An path to be scanned.',
                    default=Path.cwd())
parser.add_argument('pattern', nargs='?', type=str,
                    help='File name pattern to filtered, e.g. *.pdf',
                    default="*")
parser.add_argument('--debug', type=bool, nargs='?', const=True, default=False,
                    help='Debug mode')
parser.add_argument('--profiling', type=str, choices=['timeit', 'cprofile'],
                    default=None, help='Profiling mode')

args = parser.parse_args()
root_path = Path(args.path).resolve(strict=True)

folder_tree = tree.Tree()
root_node = folder_tree.create_node(str(root_path), root_path)  # root node


def get_hash(data):
    data = bytes(str(data), 'UTF-8')
    data_hash = blake2b(data, digest_size=8).hexdigest()

    if args.debug:
        print('++++++ blake2b ++++++')
        print('input: ' + str(data))
        print('hash: ' + data_hash)
        print('+++++++++++++++++++++')
    return data_hash


def get_node_id(depth, path):
    """ get_node_id returns
        - depth contains the current depth of the folder hierarchy
        - folder contains the current directory

        Function returns a string containing the current depth, the folder name
        and unique ID build by hashing the absolute path of the directory.
        All spaces are replaced by '_'

        <depth>_<dirname>+++<hash>
        e.g. 2_Folder_XYZ_1+++<hash>
    """
    return f"{depth}_{path}+++{get_hash(path)}".replace(" ", "_")


def get_parent_id(depth, path):
    # special case for the 'root' of the tree
    # because we don't want a cryptic root-name
    if path == root_path:
        return str(root_path)

    # looking for parent directory
    # e.g. /home/user1/mp3/folder1/parent_folder/current_folder
    # get 'parent_folder'

    parent_id = f"{depth - 1}_{path.parent}+++{get_hash(path.parent)}"
    return parent_id.replace(" ", "_")


def print_node(folder, node_id, parent_id):
    print(f"""
#############################
node created
folder: {folder}
node_id: {node_id}
parent_id: {parent_id}
""")


def crawler():
    global DIRCOUNT
    global FILECOUNT

    start_depth = len(root_path.parts)

    for current_path in sorted(root_path.glob(f'**/{args.pattern}')):
        current_depth = len(current_path.parts) - start_depth
        if args.debug:
            print(f'current: {current_path}')

        node_id = get_node_id(current_depth, current_path)
        parent_id = get_parent_id(current_depth, current_path)

        if args.debug:
            print_node(current_path, node_id, parent_id)

        if parent_id not in folder_tree:
            parent_id = root_node

        # create node
        folder_tree.create_node(current_path.name, node_id, parent=parent_id)

        # +++ DIRECTORIES +++
        if current_path.is_dir():
            if parent_id == str(None):
                DIR_ERRORLIST.append(current_path)
            DIRCOUNT += 1
        elif current_path.is_file():
            # +++ FILES +++
            if parent_id == str(None):
                FILE_ERRORLIST.append(current_path)
            FILECOUNT += 1


profiling_result = None

if args.profiling is None:
    crawler()
elif args.profiling == 'timeit':
    import timeit
    timeit_result = timeit.Timer("crawler()", "from __main__ import crawler")
    profiling_result = f'time: {timeit_result.timeit(number=1)}'
elif args.profiling == 'cprofile':
    import cProfile
    profile = cProfile.Profile()
    profiling_result = profile.run("crawler()")

folder_tree.print()

if DIR_ERRORLIST:
    for item in DIR_ERRORLIST:
        print(item)
else:
    print('no directory errors')

if FILE_ERRORLIST:
    for item in FILE_ERRORLIST:
        print(item)
else:
    print('no file errors')

print(f'Count of files: {FILECOUNT}')
print(f'Count of folders: {DIRCOUNT}')
print(f'Count of tree nodes: {len(folder_tree)}')

if profiling_result is not None:
    print('\nProfiling results:')
    if isinstance(profiling_result, str):
        print(profiling_result)
    elif isinstance(profiling_result, cProfile.Profile):
        profiling_result.print_stats('ncalls')
