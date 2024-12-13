import re
import json

class assembler:
    def __init__(self, ISAData):
        self.RESERVEDWORDS = []
        self.SYMBOLS = []
        self.REGISTERNAMES = []
        self.SYMBOLTYPES = {}
        self.SYMBOLVALUES = {}
        self.assemblerSpecificTokens = ("literal", "registerReference", "label")
        self.program = []
        self.ISADATA = ISAData

        #temp
        self.ERRORLOG = []




    def assemble(self, program):
        self.program = program

        assemblyArray = self.preProcessing()
        tokenArray = self.lexicalAnalysis(assemblyArray)
        absoluteValuesTokenArray = self.syntaxAndSemanticAnalysis(tokenArray)
        machineCode = self.codeGeneration(absoluteValuesTokenArray)
        print(machineCode)

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
        self.SYMBOLTYPES = {}
        self.LITERALVALUES = {}

        # add all instructions, pseudoinstructions and any additional assembler reserved words to reserved word table
        self.RESERVEDWORDS = []
        self.RESERVEDWORDS += list(self.ISADATA["instructions"].keys()) # add instructions
        self.RESERVEDWORDS += [x.split()[0] for x in list(self.ISADATA["pseudoInstructions"].keys())] # add pseudoinstructions
        self.RESERVEDWORDS += [f"r{i:x}" for i in range(0, 16)] # add registers
        self.REGISTERNAMES = [f"r{i:x}" for i in range(0, 16)] # add registers to registername array (for syntax and semantic checking)

        labelRegex = re.compile("^([A-Za-z]|[A-Za-z]\w+):$")
        literalRegex = re.compile("^.define ([A-Za-z]|[A-Za-z]\w+) (-\d+|\d+)$")
        registerReferenceRegex = re.compile("^.register ([A-Za-z]|[A-Za-z]\w+) (r[0-9a-f])$")

        # iterate through and add all labels and literals to the symbols table
        # this is done so when assembling the code, any literal reference can be replaced with the actual value and any label can be replaced with location
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
                    self.SYMBOLTYPES[label[0]] = "label"

            if literal != []:
                if literal[0][0] in self.SYMBOLS:
                    self.ERRORLOG.append(f"literal is already defined: {literal[0]}")
                elif literal[0][0] in self.RESERVEDWORDS:
                    self.ERRORLOG.append(f"literal is using a reserved keyword: {literal[0]}")
                else:
                    self.SYMBOLS.append(literal[0][0])
                    self.SYMBOLTYPES[literal[0][0]] = "literal"
                    self.SYMBOLVALUES[literal[0][0]] = literal[0][1]

            if registerReference != []:
                if registerReference[0][0] in self.SYMBOLS:
                    self.ERRORLOG.append(f"registerReference is already defined: {literal[0]}")
                elif registerReference[0][0] in self.RESERVEDWORDS:
                    self.ERRORLOG.append(f"registerReference is using a reserved keyword: {literal[0]}")
                else:
                    self.SYMBOLS.append(registerReference[0][0])
                    self.SYMBOLTYPES[registerReference[0][0]] = "registerReference"
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
        
        there are also some special types of argument that will be recognised by the assembler.
        type 'opcode' does not need to be listed. This will automatically be replaced by the corresponding opcode
        type 'immediate' will be substituted with a literal value (can either be the literal definition or just the literal)
        type 'register' will be substituted with a register value (can either be register rename definition or just the register)
        type 'blank' will mean there is no argument
        these special types will still follow the bit size requirement of the file
        '''

        # create an array for tokens to be stored
        tokens = []

        # add the regex statements for any assember-specific features (e.g labels, literal definition statement etc)
        tokens.append(("label", labelRegex))
        tokens.append(("literal", literalRegex))
        tokens.append(("registerReference", registerReferenceRegex))


        # add the regex statements for all instructions
        # fetch the instruction types
        instructionTypes = self.ISADATA["instructionTypes"]
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


        # remove any assember specific tokens apart from labels as about to assemble, e.g. literal definitions, register rename definitions etc.
        tokenArray = [x for x in tokenArray if ((x[0] not in self.assemblerSpecificTokens) or (x[0] == "label"))]

        # fetch the instruction types
        instructionTypes = self.ISADATA["instructionTypes"]

        # check all instructions to make sure literals and register renames are being used in the correct place
        # literals must only be used for 'immediate' type operands, nothing else
        # register renames must only be used for 'register' type operands, nothing else
        ###self.assemblerSpecif = ["literal", "registerReference", "label"]

        absoluteValuesTokenArray = []
        for token in tokenArray:
            
            if token[0] not in self.assemblerSpecificTokens:
                # get the arguments for the specific instruction
                arguments = instructionTypes[token[0]]
                # iterate through each instruction argument and check that it is correct if it is an assembler specific argument
                # opcode will always be correct (matched in regex) so does not need to be checked
                # if argument = 'register' then make sure instruction actually uses a register - not a label or literal etc
                # if argument = 'immediate' then make sure instruction actually uses an immediate - not a label or register etc.
                # if argument = 'blank' or 'opcode' then skip
                absoluteToken = []
                for index, argument in enumerate(arguments):
                    if argument == "blank":
                        absoluteToken.append(0)
                    elif argument == "opcode":
                        if type(token[1]) is tuple:
                            absoluteToken.append(token[1][index])
                        else:
                            absoluteToken.append(token[1])
                        # TODO - this if statement will be removed in future revisions as unfortunately I ran out of time to complete the project so comprimised with this.
                        # I planned to do a re-write for the pseudoinstructions so you could have proper branching statements 
                        # however, I ran out of time so the program currently only works for isaV4_definitions and wont work with other instruction sets until i fix this.
                        # I have hardcoded isa_v4 mnemonics so I could still get branch to label functionality
                        # in the future this would be replaced by pseudoinstructions so that any instruction set could have branch to label, not just isa_v4
                        # check out isaV4_definitions_future.json to see the potential pseudoinstruction re-write
                        # this would also allow you to add in operands instead of just being fixed as well.
                        branchMnemonics = ("brh", "bie", "bge", "bil")
                        if token[1][index] in branchMnemonics:
                            for index, argumentb in enumerate(token[1]):
                                if index == 0:
                                    continue
                                elif index == 1:
                                    if token[1][index] in self.SYMBOLTYPES.keys():
                                        if self.SYMBOLTYPES[token[1][index]] == "registerReference":
                                            absoluteToken.append(int(f"0x{self.SYMBOLVALUES[argumentb[1:]]}", 16))
                                        else:
                                            self.ERRORLOG.append(f"(reg) invalid operand used: {token}")
                                    elif token[1][index] in self.REGISTERNAMES:
                                        absoluteToken.append(int(f"0x{argumentb[1:]}", 16))
                                    else:
                                        self.ERRORLOG.append(f"(reg) undefined operand found: {token}")
                                elif index == 2:
                                    # check if valid label
                                    if self.SYMBOLTYPES[token[1][index]] == "label":
                                        absoluteToken.append(argumentb)
                                    else:
                                        self.ERRORLOG.append(f"undefined label found: {token}")
                                else:
                                    self.ERRORLOG.append(f"undefined operand found: {token}")
                                    
                            break
                        else:
                            continue
                    elif (argument == "register") and (token[1][index] in self.SYMBOLTYPES.keys()):
                        # check if symbol used is actually a register
                        if self.SYMBOLTYPES[token[1][index]] == "registerReference":
                            # TODO - check if value is in valid register range
                            # also need to fix this
                            absoluteToken.append(int(f"0x{self.SYMBOLVALUES[token[1][index]][1:]}", 16))
                        else:
                            self.ERRORLOG.append(f"(reg) invalid operand used: {token}")

                    elif (argument == "immediate") and (token[1][index] in self.SYMBOLTYPES.keys()):
                        # check if symbol used is actually an immediate
                        if self.SYMBOLTYPES[token[1][index]] == "literal":
                            absoluteToken.append(self.SYMBOLVALUES[token[1][index]])
                        else:
                            self.ERRORLOG.append(f"(imm) invalid operand used: {token}")

                    elif (argument == "register") and (token[1][index] in self.REGISTERNAMES):
                        # must be a valid register
                        # TODO - temporary, will fix in future version
                        absoluteToken.append(int(f"0x{token[1][index][1:]}", 16))


                    elif (argument == "immediate") and (token[1][index].isdigit()):
                        # check if within range
                        bitNumber = self.ISADATA["assemblyTypeLengths"]["immediate"]
                        # TODO - THIS NEEDS TO BE FIXED!
                        if int(token[1][index]) <= (bitNumber ** 2) - 1:
                            absoluteToken.append(token[1][index])
                        else:
                            self.ERRORLOG.append(f"value not in range: {token}")

                    else:
                        self.ERRORLOG.append(f"undefined operand found: {token}")
                absoluteValuesTokenArray.append(absoluteToken)
            else:
                absoluteValuesTokenArray.append(token)


        return absoluteValuesTokenArray



    def codeGeneration(self, absoluteValuesTokenArray):
        print(absoluteValuesTokenArray)

        currentLine = 0
        labelLine = {}
        instructionLength = self.ISADATA["instructionLength"]
        assemblyTypeLengths = self.ISADATA["assemblyTypeLengths"]
        branchMnemonics = ("brh", "bie", "bge", "bil")


        lineNumberArrayTests = [currentLine]

        # first pass - gets the line number for all labels
        for instruction in absoluteValuesTokenArray:

            if instruction[0] in branchMnemonics:
                if instruction[0] == "brh":
                    length = 32
                    ### assembly for brh label instruction
                    # mif re label(upper 8 bits); load the upper pointer of the label - 16 bits
                    # brh re label(lower 8 bits); branch (with lower 8 bits as immediate) - 16 bits
                else:
                    length = 72
                    ### assembly for bie and other types of indirect branch
                    # bie r(register specified) +3;if true then go to main branching statement, if false go to next line (which will also skip past the main branching statement) - 16 bits
                    # mfa r0; move 0 to accumulator so can indirect branch - 8 bits 
                    # bie r0 +5; branch was false so indirect branch (if r0 == 0 which evaluates to True) to offset where code continues - 16 bits
                    # mif re label(upper 8 bits); load the upper pointer of the label - 16 bits
                    # brh re label(lower 8 bits) - 16 bits

                currentLine += -(-length // instructionLength)

            elif instruction[0] == "label":
                labelLine[instruction[1]] = currentLine
                
            else:
                currentinstructionType = self.ISADATA["instructions"][instruction[0]]["instructionType"]
                length = 0
                for x in self.ISADATA["instructionTypes"][currentinstructionType]:
                    length += assemblyTypeLengths[x]
                currentLine += -(-length // instructionLength)

            # TODO remove this array - testing for seeing how many line numbers there are
            lineNumberArrayTests.append(currentLine)

        
        # labels can now be removed
        absoluteValuesTokenArray = [x for x in absoluteValuesTokenArray if x[0] != "label"]
        print(labelLine)
        print(lineNumberArrayTests)

        print(absoluteValuesTokenArray)

        #print(labelLine)
        #print(lineNumberArrayTests)    

        # second pass - replace all label references with actual values (will generate extra lines of assembly due to branches technically being pseudoinstructions)
        # also change all operands into machine code because why not lol
        # change opcodes into machine code as well
        assembleCodeArray = []
        line = "0b"
        for instruction in absoluteValuesTokenArray:
            for index, argument in enumerate(instruction):
                if argument in self.ISADATA["instructions"].keys():
                    if argument in branchMnemonics:
                        line == ""
                        print(instruction)
                        if argument == "brh":
                            # register value gets ignored, just branch based off of label
                            # this is because I ran out of time so could not implement proper branching + branching with labels
                            # so unfortunately still need to reference a register value in assembly, even though its useless
                            # this is really stupid but I need to commit to it due to time contraints lol
                            # the whole way the branching is handled is stupid - could have been an easy fix if I just took the time to revamp custom pseudoinstructions
                            lineValue = format(labelLine[instruction[2]], "016b")
                            upperPointer = lineValue[8:]
                            lowerPointer = lineValue[:8]
                            assembleCodeArray += ["0b00101110", f"0b{upperPointer}"] # mif re label(upper 8 bits); load the upper pointer of the label - 16 bits
                            assembleCodeArray += ["0b11001110", f"0b{lowerPointer}"] # brh re label(lower 8 bits); branch (with lower 8 bits as immediate) - 16 bits
                            break

                        elif argument == "bil":
                            lineValue = format(labelLine[instruction[2]], "016b")
                            upperPointer = lineValue[8:]
                            lowerPointer = lineValue[:8]
                            register = format(int(instruction[1]), "04b")
                            assembleCodeArray += [f"0b1101{register}", "0b00000010"] # bil r(register specified) +3;if true then go to main branching statement, if false go to next line (which will also skip past the main branching statement) - 16
                            assembleCodeArray += ["0b11010000" "0b00000101"] # bie r0 +5; branch was false so indirect branch (if r0 = r0) to offset where code continues - 16
                            assembleCodeArray += ["0b00101110", f"0b{upperPointer}"] # mif re label(upper 8 bits); load the upper pointer of the label - 16 bits
                            assembleCodeArray += ["0b11001110", f"0b{lowerPointer}"] # brh re label(lower 8 bits) - 16 bits
                            break

                        elif argument == "bge":
                            lineValue = format(labelLine[instruction[2]], "016b")
                            upperPointer = lineValue[8:]
                            lowerPointer = lineValue[:8]
                            register = format(int(instruction[1]), "04b")
                            assembleCodeArray += [f"0b1101{register}", "0b00000010"] # bil r(register specified) +3;if true then go to main branching statement, if false go to next line (which will also skip past the main branching statement) - 16
                            assembleCodeArray += ["0b11010000" "0b00000101"] # bie r0 +5; branch was false so indirect branch (if r0 = r0) to offset where code continues - 16
                            assembleCodeArray += ["0b00101110", f"0b{upperPointer}"] # mif re label(upper 8 bits); load the upper pointer of the label - 16 bits
                            assembleCodeArray += ["0b11001110", f"0b{lowerPointer}"] # brh re label(lower 8 bits) - 16 bits
                            break

                        elif argument == "bie":
                            lineValue = format(labelLine[instruction[2]], "016b")
                            upperPointer = lineValue[8:]
                            lowerPointer = lineValue[:8]
                            register = format(int(instruction[1]), "04b")
                            assembleCodeArray += [f"0b1110{register}", "0b00000010"] # bge r(register specified) +3;if true then go to main branching statement, if false go to next line (which will also skip past the main branching statement) - 16
                            assembleCodeArray += ["0b11110000" "0b00000101"] # bie r0 +5; branch was false so indirect branch (if r0 = r0) to offset where code continues - 16
                            assembleCodeArray += ["0b00101110", f"0b{upperPointer}"] # mif re label(upper 8 bits); load the upper pointer of the label - 16 bits
                            assembleCodeArray += ["0b11001110", f"0b{lowerPointer}"] # brh re label(lower 8 bits) - 16 bits
                            break

                    else:
                        line += self.ISADATA["instructions"][instruction[0]]["opcode"]
                else:
                    # convert number to machine code
                    # TODO - need to check size
                    line += format(int(argument), "04b")
                    print(argument, format(int(argument), "04b"))

            if line != "":
                assembleCodeArray.append(line)

                    

        

        # second pass - replaces all assembly with machine code
        # also swap out branch instruction assembly with correct values (will generate extra lines of assembly)


        #instructionTypes = self.ISADATA["instructionTypes"]
        #machineCodeArray = []

        #for token in absoluteValuesTokenArray:
        #    arguments = instructionTypes[""]
        #    for index, argument in enumerate(arguments):
        #        print(argument)
                



        '''
        instructions = self.ISADATA["instructions"]
        machineCodeArray = []
        for instruction in absoluteValuesTokenArray:
            instructionMachineCode = ""
            for argument in instruction:
                print(argument)
                if argument in self.ISADATA["instructions"]:
                    print("must be opcode")
                    instructionMachineCode += self.ISADATA["instructions"][argument]["opcode"]
                elif argument in labelLine.keys():
                    print("must be an assembler identifier")
                    instructionMachineCode += "{0:010b}".format(labelLine[argument])
                    #bitNumber = self.ISADATA["assemblyTypeLengths"]["immediate"]
                else:
                    print("unrec")

            machineCodeArray.append(instructionMachineCode)
        print("")
        print(machineCodeArray)
        '''



        return ["a"]

       





def main():
    with open("assembly.txt", "r") as file:
        program = file.readlines()
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    a.assemble(program)



if __name__ == __name__:
    main()