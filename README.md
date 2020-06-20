# code-augmentor-support

This package enables the use of Python 3 as a scripting platform to generate code to serve the goals of Code Augmentor.

Code Augmentor is a set of libraries, plugins and tools for bringing code generation techniques to every programmer. For a more detailed explanation please visit the main Code Augmentor Github repository [here](https://github.com/aaronicsubstances/code-augmentor).

As far as this package and Python 3 developers are concerned, it is enough to think of Code Augmentor as (1) a command-line application, (2) which is configured to run an [Apache Ant](https://ant.apache.org) XML build file, (3) which in turn runs a Python 3 package or project written by a programmer, (4) with the aim of generating code for Python 3 or  another target programming language, (5) using this package as a dependency.


## Install

`pip install code-augmentor-support`

If using poetry, can rather use `poetry install code-augmentor-support`

## Example

Below is a main script demonstrating how to set up the library for use with functions defined in two client modules snippets.py and worker.py.

It requires input and ouput file command-line arguments, and optional third argument to enable verbose logging.

```
python main.py test-augCodes.json actual.json
```

Or if using poetry,
```
poetry run python main.py test-augCodes.json actual.json
```

### main.py

```python
import os.path
import re
import sys

from code_augmentor_support.tasks import ProcessCodeTask
from code_augmentor_support.models import CodeAugmentorFunctions

import snippets
import worker

FUNCTION_NAME_REGEX = re.compile(r'^(((.*CodeAugmentorFunctions)|snippets|worker)\.)[a-zA-Z]\w*$')
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
```

### snippets.py

```python
def generateSerialVersionUID(augCode, context):
    return "private static final int serialVersionUID = 23L;"
```

### worker.py

```python
def stringify(augCode, context):
    g = context.newGenCode()
    for i in range(len(augCode.args)):
        s = '"' + augCode.args[i]
        if i < len(augCode.args) - 1:
            s += augCode.lineSeparator + '" +'
        else:
            s += '"'
        g.contentParts.append(context.newContent(s, True))
    return g
```

### test-augCodes.json (sample input file)

```json
{ "genCodeStartDirective": "//:GS:", "genCodeEndDirective": "//:GE:", "embeddedStringDirective": "//:STR:", "embeddedJsonDirective": "//:JSON:", "skipCodeStartDirective": "//:SS:", "skipCodeEndDirective": "//:SE:", "augCodeDirective": "//:AUG_CODE:", "inlineGenCodeDirective": "//:GG:", "nestedLevelStartMarker": "[", "nestedLevelEndMarker": "]" }
{"fileId":1,"dir":"src","relativePath":"A1.py","augmentingCodes":[{"id":1,"directiveMarker":"//:AUG_CODE:","indent":"","lineNumber":1,"lineSeparator":"\n","nestedLevelNumber":0,"hasNestedLevelStartMarker":false,"hasNestedLevelEndMarker":false,"blocks":[{"stringify":false,"jsonify":false,"content":" snippets.generateSerialVersionUID "}]}]}
{"fileId":2,"dir":"src","relativePath":"B2.py","augmentingCodes":[{"id":1,"directiveMarker":"//:AUG_CODE:","indent":"","lineNumber":1,"lineSeparator":"\n","nestedLevelNumber":0,"hasNestedLevelStartMarker":false,"hasNestedLevelEndMarker":false,"blocks":[{"stringify":false,"jsonify":false,"content":" worker.stringify "},{"stringify":true,"jsonify":false,"content":" SELECT * FROM contacts "},{"stringify":true,"jsonify":false,"content":" WHERE contacts.id = ? "}]},{"id":2,"directiveMarker":"//:AUG_CODE:","indent":"","lineNumber":19,"lineSeparator":"\n","nestedLevelNumber":0,"hasNestedLevelStartMarker":false,"hasNestedLevelEndMarker":false,"blocks":[{"stringify":false,"jsonify":false,"content":" snippets.generateSerialVersionUID "},{"stringify":false,"jsonify":true,"content":"{ \"name\": \"expired\", \"type\": \"boolean\" } "}]}]}

```

### expected.json (expected output file)

```json
{}
{"fileId":1,"generatedCodes":[{"id":1,"contentParts":[{"content":"private static final int serialVersionUID = 23L;","exactMatch":false}]}]}
{"fileId":2,"generatedCodes":[{"id":1,"contentParts":[{"content":"\" SELECT * FROM contacts \n\" +","exactMatch":true},{"content":"\" WHERE contacts.id = ? \"","exactMatch":true}]},{"id":2,"contentParts":[{"content":"private static final int serialVersionUID = 23L;","exactMatch":false}]}]}

```

## Usage

The library's functionality is contained in the method `execute` of the class `ProcessCodeTask` in the `tasks` module of this package. The `execute` method takes a function object used for evaluating code generation requests and producing generated code snippets.

Instances of `ProcessCodeTask` have the following properties:

   * `inputFile` - path to the code generation request. Must be the aug code file result of running the *code_aug_prepare* Ant task.
   * `outputFile` - path for writing out code generation response. Will be used as the gen code file input to the *code_aug_complete* Ant task.
   * `verbose` - boolean property which can be used with default verbose logging mechansim to enable printing of verbose mesages to standard output.
   * `allErrors` - array which contains any errors encountered during execution.
   
These methods can be overriden in a subclass:
   * `logVerbose`, `logInfo`, `logWarn` - methods which are called with a format string, *args, and **kwargs, when a verbose message, normal message, or warning message is issued. By default all normal and warning messages are printed to standard output, and verbose messages are ignored.

The `evalFunction` function argument of the `execute` method is called with 3 arguments. The first is name of a function to invoke in the current Python scope, and the remaining two are an augmenting code object and a helper instance of the `ProcessCodeContext` class from the `models` module of this package. These remaining two arguments are the arguments passed to the function to be invoked.

The `evalFunction` is called with every augmenting code object encountered in the input file. It is expected to in turn call client-defined functions dynamically and receive from them a correponding generated code object to be written to the output file. As a convenience, it can return strings, content parts, and arrays of generated code objects.


### Properties and Methods of `ProcessCodeContext` instances

   * *header* - JSON object resulting from parsing first line of input file.
   * *globalScope* - a readonly dictionary provided for use by clients which remains throughout parsing of entire input file.
   * *fileScope* - an dictionary provided for use by clients which is reset at the start of processing every line of input file.
   * *fileAugCodes* - JSON object resulting of parsing current line of input file other than first line.
   * *augCodeIndex* - index of `augCode` parameter in `fileAugCodes.augmentingCodes` array
   * *newGenCode()* - convenience method available to clients for creating a generated code object with empty `contentParts` array property.
   * *newContent(content, exactMatch=false)* - convenience method available to clients for creating a new content part object with properties set with arguments supplied to the function.
   * *newSkipGenCode()* - convenience method to create a generated code object indicating skipping of aug code section. Will have null content parts.
   * *getScopeVar(name)* - gets a variable from fileScope array with given name, or from globalScope array if not found in fileScope.

### Reserved 'CodeAugmentor' Prefix

CodeAugmentor supplies utility functions and variables by reserving the **CodeAugmentor** prefix. As such scripts should avoid naming aug code processing functions and variables in fileScope/globalScope with that prefix.

The following variables are provided by default in context globalScope:

   * *codeAugmentor_indent* - set with value of four spaces.

The following functions are provided by **CodeAugmentorFunctions** class of the `models` module of this package for use to process aug codes:

   * *CodeAugmentorFunctions.setScopeVar* - requires each embedded data in augmenting code section to be a JSON object. For each such object, every property of the object is used to set a variable in context fileScope whose value is the value of the property in the JSON object.
   * *CodeAugmentorFunctions.setGlobalScopeVar* - same as setScopeVar, but rather sets variables in context globalScope.

### Note on JSON serialization

This library deserializes JSON objects into instances of the class [types.SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace). It similarly requires objects to be serialized to be either dictionaries or instances of `types.SimpleNamespace`. 

By so doing clients are provided with the convenience that any arbitrary field can be set on a JSON object, and it will get serialized. 

The default Python behaviour will apply though, when trying to access non-existent fields on a deserialized JSON object by raising an error. In that case, the function `hasattr` will have to be called first.

## Further Information

For more information on the structure of augmenting code object, generated code object and other considerations, refer to [wiki](https://github.com/aaronicsubstances/code-augmentor/wiki/Documentation-for-Code-Generator-Scripts) in the main Code Augmentor repository.


## Building and Testing Locally

[Poetry](https://python-poetry.org/) is the build system for this project. So it is required to set up it first.

   * Clone repository locally
   * Install project dependencies with `poetry install`
   * With all dependencies present locally, test project with `poetry run pytest tests -s`
