# -- Implementation

import os

def save(save_variable_name, save_variable):
    try:
        save_file = open ("Data/_" + save_variable_name + ".py", "w")
        if (isinstance(save_variable, str)):
            save_file.write(save_variable_name + "=" + '"' + save_variable + '"' +"\n")
        else:
            save_file.write(save_variable_name + "=" + str(save_variable) +"\n")
        save_file.close()
        return ("Success", True)
    except Exception as e:
        return (str(e), False)
        
def load(load_variable):
    try:
        exec("from Data._" + load_variable + " import " + load_variable + " as loaded_variable", globals())
        return (loaded_variable, True)
    except Exception as e:
        return (str(e), False)


# -- Unit testing

# Saving unit test
# Save function must always take a variable name and value and save them in a python file as an importable variable.
# The file name should always be the variable name with an underscore infront of it.
# The file should reside in the Data folder.
# If there is no file to overwrite, the file must be created automatically.
# It should be possible to save any type of variable
# It should be possible to overwrite a variable multiple times in runtime.
# The variable should be accessible even after machine.reset().

# Loading unit test
# Load function must always load a variable from a python file by importing it.
# The name of the python file should always be the variable name with an underscore infront of it.
# The file should always reside in the Data folder.
# It should be possible to load any type of variable
# It should be possible to load a variable multiple times in runtime
# The variable should be accessible until machine.reset().

# Limitations
# Currently can't load a single variable multiple times on runtime

# To run unit tests, run the run_tests() function. It returns a list of tuples (results) for each test type
# You can specify a test type by passing the type as a first parameter if you wish to run a specific test
# Example -  run_tests("save") - This runs only the saving unit test.
# List of available tests - "save", "load", "all"

# By default the types that are tested are int, string and tuple.
# You can run the tests with custom types by passing them as a second parameter in the run_tests function
# Example - run_tests("all", [("tuple_type", (0,1,2), .. ] or run_tests(values = [("tuple_type", (0,1,2), .. ])

# Return example: [(value_type, test_result(bool), info), .. ]

def run_tests(specific_test = "all", values = [("number",1), ("string_value","value"), ("tuple_value", ("hello", "world"))]):
    
    # Create lists that hold test result tuples
    save_test_results = []
    load_test_results = []
    
    # Check test type to run
    if (specific_test == "all" or specific_test == "save"):
        # Run a test with each set of input values
        for value in values:
            try:
                # Get test result as a tuple - (result_string/error_string, bool)
                result = save_unit_test(value[0], value[1])
                # Check if test passed, if not add error_string to result
                if (result[1]):
                    # Add test result to results list (value_type_tested, test_passed_bool, error_info_result_string)
                    save_test_results.append((type(value[1]), True, "PySaver save passed"))
                else:
                    # Add test result to results list (value_type_tested, test_passed_bool, error_info_result_string)
                    save_test_results.append((type(value[1]), False, "PySaver save failed. Error: " + result[0]))
            except Exception as e:
                # Add test result to results list (value_type_tested, test_passed_bool, error_info_result_string)
                save_test_results.append((type(value[1]), False, "PySaver save failed. Error: " + str(e)))
    
    # Check test type to run            
    if (specific_test == "all" or specific_test == "load"):
        # Run a test with each set of input values
        for value in values:
            try:
                # Get test result as a tuple - (result_string/error_string, bool)
                result = load_unit_test(value[0], value[1])
                # Check if test passed, if not add error_string to result
                if (result[1]):
                    # Add test result to results list (value_type_tested, test_passed_bool, error_info_result_string)
                    load_test_results.append((type(value[1]), True, "PySaver load passed"))
                else:
                    # Add test result to results list (value_type_tested, test_passed_bool, error_info_result_string)
                    load_test_results.append((type(value[1]), False, "PySaver load failed. Error: " + result[0]))
            except Exception as e:
                # Add test result to results list (value_type_tested, test_passed_bool, error_info_result_string)
                load_test_results.append((type(value[1]), False, "PySaver load failed. Error: " + str(e)))
    
    # Return specified test results
    if (specific_test == "all"):
        return (save_test_results, load_test_results)
    elif (specific_test == "save"):
        return save_test_results
    elif (specific_test == "load"):
        return load_test_results

# Saving unit test implementation
def save_unit_test(name, value):
    try:
        # Try to save using pysaver.save() method
        result = save(name, value)
        
        # Read the saved file back using built in open method
        result_test = open('Data/_' + name + '.py',mode='r').read()
        
        # Check if no errors occured when using pysaver.save()
        # Second tuple value in result is a bool that indicates success
        if (result[1]):
            
            # Check if value was string
            # We do this because strings need quotations in a comparison
            if (isinstance(value, str)):
                # Check if value is correct
                if (result_test == str(name) + '="' + value + '"\n'):
                    return (result[0], True)
                else:
                    return ("Saved value incorrect", False)
            else:
                if (result_test == str(name) + '=' + str(value) + "\n"):
                    return (result[0], True)
                else:
                    return ("Saved value incorrect", False)
            os.remove('Data/_' + name + '.py')
        else:
            # If an error occurred while usind pysaver.save(), the error
            # is returned in the result tuple as a first value
            return (result[0], False)
    except Exception as e:
        return (str(e), False)
        
# Loading unit test implementation
def load_unit_test(name, value):
    try:
        # Try to write a file manually to load using pysaver.load()
        file_to_load = open('Data/_' + name + '.py',mode='w')
        
        # Check if value was string
        # We do this because strings need quotations in a comparison
        if (isinstance(value, str)):
            file_to_load.write(name + '="' + value + '"' + "\n")
        else:
            file_to_load.write(name + "=" + str(value) +"\n")
        file_to_load.close()
        
        # Load value using pysaver.load()
        loaded_value = load(name)
        os.remove('Data/_' + name + '.py')
        
        # Check if no errors occured when using pysaver.load()
        # Second tuple value in result is a bool that indicates success
        if (loaded_value[1]):
            # Check if value is correct
            if (loaded_value[0] == value):
                return loaded_value
            else:
                return ("Loaded value incorrect", False)
        else:
            # If an error occurred while usind pysaver.save(), the error
            # is returned in the result tuple as a first value
            return (loaded_value[0], False)
    except Exception as e:
        return (str(e), False)