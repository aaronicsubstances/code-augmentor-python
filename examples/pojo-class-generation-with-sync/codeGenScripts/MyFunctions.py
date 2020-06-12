import os.path

import OtherFunctions

def theClassProps(augCode, context):
    context.fileScope['theClassProps'] = augCode.args[0]
    context.fileScope['theClassName'] = os.path.splitext(os.path.basename(context.fileAugCodes.relativePath))[0]
    out = ''
    for propSpec in context.fileScope['theClassProps']:
        out += f"private {propSpec.type} {propSpec.name};"
        out += augCode.lineSeparator
    return out

def generateClassProps(augCode, context):
    out = ''
    for propSpec in context.fileScope['theClassProps']:
        capitalized = propSpec.name.capitalize()
        out += f"public {propSpec.type} get{capitalized}()" + " {"
        out += augCode.lineSeparator
        out += f"{OtherFunctions.defaultIndent()}return {propSpec.name};"
        out += augCode.lineSeparator
        out += f"}}{augCode.lineSeparator}"
        out += f"public void set{capitalized}({propSpec.type} {propSpec.name})" + " {"
        out += augCode.lineSeparator
        out += f"{OtherFunctions.defaultIndent()}this.{propSpec.name} = {propSpec.name};"
        out += augCode.lineSeparator
        out += "}" + f"{augCode.lineSeparator}"
        out += augCode.lineSeparator
    return out

def generateEqualsAndHashCode(augCode, context):
    # don't override if empty.
    if not context.fileScope['theClassProps']:
        return ''
    
    out = ''
    
    # generate equals() override
    out += f"@Override{augCode.lineSeparator}"
    out += f"public boolean equals(Object obj) {{"
    out += augCode.lineSeparator
    out += f"{OtherFunctions.defaultIndent()}if (!(obj instanceof {context.fileScope['theClassName']})) {{"
    out += augCode.lineSeparator
    out += f"{OtherFunctions.defaultIndent()}{OtherFunctions.defaultIndent()}return false;"
    out += augCode.lineSeparator
    out += f"{OtherFunctions.defaultIndent()}" + '}'
    out += augCode.lineSeparator
    out += f"{OtherFunctions.defaultIndent()}{context.fileScope['theClassName']} other = ({context.fileScope['theClassName']}) obj;"
    out += augCode.lineSeparator
    
    for propSpec in context.fileScope['theClassProps']:
        if propSpec.type[0].isupper():
            out += OtherFunctions.defaultIndent()
            out += 'if (!Objects.equals(this.'
            out += propSpec.name
            out += ', other.' 
            out += propSpec.name
            out += ')) {'
        else:
            out += OtherFunctions.defaultIndent()
            out += 'if (this.'
            out += propSpec.name
            out += ' != other.' 
            out += propSpec.name
            out += ') {'
        out += augCode.lineSeparator
        out += f"{OtherFunctions.defaultIndent()}{OtherFunctions.defaultIndent()}return false;"
        out += augCode.lineSeparator
        out += OtherFunctions.defaultIndent() + '}'
        out += augCode.lineSeparator
    
    out += f"{OtherFunctions.defaultIndent()}return true;{augCode.lineSeparator}"
    out += '}'
    out += augCode.lineSeparator
    out += augCode.lineSeparator
    
    # generate hashCode() override with Objects.hashCode()
    out += f"@Override{augCode.lineSeparator}"
    out += "public int hashCode() {"
    out += augCode.lineSeparator
    if len(context.fileScope['theClassProps']) == 1:
        out += f"{OtherFunctions.defaultIndent()}return Objects.hashCode("
        out += context.fileScope['theClassProps'][0].name
    else:
        out += f"{OtherFunctions.defaultIndent()}return Objects.hash("
        for i in range(len(context.fileScope['theClassProps'])):
            if i > 0:
                out += ', '
            out += context.fileScope['theClassProps'][i].name

    out += f");{augCode.lineSeparator}"
    out += '}'
    out += augCode.lineSeparator
    return out

def generateToString(augCode, context):
    out = ''
    out += f"@Override{augCode.lineSeparator}"
    out += "public String toString() {"
    out += augCode.lineSeparator
    out += f"{OtherFunctions.defaultIndent()}return String.format(getClass().getSimpleName() + "
    exactOut = '"{'
    outArgs = ''
    for i in range(len(context.fileScope['theClassProps'])):
        if i > 0:
            exactOut += ', '
            outArgs += ', '
        exactOut += context.fileScope['theClassProps'][i].name + '=%s'
        outArgs += context.fileScope['theClassProps'][i].name
    exactOut += '}"'
    g = context.newGenCode()
    g.contentParts.append(context.newContent(out));
    g.contentParts.append(context.newContent(exactOut, True))
    out = ''
    if outArgs:
        out += ","
        out += augCode.lineSeparator
        out += OtherFunctions.defaultIndent()
        out += OtherFunctions.defaultIndent()
    out += outArgs
    out += f");{augCode.lineSeparator}"
    out += '}'
    out += augCode.lineSeparator
    g.contentParts.append(context.newContent(out))
    return g
