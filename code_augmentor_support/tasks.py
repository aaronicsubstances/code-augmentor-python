import json
import os
import os.path
import sys
import traceback

from .models import ProcessCodeContext, GeneratedCode, ContentPart

def compactJsonDump(obj):
    return json.dumps(obj, separators=(',', ':'))

class ProcessCodeTask:
    def __init__(self):
        self._inputFile = None
        self._outputFile = None
        self._verbose = True
        self._allErrors = []
                
        
    def execute(self, evalFunction):
        self._allErrors.clear()
        
        # ensure dir exists for outputFile
        os.makedirs(os.path.dirname(self._outputFile), exist_ok=True)
        
        context = ProcessCodeContext()
        
        with open(self._inputFile, 'r', encoding='utf-8') as codeGenRequest,\
                open(self._outputFile, 'w', encoding='utf-8') as codeGenResponse:
            # begin serialize by writing header to output    
            codeGenResponse.write("{}\n")
            
            headerSeen = False
            for line in codeGenRequest:
                # begin deserialize by reading header from input
                if not headerSeen:
                    context.header = json.loads(line)
                    headerSeen = True
                    continue
                    
                fileAugCodes = json.loads(line)
                
                # set up context.
                context.srcFile = os.path.join(fileAugCodes['dir'],
                    fileAugCodes['relativePath'])
                context.fileAugCodes = fileAugCodes
                context.fileScope.clear()
                self.logVerbose("Processing {0}", context.srcFile)
                
                # fetch arguments and parse any json arguments found
                fileAugCodesList = fileAugCodes['augmentingCodes']
                for augCode in fileAugCodesList:
                    augCode['processed'] = False
                    augCode['args'] = []
                    for block in augCode['blocks']:
                        if block['jsonify']:
                            parsedArg = json.loads(block['content'])
                            augCode['args'].append(parsedArg)
                        elif block['stringify']:
                            augCode['args'].append(block['content'])
                
                # process aug codes            
                fileGenCodeList = []
                fileGenCodes = {
                    'fileId': fileAugCodes['fileId'],
                    'generatedCodes': fileGenCodeList
                }
                beginErrorCount = len(self._allErrors)
                for i in range(len(fileAugCodesList)):
                    augCode = fileAugCodesList[i]
                    if augCode['processed']:
                        continue
                        
                    context.augCodeIndex = i
                    functionName = augCode['blocks'][0]['content'].strip()
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
    
    def _processAugCode(self, evalFunction, functionName, augCode, context):
        try:
            result = evalFunction(functionName, augCode, context)
            
            if result == None:
                return []
            converted = []
            if isinstance(result, (list, tuple, set)):
                for item in result:
                    converted.append(self._convertGenCodeItem(item))
            else:
                genCode = self._convertGenCodeItem(result)
                genCode['id'] = augCode['id']
                converted.append(genCode)
            return converted
        except BaseException as evalEx:
            self._createException(context, None, sys.exc_info() )
            return []

    def _convertGenCodeItem(self, item):
        if item == None:
            genCode = GeneratedCode()
        elif isinstance(item, GeneratedCode):
            genCode = item
        elif isinstance(item, ContentPart):
            genCode = GeneratedCode()
            genCode.contentParts.append(item)
        else:
            genCode = GeneratedCode()
            genCode.contentParts.append(ContentPart(str(item), False))
        return genCode.toDict()
        
    def _validateGeneratedCodeIds(self, genCodes, context):
        ids = [x['id'] for x in genCodes]
        if [x for x in ids if x <= 0]:
            self._createException(context, 'At least one generated code id was not set. Found: ' + str(ids))
        elif len(set(ids)) < len(ids):
            self._createException(context, 'Generated code ids must be unique, but found duplicates: ' + str(ids))            
    
    def _createException(self, context, message, evalExInfo=None):
        lineMessage = ''
        stackTrace = ''
        if evalExInfo:
            augCode = context.fileAugCodes['augmentingCodes'][context.augCodeIndex]
            lineMessage = F" at line {augCode['lineNumber']}"
            message = "{0}: {1}".format(augCode['blocks'][0]['content'], 
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