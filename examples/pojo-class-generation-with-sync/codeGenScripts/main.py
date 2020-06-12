import os.path
import re
import sys

from code_augmentor_support.tasks import ProcessCodeTask

import MyFunctions
import OtherFunctions

FUNCTION_NAME_REGEX = re.compile(r'^((MyFunctions|OtherFunctions)\.)[a-zA-Z]\w*$')
def callUserFunction(functionName, augCode, context):
    # validate name.
    if not FUNCTION_NAME_REGEX.search(functionName):
        raise Exception("Invalid/Unsupported function name: " + functionName)

    # name is valid. make function call "dynamically".
    result = eval(functionName + '(augCode, context)')
    return result

instance = ProcessCodeTask()
instance.inputFile = sys.argv[1]
instance.outputFile = sys.argv[2]
if len(sys.argv) > 3:
    instance.verbose = bool(sys.argv[3])
instance.execute(callUserFunction)
if instance.allErrors:
    print(str(len(instance.allErrors)) + " error(s) found.", file=sys.stderr)
    for errMsg in instance.allErrors:
        print(errMsg, file=sys.stderr)
    sys.exit(1)