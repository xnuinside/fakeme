""" files searcher class

Walker is a class that grab recursively (or not, as you wish) folder, trying to find
files with extension what you want, for example - '.ddl' and '.hql'

If you want to get only '.ddl' with schemas it will check valid files names

"""

import glob
import io
import os


class Walker(object):

    # ddl files with names that contains such prefixes - will be ignored
    ddl_schemas_ignore_list = [
        "database",
        "drop_",
        "drop",
        "db",
        "rename",
        "create_schemas",
    ]

    def __init__(self, path_to_dir=None, extension=None, recursive=True):
        """
        :param path_to_dir:
        :type path_to_dir: str
        :param extension:
        :type extension: str
        :param recursive:
        :type recursive: bool

        """
        self.recursive = recursive
        if path_to_dir:
            self.path_to_dir = os.path.expanduser(path_to_dir)
        self.extension = extension

    def walk(self):
        """use this method to start grab files"""
        if not self.recursive:
            files = self.stump_walk()
        else:
            files = glob.glob(
                os.path.join(self.path_to_dir, "**/*.{}".format(self.extension))
            )
            [
                files.append(file_path)
                for file_path in glob.glob(
                    os.path.join(self.path_to_dir, "*.{}".format(self.extension))
                )
            ]
        if self.extension == "ddl":
            files = self.filter_files(files)
        return files

    @staticmethod
    def filter_files(files):
        """filter files to get only schemas"""
        remove = []
        for file_path in files:
            for name in Walker.ddl_schemas_ignore_list:
                if name in os.path.basename(file_path).lower():
                    remove.append(file_path)
        return filter(lambda x: x not in remove, files)

    def stump_walk(self):
        """walk only on one level inside"""
        files_list = []
        for file_path in self.find_all_files_with_extension():
            if file_path.endswith(self.extension):
                files_list.append(file_path)

        return files_list

    def find_all_files_with_extension(self):
        """find all valid files"""
        for name in os.listdir(self.path_to_dir):
            path_to_file = os.path.join(self.path_to_dir, name)
            if os.path.isfile(path_to_file):
                yield path_to_file

    @staticmethod
    def read_file(file_path, string, usages_dict, full, _encoding="UTF-8"):
        """read file"""
        with io.open(file_path, "r", encoding=_encoding) as f:
            for line in f.readlines():
                if string in line and not line.startswith("--"):
                    usages_dict[string].append(line)
                    if not full:
                        if line.split(string)[1].startswith(" ") or line.split(string)[
                            1
                        ].startswith("\n"):
                            operation_key = line.split(" ")[0].lower()
                            if not usages_dict.get(operation_key):
                                usages_dict[operation_key] = {}
                            if not usages_dict[operation_key].get(file_path):
                                usages_dict[operation_key][file_path] = []
                            usages_dict[operation_key][file_path].append(line)
