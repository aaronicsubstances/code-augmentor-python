import os.path
import sys

from code_augmentor_support import __version__
from code_augmentor_support.tasks import ProcessCodeTask

# launch with: poetry run pytest tests -s
def test_basic_usage(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'basic_usage_aug_codes.json')
    task.outputFile = os.path.join(tmpdir, 'basic_usage_gen_codes.json')

    printHeader('test_basic_usage')
    task.execute(evaler)
    printErrors(task)
    
    assert not task.allErrors
    print('Output successfully written to {0}'.format(task.outputFile))
    
def test_usage_with_array_result(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'basic_usage_aug_codes.json')
    task.outputFile = os.path.join(tmpdir, 'basic_usage_gen_codes.json')
    
    printHeader('test_usage_with_array_result')
    task.execute(evalerWithArrayResult)
    printErrors(task)
    
    assert not task.allErrors
    print('Output successfully written to {0}'.format(task.outputFile))
    
def test_basic_eval_error(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'basic_usage_aug_codes.json')
    task.outputFile = os.path.join(tmpdir, 'basic_eval_error.json')
    
    printHeader('test_basic_eval_error')
    task.execute(productionEvaler)
    printErrors(task)
    
    assert task.allErrors
    print(f'\nExpected {len(task.allErrors)} error(s)')

def printHeader(testName):
    print()
    print(testName)
    print('--------------------')
    
def printErrors(task):
    for error in task.allErrors:
        print(error)#, file=sys.stderr)
    print()

def evalerWithArrayResult(functionName, augCode, context):
    genCode = context.newGenCode()
    genCode.id = augCode['id']
    genCode.contentParts.append(context.newContent('Received: {0}'.format(functionName)))
    return [ genCode ]
    
def evaler(functionName, augCode, context):
    return 'Received: {0}: {1}, {2}'.format(functionName, augCode, context)
    
def productionEvaler(functionName, augCode, context):
    return eval(functionName + '(augCode, context)')