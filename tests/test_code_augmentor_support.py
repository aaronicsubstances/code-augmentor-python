import os.path
import re
import sys

from code_augmentor_support.tasks import ProcessCodeTask

# pre-import for use by scripts.
from code_augmentor_support.models import CodeAugmentorFunctions

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
    task.verbose = True
    
    printHeader('test_usage_producing_unset_ids')
    task.execute(evalerProducingUnsetIds)
    printErrors(task)
    
    assert len(task.allErrors) == 2
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_usage_producing_duplicate_ids(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-01.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    task.verbose = True
    
    printHeader('test_usage_producing_duplicate_ids')
    task.execute(evalerProducingDuplicateIds)
    printErrors(task)
    
    assert len(task.allErrors) == 1
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_usage_with_production_evaler(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-01.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    task.verbose = True
    
    printHeader('test_usage_with_production_evaler')
    task.execute(productionEvaler)
    printErrors(task)
    
    assert len(task.allErrors) == 2
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_usage_with_missing_evaler_return_value(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-01.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-ignore.json')
    task.verbose = True
    
    printHeader('test_usage_with_missing_evaler_return_value')
    task.execute(evalerWithoutReturn)
    printErrors(task)
    
    assert len(task.allErrors) == 1
    print(f'\nExpected {len(task.allErrors)} error(s)')
    
def test_context_scope_method_access(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'aug_codes-02.json')
    task.outputFile = os.path.join(tmpdir, 'genCodes-py-02.json')
    
    printHeader('test_context_scope_method_access')
    task.execute(contextScopeMethodAccessEvaler)
    printErrors(task)
    
    assert not task.allErrors
    
    with open(task.outputFile, encoding='utf8') as f:
        data = f.read()
    assert re.sub(r'\r\n|\n|\r', "\n", data) == '{}\n' + \
        '{"fileId":1,"generatedCodes":[' + \
        '{"id":1,"skipped":true},' + \
        '{"id":2,"skipped":true},' + \
        '{"id":3,"skipped":true}]}\n'

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

def contextScopeMethodAccessEvaler(f, a, c):
    if f != "\"testUseOfGetScopeVar\"":
        return productionEvaler(f, a, c)
    assert c.getScopeVar("address") == "NewTown"
    assert c.getScopeVar("serviceType") == "ICT"
    assert c.getScopeVar("allServiceTypes") == "ICT,Agric"
    assert c.globalScope["address"] == "OldTown"
    assert c.getScopeVar("codeAugmentor_indent") == "    "
    return c.newSkipGenCode()
