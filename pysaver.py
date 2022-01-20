'''
Module for saving/loading/deleting variables
'''

import os

# Saving -
# Saved varibles reside in the Data folder each in a seperate _variable_name.py file 
def save(_save_variable_name, _save_variable):
    try:
        _save_file = open ("Data/_" + _save_variable_name + ".py", "w")
        # If the variable is a string, it is neccesary to save in a different format
        if (isinstance(_save_variable, str)):
            _save_file.write(_save_variable_name + "=" + '"' + _save_variable + '"' +"\n")
        else:
            _save_file.write(_save_variable_name + "=" + str(_save_variable) +"\n")
        _save_file.close()
        return True
    except Exception as _e:
        print (str(_e))
        return False

# Loading -
# Loading files is done by importing the variable from the Data._variable_name.py file
def load(_load_variable, _default, _create_if_not_exist = False):
    try:
        exec("from Data._" + _load_variable + " import " + _load_variable + " as _loaded_variable", globals())
        return _loaded_variable
    except Exception as _e:
        # It is possible to create the saved variable if it doesn't exist already
        # By setting the create_if_not_exist variable to true
        if (_create_if_not_exist):
            save(_load_variable, _default)
        return _default

# Deleting
# Deleting is done by just deleting the saved variable file
def delete(_delete_variable):
    try:
        os.remove("Data/_" + _delete_variable + ".py")
        return True
    except Exception as _e:
        print("Error:" + str(_e))
        return False
