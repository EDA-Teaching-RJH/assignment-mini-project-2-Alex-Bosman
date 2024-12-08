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

        print(self.RESERVEDWORDS)
        print(self.SYMBOLS)

        self.syntaxAnalysis(assemblyArray)



    def preProcessing(self):
        # remove all blank lines, comments and whitespaces
        cleanedArray = [x.split(";")[0].strip().casefold() for x in self.program if x.split(";")[0].strip().casefold() != ""]

        # replace pseudo-instructions with standard instructions
        # a pseudo-instruction is an instruction provided by the assembler that will get translated into multiple other real instructions
        # these instructions do not translate directly into machine code so must be translated into multiple normal instructions first

        # get regex definitions for all pseudo-instructions
        pseudoInstructions = [(x, re.compile(f"^{x}$"), self.ISADATA["pseudoInstructions"][x]) for x in self.ISADATA["pseudoInstructions"]]

        # create an array for the output assembly
        assemblyArray = []
        # loop through the cleanedArray
        for line in cleanedArray:
            # set the matchflag to false as new iteration
            MATCHFLAG = False
            # if the current line is a pseudoinstruction, set the matchflag and also set the substitution assembly
            for x in pseudoInstructions:
                if re.findall(x[1], line):
                    substitution = x[2]
                    MATCHFLAG = True
                    break
            if MATCHFLAG:
                # concatinate the substitution array of instructions with the assemblyArray
                assemblyArray += substitution
            else:
                # else if no pseudo-instruction found then just append the regular instruction
                assemblyArray.append(line)

        return assemblyArray


    def lexicalAnalysis(self, assemblyArray):
        # first create a reserved word table (syntax and any word reserved by the assembler and also macros)
        # also create a symbols table (any user defined labels or literals)
        self.RESERVEDWORDS = []
        self.SYMBOLS = []

        # add all instructions, pseudoinstructions and any additional assembler reserved words to reserved word table
        self.RESERVEDWORDS = []
        self.RESERVEDWORDS += list(self.ISADATA["instructions"].keys()) # add instructions
        self.RESERVEDWORDS += [x.split()[0] for x in list(self.ISADATA["pseudoInstructions"].keys())] # add pseudoinstructions
        self.RESERVEDWORDS += [f"r{i:x}" for i in range(0, 16)] # add registers

        labelRegex = re.compile("^\w+:$")
        literalRegex = re.compile("^#define (\w+) (-\d+|\d+)$")

        # iterate through and add all labels and literals to the symbols table
        # this is done so when assembling the code, any constant reference can be replaced with the actual value and any label can be replaced with location
        for index, line in enumerate(assemblyArray):
            label = labelRegex.search(line)
            literal = literalRegex.search(line)
            if label is not None:
                self.SYMBOLS.append((index, label))
            if literal is not None:
                self.SYMBOLS.append((index, literal))

        # tokenise assemblyArray into tokenArray

        #^\w+:$
        #^({opcode})$
        #^(opcode) (r[0-9a-f]|\w+)$
        #^(opcode) (r[0-9a-f]|\w+) (\d+|-\d+|\w+)$
        #^(opcode) (r[0-9a-f]|\w+) (r[0-9a-f]|\w+) (r[0-9a-f]|\w+)$


        # token format
        # (tokentype, )

        tokens = []
        tokens.append(labelRegex)
        tokens.append(literalRegex)
        for instruction in self.ISADATA["instructions"]:
            instructionType = self.ISADATA["instructions"][instruction]["instructionType"]
            match instructionType:
                case "typeA": tokens.append(re.compile(f"^({instruction})$"))
                case "typeB": tokens.append(re.compile(f"^({instruction}) (r[0-9a-f]|\w+)$"))
                case "typeC": tokens.append(re.compile(f"^({instruction}) (r[0-9a-f]|\w+) (\d+|-\d+|\w+)$"))
                case "typeD": tokens.append(re.compile(f"^({instruction}) (r[0-9a-f]|\w+) (r[0-9a-f]|\w+) (r[0-9a-f]|\w+)$"))
                case _: print("Error, unknown instruction type encountered.")

        tokenArray = []
#        for index, value in enumerate(assemblyArray):
#            for x in 
#            print(re.findall(tokens[0], assemblyArray[index]))

        for line in assemblyArray:
            MATCHFLAG = False
            for token in tokens:
                if re.findall(token, line):
                    MATCHFLAG = True
                    break
            if MATCHFLAG:
                tokenArray.append((token, re.findall(token, line)))
            else:
                print(f"Invalid instruction found: {line}")

        print("")
        print(tokenArray)
        print("")



    def syntaxAnalysis(self, assemblyArray):
        pass




def main():
    with open("assembly.txt", "r") as file:
        program = file.readlines()
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    a.assemble(program)



if __name__ == __name__:
    main()