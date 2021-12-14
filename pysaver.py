import os

def save(save_variable_name, save_variable, debug = False):
    try:
        save_file = open ("Data/_" + save_variable_name + ".py", "w")
        if (isinstance(save_variable, str)):
            save_file.write(save_variable_name + "=" + '"' + save_variable + '"' +"\n")
        else:
            save_file.write(save_variable_name + "=" + str(save_variable) +"\n")
        save_file.close()
        if not debug:
            return True
        else:
            return ("Success", True)
    except Exception as e:
        if not debug:
            return False
        else:
            return (str(e), False)
        
def load(load_variable, debug = False):
    try:
        exec("from Data._" + load_variable + " import " + load_variable + " as loaded_variable", globals())
        if not debug:
            return loaded_variable
        else:
            return (loaded_variable, True)
    except Exception as e:
        if not debug:
            print (str(e))
            return str(e)
        else:
            return (str(e), False)
