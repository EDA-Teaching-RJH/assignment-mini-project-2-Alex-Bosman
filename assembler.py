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
        '''
        this next part of code tokenizes each line of code
        it first generates a table of regular expressions for every possible statement
        this will include assembler features like defining labels. this will also include instructions
        it also contains a kinda complicated way of allowing support for future instruction sets
        each instruction will have a type - this is a particular format the instruction follows
        a lot of instructions will follow the same format so can share the same type
        the type will always need an opcode. This can then optionally be followed with arguments such as register locations, immediate values etc
        the argument regular expressions must be defined in assemblyTypes. The length of these arguments in bits also must be defined in assemblyTypeLengths
        the program will iterate through all the possible in
        '''

        # create an array for tokens to be stored
        tokens = []

        # add the regex statements for any assember-specific features (e.g labels, constant definition statement etc)
        tokens.append(("label", labelRegex))
        tokens.append(("constant", literalRegex))
        tokens.append(("registerReference", registerReferenceRegex))


        # add the regex statements for all instructions
        # fetch the instruction types
        instructionTypes = self.ISADATA["InstructionTypes"]
        print(instructionTypes)
        # now fetch the assembly type regex statements
        assemblyTypes = self.ISADATA["assemblyTypes"]
        # loop through all the defined instructions and create a token for them using defined instruction types and features
        for instruction in self.ISADATA["instructions"]:
            # first fetch the current instruction type from the definitions file
            currentInstructionType = self.ISADATA["instructions"][instruction]["instructionType"]
            # now set a defined flag to be false - this will be set to true if the json file also included the corresponding definitions for the regex
            INSTRUCTIONDEFINEDFLAG = False
            # now iterate through all instructiontypes to see if there is a match between the listed ones and the current one
            for instructionType in instructionTypes:
                # if there is a match, start creating the regular expression
                # if there is no match then continue checking
                if currentInstructionType == instructionType:
                    # create the start of the string - the character ^ matches from the beginning of the given string
                    instructionString = "^"
                    # iterate through the instruction type to match all the statements - e.g get regex for a 'register', get regex for an 'immediate' etc
                    for statement in instructionTypes[instructionType]:
                        # if the statement was an opcode the regex can be set as the corresponding meumonic
                        if statement == "opcode":
                            instructionString += f"({instruction}) "
                        else:
                            # if the regex string is blank then do not add anything to the regex string
                            # of it is not blank then add the corresponding regex to the regex string
                            if assemblyTypes[statement] != "":
                                instructionString += f"({assemblyTypes[statement]}) "
                

                    # spaces are used to seperate operands but the last space must be removed so it does not get matched.
                    instructionString = instructionString[:-1]
                    # now add the end of the statement
                    instructionString += "$"
                    # finally, add the token to the token array
                    tokens.append((instructionType, re.compile(instructionString)))
                    # set the instruction defined flag to true - this will only not be set if the instruction type is not defined.
                    INSTRUCTIONDEFINEDFLAG = True
                    break
                    
            if not INSTRUCTIONDEFINEDFLAG:
                self.ERRORLOG.append(f"Error, unknown instruction type encountered - please check isa definitions: {currentInstructionType}")


        # create an array for tokens to be stored
        tokenArray = []
        # iterate through the assembly array and tokenize every instruction and assembler feature
        for line in assemblyArray:
            # set the token match flag to false
            MATCHFLAG = False
            # iterate through the token array and see if any of the regex matches with the current line
            for token in tokens:
                # if the regex matches then set the flag to true
                if re.findall(token[1], line):
                    MATCHFLAG = True
                    break
            if MATCHFLAG:
                # if the regex matches then tokenize the line with the particular regex statement
                tokenArray.append((token[0], re.findall(token[1], line)[0]))
            else:
                # if the current line does not match any possible token regex then it must be invalid - add a corresponding error message
                self.ERRORLOG.append(f"Invalid instruction found: {line}")
        

        return tokenArray



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