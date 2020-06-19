import json
import os
import os.path
import sys
import traceback

from types import SimpleNamespace as Object

from .models import ProcessCodeContext, JsonDumpHelper

def jsonParse(str):
    return json.loads(str, object_hook=lambda d: Object(**d))

def compactJsonDump(obj):
    return json.dumps(obj, cls=JsonDumpHelper, separators=(',', ':'))

class ProcessCodeTask:
    def __init__(self):
        self._inputFile = None
        self._outputFile = None
        self._verbose = False
        self._allErrors = []
        
    def execute(self, evalFunction):
        assert self._inputFile, "inputFile property is not set"
        assert self._outputFile, "outputFile property is not set"
        assert evalFunction

        self._allErrors.clear()
        
        # ensure dir exists for outputFile
        outputDir = os.path.dirname(self._outputFile)
        if outputDir:
            os.makedirs(outputDir, exist_ok=True)
        
        context = ProcessCodeContext()
        
        with open(self._inputFile, 'r', encoding='utf-8') as codeGenRequest,\
                open(self._outputFile, 'w', encoding='utf-8') as codeGenResponse:
            # begin serialize by writing header to output    
            codeGenResponse.write("{}\n")
            
            headerSeen = False
            for line in codeGenRequest:
                # begin deserialize by reading header from input
                if not headerSeen:
                    context.header = jsonParse(line)
                    headerSeen = True
                    continue
                    
                fileAugCodes = jsonParse(line)
                
                # set up context.
                context.srcFile = os.path.join(fileAugCodes.dir,
                    fileAugCodes.relativePath)
                context.fileAugCodes = fileAugCodes
                context.fileScope.clear()
                self.logVerbose("Processing {0}", context.srcFile)
                
                # fetch arguments and parse any json arguments found
                fileAugCodesList = fileAugCodes.augmentingCodes
                for augCode in fileAugCodesList:
                    augCode.processed = False
                    augCode.args = []
                    for block in augCode.blocks:
                        if block.jsonify:
                            parsedArg = jsonParse(block.content)
                            augCode.args.append(parsedArg)
                        elif block.stringify:
                            augCode.args.append(block.content)
                
                # process aug codes            
                fileGenCodeList = []
                fileGenCodes = Object(
                    fileId = fileAugCodes.fileId,
                    generatedCodes = fileGenCodeList
                )
                beginErrorCount = len(self._allErrors)
                for i in range(len(fileAugCodesList)):
                    augCode = fileAugCodesList[i]
                    if augCode.processed:
                        continue
                        
                    context.augCodeIndex = i
                    functionName = self._retrieveFunctionName(augCode)
                    genCodes = self._processAugCode(evalFunction, functionName, augCode, context)
                    fileGenCodeList.extend(genCodes)
                    
                self._validateGeneratedCodeIds(fileGenCodeList, context)
                
                if len(self._allErrors) > beginErrorCount:
                    self.logWarn("{0} error(s) encountered in {1}", len(self._allErrors) - beginErrorCount, context.srcFile)
                    
                if not self._allErrors:
                    codeGenResponse.write(compactJsonDump(fileGenCodes) + "\n")
                self.logInfo("Done processing {0}", context.srcFile)
    
    def logVerbose(self, formatStr, *args, **kwargs):
        if self._verbose:
            print("[VERBOSE] " + formatStr.format(*args, **kwargs))
    
    def logInfo(self, formatStr, *args, **kwargs):
        print("[INFO] " + formatStr.format(*args, **kwargs))
    
    def logWarn(self, formatStr, *args, **kwargs):
        print("[WARN] " + formatStr.format(*args, **kwargs))

    def _retrieveFunctionName(self, augCode):
        functionName = augCode.blocks[0].content.strip()
        return functionName

    def _processAugCode(self, evalFunction, functionName, augCode, context):
        try:
            result = evalFunction(functionName, augCode, context)
            
            if result == None:
                return [ self._convertGenCodeItem(None) ]
            converted = []
            if isinstance(result, (list, tuple, set)):
                for item in result:
                    genCode = self._convertGenCodeItem(item)
                    converted.append(genCode)
                    # try and mark corresponding aug code as processed.
                    if genCode.id > 0:
                        correspondingAugCodes = [x for x in
                            context.fileAugCodes.augmentingCodes
                                if x.id == genCode.id]
                        if correspondingAugCodes:
                            correspondingAugCodes[0].processed = True
            else:
                genCode = self._convertGenCodeItem(result)
                genCode.id = augCode.id
                converted.append(genCode)
            return converted
        except BaseException as evalEx:
            self._createException(context, None, sys.exc_info() )
            return []

    def _convertGenCodeItem(self, item):
        if item == None:
            return Object(id = 0)
        elif hasattr(item, 'skipped') or hasattr(item, 'contentParts'):
            if not hasattr(item, 'id'):
                item.id = 0
            return item
        elif hasattr(item, 'content'):
            return Object(id = 0, contentParts = [ item ])
        else:
            content = str(item)
            contentPart = Object(content = content, exactMatch = False)
            return Object(id = 0, contentParts = [ contentPart ])
        
    def _validateGeneratedCodeIds(self, genCodes, context):
        ids = [x.id for x in genCodes]
        # Interpret use of -1 or negatives as intentional and skip
        # validating negative ids.
        validIds = [x for x in ids if x > 0]
        if [x for x in ids if not x]:
            self._createException(context, 'At least one generated code id was not set. Found: ' + str(ids))
        elif len(set(validIds)) < len(validIds):
            self._createException(context, 'Valid generated code ids must be unique, but found duplicates: ' + str(ids))            
    
    def _createException(self, context, message, evalExInfo=None):
        lineMessage = ''
        stackTrace = ''
        if evalExInfo:
            augCode = context.fileAugCodes.augmentingCodes[context.augCodeIndex]
            lineMessage = F" at line {augCode.lineNumber}"
            message = "{0}: {1}".format(augCode.blocks[0].content, 
                "".join(traceback.format_exception_only(evalExInfo[0], evalExInfo[1])))
            stackTrace = '\n' + "".join(
                traceback.format_exception(evalExInfo[0], evalExInfo[1], evalExInfo[2]))
         
        exception = "in {0}{1}: {2}{3}".format(context.srcFile, lineMessage, message, stackTrace)
        self._allErrors.append(exception)
        
    @property
    def inputFile(self):
        return self._inputFile
        
    @inputFile.setter
    def inputFile(self, value):
        self._inputFile = value
        
    @property
    def outputFile(self):
        return self._outputFile
        
    @outputFile.setter
    def outputFile(self, value):
        self._outputFile = value

    #readonly
    @property
    def allErrors(self):
        return self._allErrors
        
    @property
    def verbose(self):
        return self.verbose
        
    @verbose.setter
    def verbose(self, value):
        self._verbose = value