'''
Usage

1. Setup rewriter password using rewriter.setup('password')
2. Authenticate rewriter (must be done again after reboot) using rewriter.auth('password')
3. Write new files or rewrite old files using rewriter.write_file('path', 'data')

When using for the first time, default password is dsputnik.
Using setup you can set your own custom password.
Setup can be done once.

'''

import os
import pysaver

authenticated = False

rewriter_setup = pysaver.load("rewriter_setup", False)
rewriter_password = pysaver.load("rewriter_password", "dsputnik")

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
        
def write_file(file, data):
    global authenticated
    if authenticated:
        if "Data." not in file:
            try:
                write_file=open(file, "w")
                write_file.write(data)
                write_file.close()
                print("File " + file + " modified")
            except Exception as e:
                print (str(e))
        else:
            print("Unauthorized path")
    else:
        print("Authenticate first")