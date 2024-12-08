import re
import json

class assembler:
    def __init__(self, ISAData):
        self.RESERVEDWORDS = []
        self.SYMBOLS = []
        self.program = []
        self.ISADATA = ISAData




    def assemble(self, program):
        self.program = program

        assemblyArray = self.preProcessing()

        print(assemblyArray)

        self.lexicalAnalysis(assemblyArray)

        self.syntaxAnalysis(assemblyArray)



    def preProcessing(self):
        # preprocessing
        # remove all blank lines, comments and whitespaces
        cleanedArray = [x.split(";")[0].strip().casefold() for x in self.program if x.split(";")[0].strip().casefold() != ""]

        # a pseudo-instruction is an instruction provided by the assembler that will get translated into multiple other real instructions
        # these instructions do not translate directly into machine code so must be translated into multiple normal instructions first
        # get regex definitions for all pseudo-instructions
        #pseudoInstruction
        pseudoInstructions = [(x, re.compile(f"^{x}$"), self.ISADATA["pseudoInstructions"][x]) for x in self.ISADATA["pseudoInstructions"]]

        print("")
        print(pseudoInstructions)
        print("")

        assemblyArray = []
        for index, line in enumerate(cleanedArray):
            MATCHFLAG = False
            for x in pseudoInstructions:
                if re.findall(x[1], line):
                    substitution = x[2]
                    MATCHFLAG = True
                    break
            if MATCHFLAG:
                assemblyArray += substitution
                print("a pseudoInstruction found")
            else:
                assemblyArray.append(line)
        print(assemblyArray)
        print("")

        return assemblyArray


    def lexicalAnalysis(self, assemblyArray):
        # clear symbols and reserved words tables
        # first create a reserved word table (syntax and any word reserved by the assembler and also macros)
        # also create a symbols table (any user defined labels or literals)
        self.RESERVEDWORDS = []
        self.SYMBOLS = []
        print(self.ISADATA["instructions"])


        labelRegex = re.compile("^\w+:$")
        literalRegex = re.compile("^#define (\w+) (-\d+|\d+)$")
        
        # iterate through and add all labels and literals to the symbols table
        for index, line in enumerate(assemblyArray):
            label = labelRegex.search(line)
            literal = literalRegex.search(line)
            if label is not None:
                self.SYMBOLS.append((index, label))
            if literal is not None:
                self.SYMBOLS.append((index, literal))
        #print(self.SYMBOLS)



    def syntaxAnalysis(self, assemblyArray):
        pass


def main():
    with open("assembly.txt", "r") as file:
        program = file.readlines()
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    
    a = assembler(instructionInfo)
    a.assemble(program)
    #assemble(assemblyArray)


if __name__ == __name__:
    main()