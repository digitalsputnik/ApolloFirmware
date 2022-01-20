'''
Module to rewrite scripts on device using Repl

Usage

1. Setup rewriter password using rewriter.setup('password')
2. Authenticate rewriter (must be done again after reboot) using rewriter.auth('password')
3. Start File Upload using rewriter.start_file_upload('path', pieces_count)
4. Send file pieces in random order using rewriter.send_file_piece(piece_number, data)
5. When all the pieces are received the file is put together and saved to the path

You can ask for indexes of missing pieces using rewriter.missing_pieces()
You can ask for cancel using rewriter.cancel()

When using for the first time, default password is dsputnik.
Using setup you can set your own custom password.
Setup can be done once.

'''

import os
import pysaver

authenticated = False

# Load saved variables
_rewriter_setup = pysaver.load("rewriter_setup", False)
_rewriter_password = pysaver.load("rewriter_password", "dsputnik")

_receiving_data = False
_total_pieces = 0

_pieces_list = []

_path = ""
_full_file = ""

def setup(_pw):
    global _rewriter_password, _rewriter_setup
    # Check if setup has been ran before
    if not _rewriter_setup:
        # Set custom password 
        _rewriter_password = _pw
        pysaver.save("rewriter_password", _rewriter_password)
        # Set setup ran to True
        _rewriter_setup = True
        pysaver.save("rewriter_setup", _rewriter_setup)
        print("Rewriter setup with custom password " + _rewriter_password)
    else:
        print("Rewriter already setup with custom password")

# Function to authenticate using default/custom password
# To allow for file overwriting and disable repl filter
def auth(_pw):
    global _rewriter_password, authenticated
    if (_rewriter_password == _pw):
        authenticated = True
        print("Authenticated")
    else:
        print("Wrong Password")

# Function to call when starting to upload a file
# This sets the module to receiving mode and sets the file path/piece_count
def start_file_upload(_inc_path, _piece_count):
    global authenticated, _receiving_data, _total_pieces, _pieces_list, _path
    if authenticated:
        if not _receiving_data:
            _path = _inc_path
            _total_pieces = _piece_count
            _receiving_data = True
            for i in range(_piece_count):
                _pieces_list.append("")
            print("Upload started")
        else:
            print("Already uploading file, cancel or wait")
    else:
        print("Authenticate first")

# Function to call with each file piece
def send_file_piece(_piece_number, _data):
    global _receiving_data, _total_pieces, _received_pieces, _pieces_list, _full_file, _path
    # Check if file upload is initiated
    if _receiving_data:
        # Add file piece to a list
        _pieces_list[_piece_number] = _data
        # If all the pieces have been received, write the file to disk
        if received_pieces_count() == _total_pieces:
            for _piece in _pieces_list:
                _full_file += _piece
            write_file()
    else:
        print("File upload not initiated")

# Function to call when cancelling file upload, this resets all the progress
def cancel():
    global _receiving_data
    if _receiving_data:
        reset()
        print("File upload cancelled")
    else:
        print("Not currently uploading")

def received_pieces_count():
    global _pieces_list, _receiving_data
    if _receiving_data:
        _received = 0
        for _piece in _pieces_list:
            if _piece is not "":
                _received += 1
        return _received
    else:
        print("Not currently uploading")

# Function to call to get indexes of missing file pieces
def missing_pieces():
    global _pieces_list, _receiving_data
    if _receiving_data:
        _not_received = []
        for _index, _piece in enumerate(_pieces_list):
            if _piece is "":
                _not_received.append(_index)
        _not_received = tuple(_not_received)
        return _not_received
    else:
        print("Not currently uploading")

# Function that writes the received pieces to file
def write_file():
    global _full_file, _path, _receiving_data
    if _receiving_data:
        try:
            _write_file=open(_path, "w")
            _write_file.write(_full_file)
            _write_file.close()
            print("Uploaded. File " + _path + " modified")
            reset()
        except Exception as _e:
            print (str(_e))
            reset()
    else:
        print("Not currently uploading")

def reset():
    global _receiving_data, _total_pieces, _received_pieces, _pieces_list, _full_file, _path
    _receiving_data = False
    _total_pieces = 0
    _received_pieces = 0
    _pieces_list = []
    _full_file = ""
    _path = ""