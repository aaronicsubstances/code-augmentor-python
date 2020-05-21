import os.path
import sys

from code_augmentor_support import __version__
from code_augmentor_support.tasks import ProcessCodeTask

# launch with: poetry run pytest tests -s

#
# Main purpose of tests in this project is to test
# error cases and the formatting of thrown exceptions.
# More thorough testing of success case scenerios is dealt with outside this
# project.
#
def test_basic_usage(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-00.json')
    task.outputFile = os.path.join(tmpdir, 'actual_gen_codes.json')

    printHeader('test_basic_usage')
    task.execute(evaler)
    printErrors(task)
    
    assert not task.allErrors
    print('Output successfully written to {0}'.format(task.outputFile))
    
def test_usage_producing_unset_ids(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-00.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    
    printHeader('test_usage_producing_unset_ids')
    task.execute(evalerProducingUnsetIds)
    printErrors(task)
    
    assert len(task.allErrors) == 2
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_usage_producing_duplicate_ids(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-01.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    
    printHeader('test_usage_producing_duplicate_ids')
    task.execute(evalerProducingDuplicateIds)
    printErrors(task)
    
    assert len(task.allErrors) == 1
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_usage_with_production_evaler(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-01.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    
    printHeader('test_usage_with_production_evaler')
    task.execute(productionEvaler)
    printErrors(task)
    
    assert len(task.allErrors) == 2
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_usage_with_missing_evaler_return_value(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-01.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    
    printHeader('test_usage_with_production_evaler')
    task.execute(evalerWithoutReturn)
    printErrors(task)
    
    assert len(task.allErrors) == 1
    print(f'\nExpected {len(task.allErrors)} error(s)')

def printHeader(testName):
    print()
    print(testName)
    print('--------------------')
    
def printErrors(task):
    for error in task.allErrors:
        print(error)#, file=sys.stderr)
    print()

def evaler(functionName, augCode, context):
    return 'Received: {0}: {1}, {2}'.format(functionName, augCode, context)

def evalerProducingUnsetIds(functionName, augCode, context):
    genCode = context.newGenCode()
    #genCode.id = augCode['id']
    genCode.contentParts.append(context.newContent('Received: {0}'.format(functionName)))
    return [ genCode ]

def evalerProducingDuplicateIds(functionName, augCode, context):
    genCode = context.newGenCode()
    genCode.id = 1
    genCode.contentParts.append(context.newContent('Received: {0}'.format(functionName)))
    return [ genCode ]
    
def productionEvaler(functionName, augCode, context):
    return eval(functionName + '(augCode, context)')

def evalerWithoutReturn(functionName, augCode, context):
    pass