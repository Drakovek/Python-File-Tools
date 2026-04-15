# Python-File-Tools

Python-File-Tools is a collection of simple functions for creating and manipulating files. This was all originally written form my [MetadataMagic](https://github.com/Drakovek/MetadataMagic/blob/master/README.md) project to make working with certain file archiving and creation easier, but decided to spin it off into its own thing, since I wound up finding the tools useful in other projects

These are all for using as library functions for other python projects. There are no command line utilities. I'll list the functions here, but for further details you can check the code itself. I've documented the functions and their parameters pretty well in the comments there, so I feel that should do for the time being.

# MAIN FUNCTIONS

Main file tool functions within the file_tools.py file.

## write_text_file

Writes a given piece of text to a text file in UTF-8 encoding.

## read_text_file

Returns the contents of a given text file as a string, with wide support for different text file encoding schemes.

## write_json_file

Writes a given dictionary as a .json file using UTF-8 encoding.

## read_json_file

Returns the contents of a given .json file as a python dictionary, with support for different text encoding schemes.

## get_extension

Returns the file extension for any given filename, file path, or URL

## find_all_files

Returns a list of absolute file paths for all the files in a directory, with or without subdirectories

## find_files_of_type

Returns a list of absolute file paths for all files in a directory that use a specific file extension or extensions.

## directory_contains

Returns whether a directory contains any files with a given file extension or extensions

## create_zip

Archives the contents of a directory into a zip file, adding a mimetype if desired.

## extract_zip

Extracts the contents of a .zip file into a directory, with many options for how to structure the extracted files and what files to not include.

## extract_file_from_zip

Extracts a single specific file from a .zip file

## get_file_friendly_text

Takes a given string and returns a text string that is allowed to be used as a filename across all major OSes and file systems, with option for pure ASCII text

## get_available_filename

Returns a valid filename for a directory given a desired filename, altering the name if a file with that name already exists

## rename_file

Renames a file to a given filename, taking care that the filename is valid and doesn't already exist.

# SORT FUNCTIONS

Sorting functions within the sort.py file. Mostly to do with "smart alphanumeric sorting" which is my quick way of saying sorting alphanumerically the way a human might, without getting confused by extra whitespace, capitalization, leading zeros, or other basic formatting. So "File 10" always comes after "File 2" and "b" comes after "A" unlike with basic alphabetic sorting.

## compare_alphanum

Compares two strings using smart alphanumeric comparison.

## sort_alphanum

Sorts a list of strings using smart alphanumeric sorting.

## sort_dictionaries_alphanum

Sorts a list of python dictionaries based on the contents of a given key using smart alphanumeric sorting.
