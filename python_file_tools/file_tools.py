#!/usr/bin/env python3

import json
import os
import re
import shutil
import tempfile
import zipfile
import html_string_tools
import python_file_tools.sort as pft_sort
from os.path import abspath, basename, exists, isdir, join, relpath
from typing import List

def write_text_file(file:str, text:str):
    """
    Writes a file containing the given text.
    Will overwrite existing files
    
    :param file: Path of the file to create
    :type file: str, required
    :param text: Text to save in the file
    :type text: str, required
    """
    try:
        full_path = abspath(file)
        with open(full_path, "w", encoding="UTF-8") as out_file:
            out_file.write(text)
    except FileNotFoundError: pass

def read_text_file(file:str) -> str:
    """
    Reads the content of a given text file.
    
    :param file: Path of the file to read
    :type file: str, required
    :return: Text contained in the given file
    :rtype: str
    """
    encodings = ["utf-8", "ascii", "latin_1", "cp437", "cp500"]
    for encoding in encodings:
        try:
            with open(abspath(file), "rb") as in_file:
                data = in_file.read()
                text = data.decode(encoding)
                return text.strip()
        except: pass
    return None

def write_json_file(file:str, contents:dict):
    """
    Writes a JSON file containing the given dictionary as contents.
    
    :param file: Path of the file to create
    :type file: str, required
    :param text: Contents to save as JSON
    :type text: str, required
    """
    json_text = json.dumps(contents, indent="   ", separators=(", ", ": "))
    write_text_file(file, json_text)

def read_json_file(file:str) -> dict:
    """
    Returns the contents of a given JSON file as a dictionary.
    
    :param file: JSON file to read.
    :type file: str, required
    :return: Contents of the JSON file
    :rtype: dict
    """
    try:
        json_text = read_text_file(file)
        json_dict = json.loads(json_text)
        return json_dict
    except(TypeError, json.JSONDecodeError): return {}

def find_all_files(directory:str, include_subdirectories:bool=True) -> List[str]:
    """
    Returns a list of all files within a given directory

    :param directory: Directory in which to search for files
    :type directory: str, required
    :param include_subdirectories: Whether to also search subdirectories for files, defaults to True
    :type include_subdirectories: bool, optional
    :return: List of all files, giving the full file path
    :rtype: list[str]
    """
    # Run through all directories
    files = []
    directories = [abspath(directory)]
    while len(directories) > 0:
        # Get list of all files in the current directory
        current_files = os.listdir(directories[0])
        for filename in current_files:
            # Check if file is a directory
            full_file = abspath(join(directories[0], filename))
            if not isdir(full_file):
                files.append(full_file)
            elif include_subdirectories:
                directories.append(full_file)
        # Delete the current directory from the list
        del directories[0]
    # Return list of files
    return pft_sort.sort_alphanum(files)

def find_files_of_type(directory:str, extension:str,
            include_subdirectories:bool=True, inverted:bool=False) -> List[str]:
    """
    Returns a list of files in a given directory that match a given file extension.
    
    :param directory: Directory in which to search for files
    :type directory: str, required
    :param extension: File extension(s) to search for
    :type extension: str/List[str], required
    :param include_subdirectories: Whether to also search subdirectories for files, defaults to True
    :type include_subdirectories: bool, optional
    :param inverted: If true, searches for files WITHOUT the given extension, defaults to False
    :type inverted: bool, optional
    :return: List of files that match the extension, giving the full file path
    :rtype: list[str]
    """
    # Get the list of extensions
    extensions = extension
    if isinstance(extensions, str):
        extensions = [extensions.lower()]
    else:
        for i in range(0, len(extensions)):
            extensions[i] = extensions[i].lower()
    # Get list of all files in the given directory
    all_files = find_all_files(directory, include_subdirectories)
    # Find files that match the given extensions
    files = []
    for current_file in all_files:
        current_extension = html_string_tools.get_extension(current_file).lower()
        if not (current_extension in extensions) == inverted:
            files.append(current_file)
    # Return files
    return files

def directory_contains(directory:str, extension:List[str], include_subdirectories:bool=True) -> bool:
    """
    Returns whether a given directory contains a file with any of the given extensions.

    :param directory: Directory in which to search for files
    :type directory: str, required
    :param extensions: List of extensions to search for
    :type extensions: List[str], required
    :param include_subdirectories: Whether to search subdirectories, defaults to True
    :type include_subdirectories: bool, optional
    :return: Whether any files of the given extensions exist in the given directory
    :rtype: bool
    """
    directories = [abspath(directory)]
    # Get the list of extensions
    extensions = extension
    if isinstance(extensions, str):
        extensions = [extensions]
    # Run through all directories
    while len(directories) > 0:
        # Get list of all files in the current directory
        current_files = os.listdir(directories[0])
        for filename in current_files:
            # Get the full file
            full_file = abspath(join(directories[0], filename))
            # Check if the file is a directory
            if isdir(full_file):
                if include_subdirectories:
                    directories.append(full_file)
                continue
            # Check if the extension matches
            cur_extension = html_string_tools.get_extension(full_file).lower()
            if cur_extension in extensions:
                return True
        # Delete the current directory from the list
        del directories[0]
    # Return false if no files of the type specified were found
    return False

def create_zip(directory:str, zip_path:str, compress_level:int=9, mimetype:str=None) -> bool:
    """
    Creates a zip file with all the files and subdirectories within a given directory.
    
    :param directory: Directory with files to archive into a zip file
    :type directory: str, required
    :param zip_path: Path of the zip file to be created
    :type zip_path: str, required
    :param compress_level: Level of compression from min 0 to max 9, defaults to 9
    :type compress_level: int, optional
    :return: Whether a zip file was successfully created
    :param mimetype: Mimetype for the file to be added without compression for zip-based formats, defaults to None
    :type mimetype: str
    :rtype: bool
    """
    # Get list of files in the directory
    full_directory = abspath(directory)
    files = os.listdir(full_directory)
    for i in range(0, len(files)):
        files[i] = abspath(join(full_directory, files[i]))
    # Expand list of files to include subdirectories
    for file in files:
        if isdir(file):
            sub_files = os.listdir(file)
            for i in range(0, len(sub_files)):
                files.append(abspath(join(file, sub_files[i])))
    # Create empty zip file
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compress_level) as out_file:
        if mimetype is not None:
            out_file.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
    if not exists(zip_path):
        return False
    # Write contents of directory to zip file
    for file in files:
        if not basename(file).startswith("."):
            relative = relpath(file, full_directory)
            with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED, compresslevel=compress_level) as out_file:
                out_file.write(file, relative)
    # Return if the zip file was successfully created
    return exists(zip_path)

def extract_zip(zip_path:str, extract_directory:str, create_folder:bool=False,
                remove_internal:bool=False, delete_files:List[str]=[]) -> bool:
    """
    Extracts a ZIP file into a given directory without ever overwriting files.
    
    :param zip_path: Path to ZIP file to extract
    :type zip_path: str, required
    :param extract_directory: Directory in which to extract ZIP contents
    :type extract_directory: str, required
    :param create_folder: Whether to create a folder within the given directory to hold contents, defaults to False
    :type create_folder: bool, optional
    :param remove_internal: Whether to remove redundant internal folder, defaults to False
    :type remove_internal: bool, optional
    :param delete_files: List of filenames to delete if desired, defaults to []
    :type delete_files: list[str], optional
    :return: Whether the files were extracted successfully
    :rtype: bool
    """
    # Get temporary directory
    with tempfile.TemporaryDirectory() as unzip_dir:
        # Unzip files into temp directory
        try:
            with zipfile.ZipFile(zip_path, mode="r") as file:
                file.extractall(path=unzip_dir)
        except (FileNotFoundError, OSError, zipfile.BadZipFile): return False
        # Delete listed files
        for delete_file in delete_files:
            full_file = abspath(join(unzip_dir, delete_file))
            if exists(full_file):
                os.remove(full_file)
        # Remove internal folder if specified
        if remove_internal and len(os.listdir(unzip_dir)) == 1:
            full_file = abspath(join(unzip_dir, os.listdir(unzip_dir)[0]))
            if isdir(full_file):
                unzip_dir = full_file
        # Check if any of the to be extracted files already exist in the new directory
        contains_existing = create_folder
        files = os.listdir(unzip_dir)
        for current_file in files:
            if contains_existing:
                break
            contains_existing = exists(join(extract_directory, current_file))
        # Create new extraction subfolder if specified
        main_dir = abspath(extract_directory)
        new_dir = abspath(extract_directory)
        if create_folder or contains_existing:
            filename = basename(zip_path)
            extension = html_string_tools.get_extension(filename)
            filename = filename[:len(filename) - len(extension)]
            filename = get_available_filename(["AAAAAAAAAA"], filename, main_dir)
            new_dir = abspath(join(main_dir, filename))
            os.mkdir(new_dir)
        # Copy files to new directory
        files = os.listdir(unzip_dir)
        for current_file in files:
            extension = html_string_tools.get_extension(current_file)
            filename = current_file[:len(current_file) - len(extension)]
            filename = get_available_filename([current_file], filename, new_dir)
            old_file = abspath(join(unzip_dir, current_file))
            new_file = abspath(join(new_dir, f"{filename}{extension}"))
            if isdir(old_file):
                shutil.copytree(old_file, new_file)
            else:
                shutil.copy(old_file, new_file)
    return True

def extract_file_from_zip(zip_path:str, extract_directory:str, extract_file:str, check_subdirectories:bool=False) -> str:
    """
    Attempts to extract a single file from a ZIP archive given a filename.
    
    :param zip_path: ZIP archive to extract a file from.
    :type zip_path: str, required
    :param extract_directory: Directory in which to extract the file.
    :type extract_directory: str, required
    :param extract_file: Filename of the file to be extracted
    :type extract_file: str, required
    :param check_subdirectories: Whether to check subdirectories for the given file as well, defaults to False
    :type check_subdirectories: bool, optional
    :return: Path of the extracted file, None if file couldn't be extracted
    :rtype: str
    """
    try:
        # Get temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, mode="r") as zfile:
                # Get the correct file to extract
                internal_file = None
                info_list = zfile.infolist()
                for info in info_list:
                    if info.filename == extract_file or (check_subdirectories and basename(info.filename) == extract_file):
                        internal_file = info.filename
                # Attempt extracting the file
                zfile.extract(internal_file, path=temp_dir)
                extracted = abspath(join(temp_dir, internal_file))
                new_file = abspath(join(extract_directory, extract_file))
                # Update file if it already exists
                if exists(new_file):
                    extension = html_string_tools.get_extension(extract_file)
                    filename = extract_file[:len(extract_file) - len(extension)]
                    filename = get_available_filename([extracted], filename, extract_directory)
                    new_file = abspath(join(extract_directory, f"{filename}{extension}"))
                # Copy file to new location
                shutil.copy(extracted, new_file)
                return new_file
    except (zipfile.BadZipFile, FileNotFoundError, OSError, KeyError, zipfile.BadZipFile): return None

def get_file_friendly_text(string:str, ascii_only:bool=False) -> str:
    """
    Creates a string suitable for a filename from a given string.

    :param string: Any string to convert into filename
    :type string: str, required
    :param ascii_only: Whether to only allow basic ASCII characters, defaults to False
    :type ascii_only: bool, optional
    :return: String with all invalid characters removed or replaced
    :rtype: str
    """
    # Return default string if the whole name is disallowed
    reserved = "^con$|^prn$|^aux$|^nul$|^com[1-5]$|^lpt[1-5]$"
    if string is None or len(re.findall(reserved, string.lower())) > 0:
        return "0"
    # Unify hyphen and whitespace varieties
    new_string = re.sub(r"\s", " ", string)
    new_string = re.sub(r"[\-－﹣‑‐⎼]", "-", new_string)
    # Replace special structures
    new_string = re.sub(r":", " - ", new_string)
    new_string = re.sub(r"\s+\-+>\s+", " to ", new_string)
    new_string = re.sub(r"(?:\.\s*){2}\.", "…", new_string)
    # Remove invalid filename characters
    new_string = re.sub(r'[<>"\\\/\|\*\?]', "-", new_string)
    new_string = re.sub(r"[\x00-\x1F]|(?:\s*\.\s*)+$", "", new_string)
    # Replace repeated hyphens and whitespace
    new_string = re.sub(r"\-+(?:\s*\-+)*", "-", new_string)
    new_string = re.sub(r"\s+", " ", new_string)
    # Remove hanging hyphens
    new_string = re.sub(r"(?<=[^\s])-(?=\s)|(?<=\s)-(?=[^\s])", "", new_string)
    # Remove whitespace and hyphens from the end of string
    new_string = re.sub(r"^[\s\-]+|[\s\-]+$", "", new_string)
    # Replace non-standard ASCII characters, if specified
    if ascii_only:
        new_string = re.sub(r"[ÀÁÂÃÄÅ]", "A", new_string)
        new_string = re.sub(r"[ÈÉÊË]", "E", new_string)
        new_string = re.sub(r"[ÌÍÎÏ]", "I", new_string)
        new_string = re.sub(r"[ÒÓÔÕÖ]", "O", new_string)
        new_string = re.sub(r"[ÙÚÛÜ]", "U", new_string)
        new_string = re.sub(r"[ÑŃ]", "N", new_string)
        new_string = re.sub(r"[ÝŸ]", "Y", new_string)
        new_string = re.sub(r"[àáâãäå]", "a", new_string)
        new_string = re.sub(r"[èéêë]", "e", new_string)
        new_string = re.sub(r"[ìíîï]", "i", new_string)
        new_string = re.sub(r"[òóôõö]", "o", new_string)
        new_string = re.sub(r"[ùúûü]", "u", new_string)
        new_string = re.sub(r"[ńñ]", "n", new_string)
        new_string = re.sub(r"[ýÿ]", "y", new_string)
        regex = r"[\.\x22-\x27\x2A-\x2F\x3A-\x40\x5E-\x60]|[^\x20-\x7A]"
        new_string = re.sub(regex, "-", new_string)
        return get_file_friendly_text(new_string, False)
    # Check if the string is empty
    if new_string == "":
        return "0"
    # Return the modified string
    return new_string

def get_available_filename(source_files:List[str], filename:str, end_path:str, ascii_only:bool=False) -> str:
    """
    Returns a filename not already taken in a given directory.
    The given disired filename will be slightly modified if already taken.

    :param source_files: File(s) with extensions to use when checking for existing files
    :type source_files: List[str]/str, required
    :param filename: The desired filename (without extension)
    :type filename: str, required
    :param end_path: The path of the directory with files to check against
    :type end_path: str, required
    :param ascii_only: Whether to only allow basic ASCII characters in the filename, defaults to False
    :type ascii_only:bool, optional
    :return: Filename that is available to be used in the given directory
    :rtype: str
    """
    # Get the file friendly version of the desired filename
    new_filename = get_file_friendly_text(filename, ascii_only)
    # Get extensions from the source files
    extensions = []
    if isinstance(source_files, list):
        for source_file in source_files:
            extensions.append(html_string_tools.get_extension(source_file))
    else:
        extensions = [html_string_tools.get_extension(source_files)]
    # Get a list of all the files in the end path
    try:
        files = []
        for file in os.listdir(abspath(end_path)):
            files.append(file.lower())
    except FileNotFoundError:
        return None
    # Get the new filename that is available
    base = new_filename
    append_num = 1
    while True:
        try:
            for extension in extensions:
                assert not (f"{new_filename}{extension}").lower() in files
            return new_filename
        except AssertionError:
            append_num += 1
            new_filename = f"{base}-{append_num}"

def rename_file(file:str, new_filename:str, ascii_only:bool=False) -> str:
    """
    Renames a given file to a given filename.
    Number will be appended to filename if file already exists with that name.

    :param file: Path of the file to rename
    :type file: str, required
    :param new_filename: Filename to set new file to
    :type new_filename: str, required
    :param ascii_only: Whether to only allow basic ASCII characters in the filename, defaults to False
    :type ascii_only:bool, optional
    :return: Path of the file after being renamed, None if rename failed
    :rtype: str
    """
    # Get the prefered new filename
    path = abspath(file)
    extension = html_string_tools.get_extension(file)
    filename = get_file_friendly_text(new_filename, ascii_only)
    # Do nothing if the filename is already accurate
    if basename(path) == f"{filename}{extension}":
        return path
    # Update filename if file already exists
    parent_dir = abspath(join(path, os.pardir))
    filename = get_available_filename([file], new_filename, parent_dir, ascii_only)
    # Rename file
    try:
        new_file = abspath(join(parent_dir, f"{filename}{extension}"))
        os.rename(path, new_file)
        return new_file
    except FileNotFoundError:
        return None
