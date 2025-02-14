import os
import re
import sys

import utilz


def load_file(filename):
    raise NotImplementedError


def find_files(search_directory, base_name=None, extension=None):
    """
    The function returns files with the argument combination as logical switcher.
    :param search_directory: If none other argument is provided, all files in this directory will be returned.
    :param base_name: The filename to search for, if provided the function will return the specific file that matches said name.
    :param extension: Extension of the file to search for, if the filename is not provided, it will search for all files with this extension.
    :return: List of / single file matching the arguments given.
    """
    found_files = []
    for root, directories, files in os.walk(search_directory):
        for file in files:
            split_name, split_extension = os.path.splitext(file)
            if base_name and extension:
                if split_name == base_name and split_extension == extension:
                    found_files.append(os.path.join(root, file))
                    utilz.printer(
                        message=f"Found file '{split_name}' with extension '{split_extension}' in [{search_directory}]",
                        log_type=utilz.Type.INFO,
                    )
            elif extension:
                if file.endswith(extension) or split_extension == extension:
                    utilz.printer(
                        message=f"Found file: {file} with extension: {extension}",
                        log_type=utilz.Type.INFO,
                    )
                    found_files.append(os.path.join(root, file))

            elif base_name:
                if split_name == base_name:
                    utilz.printer(
                        message=f"Found file: {split_name} with extension: {split_extension}",
                        log_type=utilz.Type.INFO,
                    )
                    found_files.append(os.path.join(root, file))
            else:
                utilz.printer(
                    message=f"Found file in the search_directory: {search_directory}",
                    log_type=utilz.Type.INFO,
                )
                found_files.append(os.path.join(root, file))

        return found_files


def find_folder_by_name(searched_folder_name=None, search_location=None):
    """
    Searches for folders with a specific name within a given location on the filesystem.

    Args:
        searched_folder_name (str): The name of the folder to search for.
        search_location (str): The path to the directory to search within.

    Returns:
        list: A list of paths to folders that match the searched folder name.
    """
    found_candidates = []
    for root, dirs, files in os.walk(search_location):
        for folder in dirs:
            if searched_folder_name == folder:
                found_candidates.append(os.path.join(root, folder))

    return found_candidates


def find_folder_by_pattern(searched_pattern=None, search_location=None):
    """
    Searches for folders that match a specific regex pattern within a given location on the filesystem.

    Args:
        searched_pattern (str): The regex pattern to match folder names.
        search_location (str): The path to the directory to search within.

    Returns:
        list: A list of paths to folders that match the regex pattern.
    """
    found_candidates = []
    pattern = re.compile(searched_pattern)
    for root, dirs, files in os.walk(search_location):
        for folder in dirs:
            if pattern.match(folder):
                found_candidates.append(os.path.join(root, folder))

    return found_candidates


def test():
    files = find_files(
        # base_name="bubu",
        # extension=".txt",
        search_directory="secret_path",  #anonymized
    )
    for file in files:
        print(f"file: {file}")

    print(find_folder_by_name("secret", "secret_path"))  #anonymized
    print(
        find_folder_by_pattern(
            searched_pattern="secret_pattern",
            search_location="secret_path",  #anonymized
        )
    )


if __name__ == "__main__":
    test()
