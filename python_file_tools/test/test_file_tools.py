#!/usr/bin/env python3

import os
import shutil
import tempfile
import python_file_tools
import python_file_tools.test as pft_test
from os.path import abspath, basename, join

def test_read_text_file():
    """
    Tests the read_text_file function.
    """
    # Test reading a basic unicode text file
    text_directory = abspath(join(pft_test.BASIC_DIRECTORY, "text"))
    text_file = abspath(join(text_directory, "unicode.txt"))
    assert python_file_tools.read_text_file(text_file) == "This is ünicode."
    # Test reading non-unicode text files
    text_file = abspath(join(text_directory, "latin1.txt"))
    assert python_file_tools.read_text_file(text_file) == "This is lätin1."
    text_file = abspath(join(text_directory, "cp437.TXT"))
    assert python_file_tools.read_text_file(text_file) == "This is cp437."
    # Test reading a non-text file
    assert python_file_tools.read_text_file(pft_test.BASIC_DIRECTORY) is None

def test_write_text_file():
    """
    Tests the write_text_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test writing a basic text file
        text_file = abspath(join(temp_dir, "test.txt"))
        python_file_tools.write_text_file(text_file, "This is text!")
        assert python_file_tools.read_text_file(text_file) == "This is text!"
        # Test overwriting a text file
        python_file_tools.write_text_file(text_file, "New\nText.")
        assert python_file_tools.read_text_file(text_file) == "New\nText."
        # Test writing to an invalid location
        fake_text_file = abspath(join("/non/existant/dir/", "fake.txt"))
        python_file_tools.write_text_file(fake_text_file, "Thing")
        assert os.listdir(abspath(temp_dir)) == ["test.txt"]

def test_read_json_file():
    """
    Tests the read_json_file function.
    """
    # Test reading a basic unicode JSON file
    json_directory = abspath(join(pft_test.BASIC_DIRECTORY, "json"))
    json_file = abspath(join(json_directory, "unicode.json"))
    json = python_file_tools.read_json_file(json_file)
    assert json["name"] == "vãlue"
    assert json["number"] == 25
    assert json["boolean"] == False
    assert json["internal"] == {"key":"another"}
    # Test reading a non-unicode JSON file
    json_file = abspath(join(json_directory, "latin1.JSON"))
    json = python_file_tools.read_json_file(json_file)
    assert json["new"] == "Títle"
    # Test reading a non-JSON file
    json_file = abspath(join(pft_test.BASIC_DIRECTORY, "unicode.txt"))
    assert python_file_tools.read_json_file(json_file) == {}
    assert python_file_tools.read_json_file(pft_test.BASIC_DIRECTORY) == {}

def test_write_json_file():
    """
    Tests the write_json_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test writing a JSON file
        dictionary = {"name":"title", "num":42, "boolean":True}
        json_file = abspath(join(temp_dir, "test.json"))
        python_file_tools.write_json_file(json_file, dictionary)
        assert python_file_tools.read_json_file(json_file) == dictionary
        # Test overwriting a JSON file
        python_file_tools.write_json_file(json_file, {"A":"B"})
        assert python_file_tools.read_json_file(json_file) == {"A":"B"}
        # Test writing a JSON file to an invalid location
        fake_json_file = abspath(join("/non/existant/dir/", "fake.json"))
        python_file_tools.write_json_file(fake_json_file, "Thing")
        assert os.listdir(abspath(temp_dir)) == ["test.json"]

def test_get_extension():
    """
    Tests the get_extension function.
    """
    # Test getting extensions from filenames
    assert python_file_tools.get_extension("test.png") == ".png"
    assert python_file_tools.get_extension(".long") == ".long"
    assert python_file_tools.get_extension("test2.thing") == ".thing"
    assert python_file_tools.get_extension("blah.test.png") == ".png"
    # Test getting extensions from URLs with tokens
    assert python_file_tools.get_extension("test.mp4?extra_.thing") == ".mp4"
    assert python_file_tools.get_extension("thing.test.thing?") == ".thing"
    assert python_file_tools.get_extension("another.txt? test.png?extra.thing") == ".png"
    # Test getting invalid extensions
    assert python_file_tools.get_extension("test.tolong") == ""
    assert python_file_tools.get_extension("test.notextension") == ""
    assert python_file_tools.get_extension("asdfasdfasdfasdf") == ""
    assert python_file_tools.get_extension("test.tolong?extra") == ""
    assert python_file_tools.get_extension("none?") == ""
    # Test getting extension if given string is None
    assert python_file_tools.get_extension(None) == ""

def test_extract_zip():
    """
    Tests the extract_zip function.
    """
    # Get file paths
    zip_file = abspath(join(pft_test.BASIC_DIRECTORY, "archive.zip"))
    text_directory = abspath(join(pft_test.BASIC_DIRECTORY, "text"))
    non_zip_file = abspath(join(text_directory, "unicode.txt"))
    # Test extracting a zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        assert python_file_tools.extract_zip(zip_file, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(temp_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(temp_dir, "DELETE.txt"))
        assert python_file_tools.read_text_file(text_file) == "Delete Me!"
    # Test extracting a zip file with an added container directory
    with tempfile.TemporaryDirectory() as temp_dir:
        assert python_file_tools.extract_zip(zip_file, temp_dir, create_folder=True)
        assert os.listdir(temp_dir) == ["archive"]
        archive_dir = abspath(join(temp_dir, "archive"))
        assert sorted(os.listdir(archive_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(archive_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(internal_dir, "Text1.txt"))
        assert python_file_tools.read_text_file(text_file) == "This is text!"
    # Test is the container directory already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        duplicate_dir = abspath(join(temp_dir, "archive"))
        os.mkdir(duplicate_dir)
        assert python_file_tools.extract_zip(zip_file, temp_dir, create_folder=True)
        assert sorted(os.listdir(temp_dir)) == ["archive", "archive-2"]
        archive_dir = abspath(join(temp_dir, "archive-2"))
        assert sorted(os.listdir(archive_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(archive_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(internal_dir, "Text2.txt"))
        assert python_file_tools.read_text_file(text_file) == "Another File."
    # Test extracting zip while deleting unwanted files
    with tempfile.TemporaryDirectory() as temp_dir:
        assert python_file_tools.extract_zip(zip_file, temp_dir, delete_files=["DELETE.txt"])
        assert sorted(os.listdir(temp_dir)) == ["Internal", "metadata.json"]
        internal_dir = abspath(join(temp_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(temp_dir, "metadata.json"))
        assert python_file_tools.read_json_file(text_file) == {"title":"Zip Test"}
    # Test extracting zip while removing internal directory
    with tempfile.TemporaryDirectory() as temp_dir:
        delete = ["DELETE.txt", "metadata.json"]
        assert python_file_tools.extract_zip(zip_file, temp_dir, create_folder=True, remove_internal=True, delete_files=delete)
        assert os.listdir(temp_dir) == ["archive"]
        archive_dir = abspath(join(temp_dir, "archive"))
        assert sorted(os.listdir(archive_dir)) == ["Text1.txt", "Text2.txt"]
    # Test that directory is not removed with external files
    with tempfile.TemporaryDirectory() as temp_dir:
        assert python_file_tools.extract_zip(zip_file, temp_dir, remove_internal=True)
        assert sorted(os.listdir(temp_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(temp_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
    # Test if the extracted files already exist
    with tempfile.TemporaryDirectory() as temp_dir:
        python_file_tools.write_text_file(abspath(join(temp_dir, "Text1.txt")), "A")
        python_file_tools.write_text_file(abspath(join(temp_dir, "Text2.txt")), "B")
        delete = ["DELETE.txt", "metadata.json"]
        assert python_file_tools.extract_zip(zip_file, temp_dir, remove_internal=True, delete_files=delete)
        assert sorted(os.listdir(temp_dir)) == ["Text1.txt", "Text2.txt", "archive"]
        text_file = abspath(join(temp_dir, "Text1.txt"))
        assert python_file_tools.read_text_file(text_file) == "A"
        sub_dir = abspath(join(temp_dir, "archive"))
        text_file = abspath(join(sub_dir, "Text1.txt"))
        assert python_file_tools.read_text_file(text_file) == "This is text!"
        text_file = abspath(join(sub_dir, "Text2.txt"))
        assert python_file_tools.read_text_file(text_file) == "Another File."
    # Test that paired files remain connected when there's a file name conflict
    base_dir = pft_test.ZIP_CONFLICT_DIRECTORY
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = abspath(join(temp_dir, "extract"))
        shutil.copytree(base_dir, extract_dir)
        zip_file = abspath(join(extract_dir, "blue.zip"))
        assert python_file_tools.extract_zip(zip_file, extract_dir, remove_internal=True)
        files = sorted(os.listdir(extract_dir))
        assert len(files) == 5
        assert files[0] == "blue"
        assert files[1] == "blue.jpg"
        assert files[2] == "blue.json"
        assert files[3] == "blue.zip"
        assert files[4] == "folder"
        assert sorted(os.listdir(abspath(join(extract_dir, "folder")))) == ["outside.txt"]
        sub_dir = abspath(join(extract_dir, "blue"))
        assert sorted(os.listdir(sub_dir)) == ["blue.json", "blue.png", "folder"]
        assert sorted(os.listdir(abspath(join(sub_dir, "folder")))) == ["internal.txt"]
    # Test if an invalid zip file is given
    with tempfile.TemporaryDirectory() as temp_dir:
        assert not python_file_tools.extract_zip(non_zip_file, temp_dir)
        assert not python_file_tools.extract_zip("/non/existant/", temp_dir)
        assert os.listdir(temp_dir) == []

def test_extract_file_from_zip():
    """
    Tests the extract_file_from_zip function.
    """
    # Get file paths
    zip_file = abspath(join(pft_test.BASIC_DIRECTORY, "archive.zip"))
    text_directory = abspath(join(pft_test.BASIC_DIRECTORY, "text"))
    non_zip_file = abspath(join(text_directory, "unicode.txt"))
    # Test extracting a file from a zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = python_file_tools.extract_file_from_zip(zip_file, temp_dir, "metadata.json")
        assert os.listdir(temp_dir) == ["metadata.json"]
        assert abspath(join(extracted, os.pardir)) == abspath(temp_dir)
        assert basename(extracted) == "metadata.json"
        assert python_file_tools.read_json_file(extracted) == {"title":"Zip Test"}
    # Test extracting file from a subdirectory
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = python_file_tools.extract_file_from_zip(zip_file, temp_dir, "Text1.txt", True)
        assert os.listdir(temp_dir) == ["Text1.txt"]
        assert abspath(join(extracted, os.pardir)) == abspath(temp_dir)
        assert basename(extracted) == "Text1.txt"
        assert python_file_tools.read_text_file(extracted) == "This is text!"
    # Test if requested file is not present in the zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = python_file_tools.extract_file_from_zip(zip_file, temp_dir, "Nothing.txt", True)
        assert extracted is None
        extracted = python_file_tools.extract_file_from_zip(zip_file, temp_dir, "Text1.txt")
        assert extracted is None
        assert os.listdir(temp_dir) == []
    # Test that directories cannot be extracted
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = python_file_tools.extract_file_from_zip(zip_file, temp_dir, "Internal")
        assert extracted is None
        assert os.listdir(temp_dir) == []
    # Test if the extracted file already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        python_file_tools.write_text_file(abspath(join(temp_dir, "DELETE.txt")), "A")
        extracted = python_file_tools.extract_file_from_zip(zip_file, temp_dir, "DELETE.txt")
        assert sorted(os.listdir(temp_dir)) == ["DELETE-2.txt", "DELETE.txt"]
        assert abspath(join(extracted, os.pardir)) == abspath(temp_dir)
        assert basename(extracted) == "DELETE-2.txt"
        assert python_file_tools.read_text_file(extracted) == "Delete Me!"
    # Test extracting from an invalid zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = python_file_tools.extract_file_from_zip(non_zip_file, temp_dir, "DELETE.txt")
        assert extracted is None
        extracted = python_file_tools.extract_file_from_zip("/non/existant/file", temp_dir, "DELETE.txt")
        assert extracted is None
        assert os.listdir(temp_dir) == []

def test_create_zip():
    """
    Tests the create_zip function.
    """
    # Get file paths
    json_directory = abspath(join(pft_test.BASIC_DIRECTORY, "json"))
    non_zip_file = abspath(join(json_directory, "unicode.json"))
    # Test creating a zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        created_zip = abspath(join(temp_dir, "created.zip"))
        assert python_file_tools.create_zip(json_directory, created_zip)
        assert python_file_tools.extract_zip(created_zip, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["created.zip", "latin1.JSON", "unicode.json"]
        json_file = abspath(join(temp_dir, "latin1.JSON"))
        assert python_file_tools.read_json_file(json_file) == {"new": "Títle"}
    # Test creating a zip file with internal directories
    with tempfile.TemporaryDirectory() as temp_dir:
        created_zip = abspath(join(temp_dir, "created.zip"))
        assert python_file_tools.create_zip(pft_test.BASIC_DIRECTORY, created_zip)
        assert python_file_tools.extract_zip(created_zip, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["archive.zip", "created.zip", "html", "json", "text"]
        internal_dir = abspath(join(temp_dir, "json"))
        assert sorted(os.listdir(internal_dir)) == ["latin1.JSON", "unicode.json"]
        internal_dir = abspath(join(temp_dir, "html"))
        assert sorted(os.listdir(internal_dir)) == ["basic.html", "unformatted.html"]
        internal_dir = abspath(join(temp_dir, "text"))
        assert sorted(os.listdir(internal_dir)) == ["cp437.TXT", "latin1.txt", "unicode.txt"]
        text_file = abspath(join(internal_dir, "cp437.TXT"))
        assert python_file_tools.read_text_file(text_file) == "This is cp437."
    # Test adding a mimetype file
    with tempfile.TemporaryDirectory() as temp_dir:
        created_zip = abspath(join(temp_dir, "created.zip"))
        assert python_file_tools.create_zip(json_directory, created_zip, mimetype="Thing")
        assert python_file_tools.extract_zip(created_zip, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["created.zip", "latin1.JSON", "mimetype", "unicode.json"]
        text_file = abspath(join(temp_dir, "mimetype"))
        assert python_file_tools.read_text_file(text_file) == "Thing"

def test_get_all_files():
    """
    Tests the get_all_files function.
    """
    # Get file paths
    basic_directory = pft_test.BASIC_DIRECTORY
    text_directory = abspath(join(basic_directory, "text"))
    html_directory = abspath(join(basic_directory, "html"))
    json_directory = abspath(join(basic_directory, "json"))
    # Test finding files in a folder without subdirectories
    files = python_file_tools.find_all_files(text_directory)
    assert len(files) == 3
    assert basename(files[0]) == "cp437.TXT"
    assert basename(files[1]) == "latin1.txt"
    assert basename(files[2]) == "unicode.txt"
    assert python_file_tools.find_files_of_type(text_directory, ".png") == []
    assert python_file_tools.find_files_of_type(text_directory, ".json") == []
    assert python_file_tools.find_files_of_type(basic_directory, ".txt", False) == []
    # Test finding files while including subdirectories
    files = python_file_tools.find_all_files(basic_directory)
    assert len(files) == 8
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory
    assert basename(files[1]) == "basic.html"
    assert abspath(join(files[1], os.pardir)) == html_directory
    assert basename(files[2]) == "unformatted.html"
    assert abspath(join(files[2], os.pardir)) == html_directory
    assert basename(files[3]) == "latin1.JSON"
    assert abspath(join(files[3], os.pardir)) == json_directory
    assert basename(files[4]) == "unicode.json"
    assert abspath(join(files[4], os.pardir)) == json_directory
    assert basename(files[5]) == "cp437.TXT"
    assert abspath(join(files[5], os.pardir)) == text_directory
    assert basename(files[6]) == "latin1.txt"
    assert abspath(join(files[6], os.pardir)) == text_directory
    assert basename(files[7]) == "unicode.txt"
    assert abspath(join(files[7], os.pardir)) == text_directory
    # Test finding files while ignoring subdirectories
    files = python_file_tools.find_all_files(basic_directory, False)
    assert len(files) == 1
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory

def test_find_files_of_type():
    """
    Tests the find_files_of_type function.
    """
    # Get file paths
    basic_directory = pft_test.BASIC_DIRECTORY
    text_directory = abspath(join(basic_directory, "text"))
    html_directory = abspath(join(basic_directory, "html"))
    json_directory = abspath(join(basic_directory, "json"))
    # Test finding all files of a given extension
    files = python_file_tools.find_files_of_type(text_directory, ".txt")
    assert len(files) == 3
    assert basename(files[0]) == "cp437.TXT"
    assert basename(files[1]) == "latin1.txt"
    assert basename(files[2]) == "unicode.txt"
    assert python_file_tools.find_files_of_type(text_directory, ".png") == []
    assert python_file_tools.find_files_of_type(text_directory, ".json") == []
    assert python_file_tools.find_files_of_type(basic_directory, ".txt", False) == []
    # Test finding files while including subdirectories
    files = python_file_tools.find_files_of_type(basic_directory, ".txt")
    assert len(files) == 3
    files = python_file_tools.find_files_of_type(basic_directory, [".json", ".zip"])
    assert len(files) == 3
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory
    assert basename(files[1]) == "latin1.JSON"
    assert abspath(join(files[1], os.pardir)) == json_directory
    assert basename(files[2]) == "unicode.json"
    assert abspath(join(files[2], os.pardir)) == json_directory
    # Test finding files with inverted extension
    files = python_file_tools.find_files_of_type(basic_directory, [".txt"], inverted=True)
    assert len(files) == 5
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory
    assert basename(files[1]) == "basic.html"
    assert abspath(join(files[1], os.pardir)) == html_directory
    assert basename(files[2]) == "unformatted.html"
    assert abspath(join(files[2], os.pardir)) == html_directory
    assert basename(files[3]) == "latin1.JSON"
    assert abspath(join(files[3], os.pardir)) == json_directory
    assert basename(files[4]) == "unicode.json"
    assert abspath(join(files[4], os.pardir)) == json_directory
    files = python_file_tools.find_files_of_type(basic_directory, [".txt", ".json", ".htm", ".html"], inverted=True)
    assert len(files) == 1
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory

def test_directory_contains():
    """
    Tests the directory_contains function.
    """
    # Get file paths
    basic_directory = pft_test.BASIC_DIRECTORY
    text_directory = abspath(join(basic_directory, "text"))
    json_directory = abspath(join(basic_directory, "json"))
    # Test if a directory contains files without checking subdirectories
    assert python_file_tools.directory_contains(basic_directory, ".zip", False)
    assert python_file_tools.directory_contains(text_directory, ".txt")
    assert python_file_tools.directory_contains(text_directory, [".txt", ".json"])
    assert not python_file_tools.directory_contains(text_directory, ".t")
    assert not python_file_tools.directory_contains(text_directory, ".json")
    assert not python_file_tools.directory_contains(text_directory, [".json", ".png"])
    assert not python_file_tools.directory_contains(basic_directory, ".txt", False)
    # Test if directory contains files while checking subdirectories
    assert python_file_tools.directory_contains(basic_directory, ".zip")
    assert python_file_tools.directory_contains(basic_directory, ".json")
    assert python_file_tools.directory_contains(basic_directory, [".txt", ".png"])
    assert not python_file_tools.directory_contains(basic_directory, ".png")
    assert not python_file_tools.directory_contains(basic_directory, [".jpeg", ".png", ".pdf"])

def test_get_file_friendly_text():
    """
    Tests the get_file_friendly_text function.
    """
    # Test replacing invalid characters
    assert python_file_tools.get_file_friendly_text(r"A < B > C") == "A - B - C"
    assert python_file_tools.get_file_friendly_text(r'1 " 2 " 3') == "1 - 2 - 3"
    assert python_file_tools.get_file_friendly_text(r"A\B/C | 123") == "A-B-C - 123"
    assert python_file_tools.get_file_friendly_text(r"a*b?c") == "a-b-c"
    assert python_file_tools.get_file_friendly_text(r"abcd..") == "abcd"
    assert python_file_tools.get_file_friendly_text(r"abcd . .") == "abcd"
    assert python_file_tools.get_file_friendly_text("ABCDE") == "ABCDE"
    # Test removing reserved file names
    assert python_file_tools.get_file_friendly_text(r"CON") == "0"
    assert python_file_tools.get_file_friendly_text(r"prn") == "0"
    assert python_file_tools.get_file_friendly_text(r"AUX") == "0"
    assert python_file_tools.get_file_friendly_text(r"nul") == "0"
    assert python_file_tools.get_file_friendly_text(r"com1") == "0"
    assert python_file_tools.get_file_friendly_text(r"COM2") == "0"
    assert python_file_tools.get_file_friendly_text(r"com5") == "0"
    assert python_file_tools.get_file_friendly_text(r"lpt1") == "0"
    assert python_file_tools.get_file_friendly_text(r"LPT5") == "0"
    assert python_file_tools.get_file_friendly_text(r"CONTENT") == "CONTENT"
    assert python_file_tools.get_file_friendly_text(r"aprn") == "aprn"
    assert python_file_tools.get_file_friendly_text(r"com6") == "com6"
    assert python_file_tools.get_file_friendly_text(r"LPT6") == "LPT6"
    assert python_file_tools.get_file_friendly_text(r"LPT0") == "LPT0"
    # Test replacing different types of whitespace and hyphens
    assert python_file_tools.get_file_friendly_text(r"A－B⎼C") == "A-B-C"
    assert python_file_tools.get_file_friendly_text("1\n2\t3") == "1 2 3"
    # Test replacing multiple hyphens or whitespace
    assert python_file_tools.get_file_friendly_text(r"A-----B") == "A-B"
    assert python_file_tools.get_file_friendly_text(r"1     2") == "1 2"
    assert python_file_tools.get_file_friendly_text(r"a -  -?   -   b") == "a - b"
    assert python_file_tools.get_file_friendly_text(r"A- -*-   -Z") == "A-Z"
    # Test replacing special structures
    assert python_file_tools.get_file_friendly_text(r"A:B") == "A - B"
    assert python_file_tools.get_file_friendly_text(r"abc...") == "abc…"
    assert python_file_tools.get_file_friendly_text(r"123.  . .  . ") == "123…"
    assert python_file_tools.get_file_friendly_text(r". . . A . . . . . .") == "… A … …"
    assert python_file_tools.get_file_friendly_text(r"A -> B") == "A to B"
    assert python_file_tools.get_file_friendly_text(r"B --－－-> C") == "B to C"
    assert python_file_tools.get_file_friendly_text(r"1->3") == "1-3"
    # Test removing hanging hyphens
    assert python_file_tools.get_file_friendly_text(r"A- B") == "A B"
    assert python_file_tools.get_file_friendly_text(r"C -D") == "C D"
    assert python_file_tools.get_file_friendly_text(r"a? z") == "a z"
    assert python_file_tools.get_file_friendly_text(r"A *Z") == "A Z"
    # Test removing whitespace and hyphens from ends of string
    assert python_file_tools.get_file_friendly_text(r"   ABC    ") == "ABC"
    assert python_file_tools.get_file_friendly_text(r"- - 123 - -") == "123"
    assert python_file_tools.get_file_friendly_text(r" ?? az * * ") == "az"
    # Test replacing diacritic characters in ASCII only mode
    assert python_file_tools.get_file_friendly_text("Áéíóú") == "Áéíóú"
    assert python_file_tools.get_file_friendly_text("ÀÁÂÃÄÅ", True) == "AAAAAA"
    assert python_file_tools.get_file_friendly_text("ÈÉÊË", True) == "EEEE"
    assert python_file_tools.get_file_friendly_text("ÌÍÎÏ", True) == "IIII"
    assert python_file_tools.get_file_friendly_text("ÑŃÒÓÔÕÖ", True) == "NNOOOOO"
    assert python_file_tools.get_file_friendly_text("ÙÚÛÜÝŸ", True) == "UUUUYY"
    assert python_file_tools.get_file_friendly_text("àáâãäå", True) == "aaaaaa"
    assert python_file_tools.get_file_friendly_text("èéêë", True) == "eeee"
    assert python_file_tools.get_file_friendly_text("ìíîï", True) == "iiii"
    assert python_file_tools.get_file_friendly_text("ńñòóôõö", True) == "nnooooo"
    assert python_file_tools.get_file_friendly_text("ùúûüýÿ", True) == "uuuuyy"
    # Test non-ASCII characters are removed in ASCII only mode
    assert python_file_tools.get_file_friendly_text("$.AAA☺") == "$.AAA☺"
    assert python_file_tools.get_file_friendly_text("$.☺abz", True) == "abz"
    assert python_file_tools.get_file_friendly_text("[A] @;`^{} (Z)", True) == "[A] - (Z)"
    assert python_file_tools.get_file_friendly_text("0 % % % 9!", True) == "0 - 9!"
    # Test if the final filename has no length
    assert python_file_tools.get_file_friendly_text("@#$%^&*-=", True) == "0"
    assert python_file_tools.get_file_friendly_text("---") == "0"
    assert python_file_tools.get_file_friendly_text("   ") == "0"
    assert python_file_tools.get_file_friendly_text("") == "0"
    assert python_file_tools.get_file_friendly_text(None) == "0"

def test_get_available_filename():
    """
    Tests the get_available_filename function.
    """
    # Test getting a filename with invalid characters
    directory = pft_test.MULTI_TYPE_DIRECTORY
    assert python_file_tools.get_available_filename("a.txt", "Name?", directory) == "Name"
    assert python_file_tools.get_available_filename(["a.txt"], ".Náme.", directory) == ".Náme"
    assert python_file_tools.get_available_filename("a.txt", ".Náme.", directory, True) == "Name"
    # Test getting the filename if the desired filename already exists
    assert python_file_tools.get_available_filename("a.txt", "fíle", directory, True) == "file-2"
    assert python_file_tools.get_available_filename(["a.TXT", "a.html"], "file", directory) == "file-3"
    # Test if filename exists with filename but different capitalization
    assert python_file_tools.get_available_filename("a.txt", "OTHER", directory) == "OTHER-2"
    # Test if the filename exists, but with a different extension
    assert python_file_tools.get_available_filename("thing.png", "other", directory) == "other"
    assert python_file_tools.get_available_filename(["a.png", "b.jpg"], "file", directory) == "file"
    # Test with invalid directory
    assert python_file_tools.get_available_filename(".txt", "abc", "/non/existant/dir/") is None

def test_rename_file():
    """
    Tests the rename_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        file = abspath(join(temp_dir, "file.txt"))
        python_file_tools.write_text_file(file, "test text")
        # Test renaming file
        file = python_file_tools.rename_file(file, "Náme?")
        assert abspath(join(file, os.pardir)) == temp_dir
        assert basename(file) == "Náme.txt"
        # Test renaming file with only ASCII characters allowed
        file = python_file_tools.rename_file(file, ".Náme", True)
        assert abspath(join(file, os.pardir)) == temp_dir
        assert basename(file) == "Name.txt"
        # Test renaming file to its current name
        file = python_file_tools.rename_file(file, "Name??????????????")
        assert basename(file) == "Name.txt"
        # Test renaming file to name of existing file
        file = abspath(join(temp_dir, "new.txt"))
        python_file_tools.write_text_file(file, "new text")
        file = python_file_tools.rename_file(file, "Name")
        assert basename(file) == "Name-2.txt"
        assert sorted(os.listdir(temp_dir)) == ["Name-2.txt", "Name.txt"]
        # Test renaming same filename but different extension
        file = abspath(join(temp_dir, "Image.png"))
        python_file_tools.write_text_file(file, "image text")
        file = python_file_tools.rename_file(file, ":Name:")
        assert basename(file) == "Name.png"
        # Test that renamed files still contain the correct data
        assert sorted(os.listdir(temp_dir)) == ["Name-2.txt", "Name.png", "Name.txt"]
        file = abspath(join(temp_dir, "Name.txt"))
        assert python_file_tools.read_text_file(file) == "test text"
        file = abspath(join(temp_dir, "Name-2.txt"))
        assert python_file_tools.read_text_file(file) == "new text"
        file = abspath(join(temp_dir, "Name.png"))
        assert python_file_tools.read_text_file(file) == "image text"
        # Test renaming invalid file
        file = abspath(join(temp_dir, "non-existant"))
        assert python_file_tools.rename_file(file, "new") is None
        assert python_file_tools.rename_file("/non/existant/file", "new") is None
