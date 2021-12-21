import os

def save(save_variable_name, save_variable):
    try:
        save_file = open ("Data/_" + save_variable_name + ".py", "w")
        if (isinstance(save_variable, str)):
            save_file.write(save_variable_name + "=" + '"' + save_variable + '"' +"\n")
        else:
            save_file.write(save_variable_name + "=" + str(save_variable) +"\n")
        save_file.close()
        return True
    except Exception as e:
        print (str(e))
        return False
        
def load(load_variable, default, create_if_not_exist = False):
    try:
        exec("from Data._" + load_variable + " import " + load_variable + " as loaded_variable", globals())
        return loaded_variable
    except Exception as e:
        if (create_if_not_exist):
            save(load_variable, default)
        return default
    
def delete(load_variable):
    try:
        os.remove("Data/_" + load_variable + ".py")
        return True
    except Exception as e:
        print("Error:" + str(e))
        return False
