import sys

import os
import tarfile
import uuid
import re
import zlib

requestConfig = {
    "headers": {
        "Accept": "application/zip",
    },
    "responseType": "arraybuffer",
}
requestConfigAcceptAll = {
    "headers": {
        "Accept": "*/*",
    },
    "responseType": "arraybuffer",
}


def getProjectDirectory(projectUuid):
    current_directory = os.getcwd()
    print("Current working directory: {0}".format(current_directory))
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    projectDirectory = parent_directory + "/repositories"

    if not os.path.exists(projectDirectory):
        os.makedirs(projectDirectory)

    myProjectFolder = projectDirectory + "/" + projectUuid
    if not os.path.exists(myProjectFolder):
        os.makedirs(myProjectFolder)

    return myProjectFolder


def getProjectLocation(projectUuid):
    current_directory = os.getcwd()
    print("Current working directory: {0}".format(current_directory))

    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    print(parent_directory)

    myProjectFolder = getProjectDirectory(projectUuid)
    projectFiles = myProjectFolder + "/files"

    return {"projectFiles": projectFiles, "myProjectFolder": myProjectFolder}


def get_all_file_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


def find_files(directory):
    files = []
    directory = os.path.abspath(directory)  # Convert to absolute path for consistency

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)

            # Remove the directory prefix from the full path
            reduced_path = os.path.relpath(full_path, directory)

            files.append(reduced_path)

    return files
    # files = []
    # base_dir = os.path.basename(directory.rstrip(os.sep))  # Get the base directory name
    #
    # for root, dirs, filenames in os.walk(directory):
    #     for filename in filenames:
    #         full_path = os.path.join(root, filename)
    #
    #         # Compute the relative path and prepend the base directory
    #         rel_path = os.path.relpath(full_path, directory)
    #         reduced_path = os.path.join(base_dir, rel_path)
    #
    #         files.append(reduced_path)
    #
    # return files


def read_first_50_lines(file_path):
    """Reads the first 50 lines of a file and returns them while preserving indentation."""
    lines = []
    try:
        with open(file_path, 'r') as file:
            for i in range(50):
                line = file.readline()
                if not line:
                    break
                lines.append(line.rstrip())  # Preserve the indentation
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return lines

