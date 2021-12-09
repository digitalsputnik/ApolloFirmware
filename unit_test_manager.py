# Unit Tests

def init():
    global unit_test_results
    unit_test_results = ""

init()

# -- PySaver unit test Implementation Start

import pysaver

def pysaver_tests():
    global unit_test_results
    
    test_results = pysaver.run_tests()
    
    for test_type in test_results:
        for value_type in test_type:
            unit_test_results += value_type[2] + " with type " + str(value_type[0]) + "\n"

pysaver_tests()

# -- PySaver unit test Implementation End

def save_test_results():
    test_results = open('Data/unit_test_results.txt',mode='w')
    test_results.write(unit_test_results)
    print(unit_test_results)
    test_results.close()

save_test_results()