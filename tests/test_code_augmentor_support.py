import os.path
import sys

from code_augmentor_support import __version__
from code_augmentor_support.tasks import ProcessCodeTask


def test_version():
    assert __version__ == '0.1.0'

# launch with: poetry run pytest tests -s
def test_basic_usage(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'basic_usage_aug_codes.json')
    task.outputFile = os.path.join(tmpdir, 'basic_usage_gen_codes.json')
    # print blank line for nice execute output
    print
    task.execute(evaler)
    assert not task.allErrors
    print('Output successfully written to {0}'.format(task.outputFile))
    
def test_basic_eval_error(tmpdir):
    task = ProcessCodeTask()
    task.inputFile = os.path.join(os.path.dirname(__file__), 'basic_usage_aug_codes.json')
    task.outputFile = os.path.join(tmpdir, 'basic_eval_error.json')
    task.execute(productionEvaler)
    assert task.allErrors
    print(f'\nExpected errors, and found {len(task.allErrors)}')
    for error in task.allErrors:
        print(f'\t{error}')#, file=sys.stderr)
    
def evaler(functionName, augCode, context):
    return 'Received: {0}: {1}, {2}'.format(functionName, augCode, context)
    
def productionEvaler(functionName, augCode, context):
    return eval(functionName + '(augCode, context)')