import re

'''
reservedWords = ("maf", "mfa", "mif", "mfr", "mrf")
reservedWordsFormatted = "".join([("\\b{x}\\b|".format(x=data) if index != len(reservedWords)-1 else "\\b{x}\\b".format(x=data)) for index, data in enumerate(reservedWords)])

print(reservedWordsFormatted)
print(f"^(maf) (\\br[0-9a-f]\\b|(?!(?:{reservedWordsFormatted}))\w+)$")
'''

def loadInstructionDefinitions(definitionsArray):
    pass

def assemble(assemblyArray):

    ## preprocessing

    # remove all blank lines, comments and whitespaces
    assemblyArray = [x.split(";")[0].strip().casefold() for x in assemblyArray if x.split(";")[0].strip().casefold() != ""]

    print(assemblyArray)

    lexicalAnalysis(assemblyArray)
    #pattern = re.compile("^(lrs)$")


def lexicalAnalysis(assemblyArray):
    # first create a reserved word table (syntax and any word reserved by the assembler)
    RESERVEDWORDS = ()
    # also create a symbols table (any user defined labels or literals)
    SYMBOLS = []

    labelRegex = re.compile("^\w+:$")
    literalRegex = re.compile("^#define (\w+) (-\d+|\d+)$")
    
    # iterate through and add all labels and literals to the symbols table
    for index, line in enumerate(assemblyArray):
        label = labelRegex.search(line)
        literal = literalRegex.search(line)
        if label is not None:
            SYMBOLS.append((index, label))
        if literal is not None:
            SYMBOLS.append((index, literal))

    print(SYMBOLS)



def main():
    with open("assembly.txt", "r") as file:
        assemblyArray = file.readlines()
        #print(assemblyArray)
        assemble(assemblyArray)


if __name__ == __name__:
    main()