'''
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

version = 1.3

hashes = pysaver.load("hashes", {}, True)
repo_hash = pysaver.load("repo_hash", None, True)
dirty_files = pysaver.load("dirty_files", [], True)

authenticated = False

rewriter_setup = pysaver.load("rewriter_setup", False)
rewriter_password = pysaver.load("rewriter_password", "dsputnik")

receiving_data = False
total_pieces = 0

pieces_list = []

path = ""
full_file = ""
current_file_hash = ""

def setup(pw):
    global rewriter_password, rewriter_setup
    if not rewriter_setup:
        rewriter_password = pw
        pysaver.save("rewriter_password", rewriter_password)
        rewriter_setup = True
        pysaver.save("rewriter_setup", rewriter_setup)
        print("Rewriter setup with custom password " + rewriter_password)
    else:
        print("Rewriter already setup with custom password")

def auth(pw):
    global rewriter_password, authenticated
    if (rewriter_password == pw):
        authenticated = True
        print("Authenticated")
    else:
        print("Wrong Password")
        
def check_file_hash(file_name, file_hash):
    global hashes
    if file_hash in hashes.values():
        return "correct"
    elif file_name in hashes.keys():
        return "outdated"
    else:
        return "none"

def start_file_upload(inc_path, piece_count, file_hash = None):
    global authenticated, receiving_data, total_pieces, pieces_list, path, current_file_hash
    if authenticated:
        if not receiving_data:
            if file_hash is not None:
                current_file_hash = file_hash
            path = inc_path
            total_pieces = piece_count
            receiving_data = True
            for i in range(piece_count):
                pieces_list.append("")
            print("Upload started")
        else:
            print("Already uploading file, cancel or wait")
    else:
        print("Authenticate first")
        
def send_file_piece(piece_number, data, is_byte=False):
    global receiving_data, total_pieces, received_pieces, pieces_list, full_file, path
    if receiving_data:
        pieces_list[piece_number] = data
        if received_pieces_count() == total_pieces:
            for piece in pieces_list:
                if is_byte:
                    full_file += piece.decode('utf-8')
                else:
                    full_file += piece
            write_file()
    else:
        print("File upload not initiated")

def cancel():
    global receiving_data
    if receiving_data:
        reset()
        print("File upload cancelled")
    else:
        print("Not currently uploading")

def received_pieces_count():
    global pieces_list, receiving_data
    if receiving_data:
        received = 0
        for piece in pieces_list:
            if piece is not "":
                received += 1
        return received
    else:
        print("Not currently uploading")
        
def missing_pieces():
    global pieces_list, receiving_data
    if receiving_data:
        not_received = []
        for index, piece in enumerate(pieces_list):
            if piece is "":
                not_received.append(index)
        not_received = tuple(not_received)
        if not_received == []:
            return False
        else:
            return not_received
    else:
        return False
    
def write_file():
    global full_file, path, receiving_data, current_file_hash
    if receiving_data:
        try:
            write_file=open(path, "w")
            write_file.write(full_file)
            write_file.close()
            update_hash_list(path, current_file_hash)
            print("Uploaded. File " + path + " modified")
            reset()
        except Exception as e:
            print (str(e))
            reset()
    else:
        print("Not currently uploading")

def reset():
    global receiving_data, total_pieces, received_pieces, pieces_list, full_file, path, current_file_hash
    receiving_data = False
    total_pieces = 0
    received_pieces = 0
    pieces_list = []
    full_file = ""
    path = ""
    current_file_hash = ""
    
def update_hash_list(path, file_hash):
    global hashes
    hashes[path] = file_hash
    pysaver.save("hashes", hashes)
    
def update_repo_hash(new_repo_hash):
    global repo_hash
    repo_hash = new_repo_hash
    pysaver.save("repo_hash", repo_hash)
    print("Repo hash updated")
    
def clear_dirty_files():
    global dirty_files
    dirty_files = []
    pysaver.save("dirty_files", dirty_files)
    
def add_dirty_file(dirty_file_path):
    global dirty_files
    if dirty_file_path not in dirty_files:
        dirty_files.append(dirty_file_path)
        pysaver.save("dirty_files", dirty_files)
    print("File Added")

def remove_dirty_file(dirty_file_path):
    global dirty_files
    if dirty_file_path in dirty_files:
        dirty_files.remove(dirty_file_path)
        pysaver.save("dirty_files", dirty_files)
    print("File Removed")