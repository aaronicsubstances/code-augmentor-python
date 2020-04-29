# models used with code augmentor are defined here.

class ProcessCodeContext:
    def __init__(self):
        self._header = None
        self._globalScope = {}
        self._fileScope = {}
        self._fileAugCodes = None
        self._augCodeIndex = 0
        self._srcFile = None

    # Intended for use by scripts
    def newGenCode(self):
        return GeneratedCode()

    # Intended for use by scripts
    def newContent(self, content, exactMatch=False):
        return ContentPart(content, exactMatch)
        
    @property
    def header(self):
        return self._header
        
    @header.setter
    def header(self, value):
        self._header = value

    #readonly
    @property
    def globalScope(self):
        return self._globalScope

    #readonly
    @property
    def fileScope(self):
        return self._fileScope
        
    @property
    def fileAugCodes(self):
        return self._fileAugCodes
    
    @fileAugCodes.setter
    def fileAugCodes(self, value):
        self._fileAugCodes = value
        
    @property
    def augCodeIndex(self):
        return self._augCodeIndex
        
    @augCodeIndex.setter
    def augCodeIndex(self, value):
       self._augCodeIndex = value
       
    @property
    def srcFile(self):
        return self._srcFile
        
    @srcFile.setter
    def srcFile(self, value):
        self._srcFile = value


class GeneratedCode:
    def __init__(self):
        self.id = 0
        self.contentParts = []
        self.indent = None
        self.skipped = False
        self.replaceAugCodeDirectives = False
        self.replaceGenCodeDirectives = False
        
    def toDict(self):
        contentPartsAsDicts = []
        for c in self.contentParts:
            contentPartsAsDicts.append({
                'content': c.content,
                'exactMatch': c.exactMatch
            })
        dictRepr = {
            'id': self.id,
            'contentParts': contentPartsAsDicts,
            'indent' : self.indent,
            'skipped': self.skipped,
            'replaceAugCodeDirectives': self.replaceAugCodeDirectives,
            'replaceGenCodeDirectives': self.replaceGenCodeDirectives
        }
        return dictRepr

class ContentPart:
    def __init__(self, content, exactMatch):
        self.content = content
        self.exactMatch = exactMatch

    def __str__(self):
        return f"ContentPart{{content={self.content}, exactMatch={self.exactMatch}}}"