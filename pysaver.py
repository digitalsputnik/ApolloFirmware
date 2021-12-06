import os

def save(save_variable_name, save_variable):
    try:
        try:
            os.remove("Data/_" + save_variable_name + ".py")
        except Exception as e:
            pass
        save_file = open ("Data/_" + save_variable_name + ".py", "w")
        save_file.write(save_variable_name + "=" + str(save_variable) +"\n")
        save_file.close()
    except Exception as e:
        print(str(e))
        
def load(load_variable):
    try:
        exec("from Data._" + load_variable + " import " + load_variable + " as loaded_variable", globals())
        return loaded_variable
    except Exception as e:
        print("Error: " + str(e))
    