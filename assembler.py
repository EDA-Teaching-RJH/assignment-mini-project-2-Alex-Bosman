import re
import json

class assembler:
    def __init__(self, ISAData):
        self.RESERVEDWORDS = []
        self.SYMBOLS = []
        self.SYMBOLVALUES = {}
        self.program = []
        self.ISADATA = ISAData

        #temp
        self.ERRORLOG = []




    def assemble(self, program):
        self.program = program

        assemblyArray = self.preProcessing()
        tokenArray = self.lexicalAnalysis(assemblyArray)
        self.syntaxAndSemanticAnalysis(tokenArray)

        print(f"Errors: {self.ERRORLOG}")



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
        self.LITERALVALUES = {}

        # add all instructions, pseudoinstructions and any additional assembler reserved words to reserved word table
        self.RESERVEDWORDS = []
        self.RESERVEDWORDS += list(self.ISADATA["instructions"].keys()) # add instructions
        self.RESERVEDWORDS += [x.split()[0] for x in list(self.ISADATA["pseudoInstructions"].keys())] # add pseudoinstructions
        self.RESERVEDWORDS += [f"r{i:x}" for i in range(0, 16)] # add registers

        labelRegex = re.compile("^(\w+):$")
        literalRegex = re.compile("^.constant (\w+) (-\d+|\d+)$")
        registerReferenceRegex = re.compile("^.register (\w+) (r[0-9a-f])$")

        # iterate through and add all labels and literals to the symbols table
        # this is done so when assembling the code, any constant reference can be replaced with the actual value and any label can be replaced with location
        for line in assemblyArray:
            label = labelRegex.findall(line)
            literal = literalRegex.findall(line)
            registerReference = registerReferenceRegex.findall(line)
            if label != []:
                # check the label is not in the reserved words table or already exists
                if label[0] in self.SYMBOLS:
                    self.ERRORLOG.append(f"label is already defined: {label[0]}")
                elif label[0] in self.RESERVEDWORDS:
                    self.ERRORLOG.append(f"label is using a reserved keyword: {label[0]}")
                else:
                    self.SYMBOLS.append(label[0])
            if literal != []:
                if literal[0][0] in self.SYMBOLS:
                    self.ERRORLOG.append(f"literal is already defined: {literal[0]}")
                elif literal[0][0] in self.RESERVEDWORDS:
                    self.ERRORLOG.append(f"literal is using a reserved keyword: {literal[0]}")
                else:
                    self.SYMBOLS.append(literal[0][0])
                    self.SYMBOLVALUES[literal[0][0]] = literal[0][1]
            if registerReference != []:
                if registerReference[0][0] in self.SYMBOLS:
                    self.ERRORLOG.append(f"registerReference is already defined: {literal[0]}")
                elif registerReference[0][0] in self.RESERVEDWORDS:
                    self.ERRORLOG.append(f"registerReference is using a reserved keyword: {literal[0]}")
                else:
                    self.SYMBOLS.append(registerReference[0][0])
                    self.SYMBOLVALUES[registerReference[0][0]] = registerReference[0][1]

        # tokenise assemblyArray into tokenArray

        # create an array for tokens to be stored
        tokens = []

        # add the regex statements for any assember-specific features (e.g labels, constant definition statement etc)
        tokens.append(("label", labelRegex))
        tokens.append(("constant", literalRegex))
        tokens.append(("registerReference", registerReferenceRegex))

        # add the regex statements for all instructions
        for instruction in self.ISADATA["instructions"]:
            instructionType = self.ISADATA["instructions"][instruction]["instructionType"]
            match instructionType:
                # TODO - additional feature could pass these in with the ISA definitions - then user can also redefine these.
                case "typeA": tokens.append((instructionType, re.compile(f"^({instruction})$")))
                case "typeB": tokens.append((instructionType, re.compile(f"^({instruction}) (r[0-9a-f]|\w+)$")))
                case "typeC": tokens.append((instructionType, re.compile(f"^({instruction}) (r[0-9a-f]|\w+) (\d+|-\d+|\w+)$")))
                case "typeD": tokens.append((instructionType, re.compile(f"^({instruction}) (r[0-9a-f]|\w+) (r[0-9a-f]|\w+) (r[0-9a-f]|\w+)$")))
                case _: print("Error, unknown instruction type encountered - please check isa definitions.")

        # create an array for tokens to be stored
        tokenArray = []
        for line in assemblyArray:
            MATCHFLAG = False
            for token in tokens:
                if re.findall(token[1], line):
                    MATCHFLAG = True
                    break
            if MATCHFLAG:
                tokenArray.append((token[0], re.findall(token[1], line)[0]))
            else:
                print(f"Invalid instruction found: {line}")
                self.ERRORLOG.append(f"Invalid instruction found: {line}")
        

        return tokenArray
        #print(tokenArray)
        #print("")
        #print(self.LITERALVALUES)
        ##print(self.RESERVEDWORDS, self.SYMBOLS)
        







    def syntaxAndSemanticAnalysis(self, tokenArray):
        print(tokenArray)
        print(self.SYMBOLVALUES)
        # check if reserved word or symbol is being used as an operand
        # iterate through entire token array and make sure that all constants and labels are declared correctly
        # this can be done by using the reserved words and symbols tables
        # labels will be in typeC instruction  (will need to convert label to integer and also add extra branch statements if needed)
        # literals will only be in typeC (mif)
        # literals must be 0-255 or -128 to 127


        # check if reserved word or symbol is being used as an operand - effects typeC only (but only if register references not used - TODO)


        # now remove any assember only tokens apart from labels as about to assemble, e.g. literals
        tokenArray = [x for x in tokenArray if x[0] != "literal"]

    
        pass
    #### TODO - add feature to rename registers - cannot be constants



def main():
    with open("assembly.txt", "r") as file:
        program = file.readlines()
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    a.assemble(program)



if __name__ == __name__:
    main()