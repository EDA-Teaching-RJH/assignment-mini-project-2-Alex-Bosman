from assembler import assembler
import json

# run tests by typing in pytest into console

'''
test breakdown:
1) tests for all instructions
2) tests assembler features such as labels, constants, register renaming etc.
3) test some erroneous data
'''



# test every single instruction to see if they can be assembled properly

def test_instruction_maf():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"maf r{format(reg, 'x')}"]
        validMachineCode = [f"0b0000{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode


def test_instruction_mfa():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"mfa r{format(reg, 'x')}"]
        validMachineCode = [f"0b0001{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode


def test_instruction_mif():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(1, 16):
        for integer in range(0, 255):
            program = [f"mif r{format(reg, 'x')} {integer}"]
            print(program)
            validMachineCode = [f"0b0010{format(reg, '04b')}\n", f"0b{format(integer, '08b')}\n"]
            generatedMachineCode = a.assemble(program)
            assert validMachineCode == generatedMachineCode


def test_instruction_mfr():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    # just a simple test as testing every memory location would take years lol
    program = [f"mfr r1 r2 r3"]
    validMachineCode = ["0b00110001\n", "0b00100011\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_mrf():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    # just a simple test as testing every memory location would take years lol
    program = [f"mrf r1 r2 r3"]
    validMachineCode = ["0b01000001\n", "0b00100011\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_add():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"add r{format(reg, 'x')}"]
        validMachineCode = [f"0b0101{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode


def test_instruction_sub():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"sub r{format(reg, 'x')}"]
        validMachineCode = [f"0b0110{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode


def test_instruction_ior():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"ior r{format(reg, 'x')}"]
        validMachineCode = [f"0b0111{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode


def test_instruction_xor():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"xor r{format(reg, 'x')}"]
        validMachineCode = [f"0b1000{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode


def test_instruction_and():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    for reg in range(16):
        program = [f"and r{format(reg, 'x')}"]
        validMachineCode = [f"0b1001{format(reg, '04b')}\n"]

        generatedMachineCode = a.assemble(program)
        assert validMachineCode == generatedMachineCode



def test_instruction_inc():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)


    program = [f"inc"]
    validMachineCode = ["0b10100000\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_lrs():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = [f"lrs"]
    validMachineCode = ["0b10110000\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_brh():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = ["labelhere:", "brh r0 labelhere"]
    validMachineCode = ["0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000000\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_bil():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = ["labelhere:", "bil r3 labelhere"]
    validMachineCode = ["0b11010011\n", "0b00000011\n", "0b11100000\n", "0b00000101\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000000\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_bge():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = ["labelhere:", "bge r3 labelhere"]
    validMachineCode = ["0b11100011\n", "0b00000011\n", "0b11100000\n", "0b00000101\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000000\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_instruction_bie():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = ["labelhere:", "bie r3 labelhere"]
    validMachineCode = ["0b11110011\n", "0b00000011\n", "0b11100000\n", "0b00000101\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000000\n"]

    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


# tests for assembler features such as labels, constants, register renaming etc.

def test_assembler_label():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = ["startLabel:", "lrs", "lrs", "branchLabel:", "bie r3 startLabel", "brh r0 branchLabel"]
    validMachineCode = ["0b10110000\n", "0b10110000\n", "0b11110011\n", "0b00000011\n", "0b11100000\n", "0b00000101\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000000\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000010\n"]
    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_assembler_constant():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = [".define constant1 39", "mif r3 constant1"]
    validMachineCode = ["0b00100011\n", "0b00100111\n"]
    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode 


def test_assembler_registerRename():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = [".register registerBallX r5", "mif registerBallX 39"]
    validMachineCode = ["0b00100101\n", "0b00100111\n"]
    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode 


def test_assembler_comments():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)

    program = ["startLabel:;comment on label", "lrs; logical right shift", ";blank line comment", "lrs", "branchLabel:", "bie r3 startLabel     ; branch if equal to acc", "brh r0 branchLabel"]
    validMachineCode = ["0b10110000\n", "0b10110000\n", "0b11110011\n", "0b00000011\n", "0b11100000\n", "0b00000101\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000000\n", "0b00101110\n", "0b00000000\n", "0b11001110\n", "0b00000010\n"]
    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode


def test_assembler_invalidData():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    program = ["asudohsduof"]
    validMachineCode = None
    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode
    assert a.ERRORLOG == ["Invalid instruction found: asudohsduof"]


def test_assembler_moreInvalidData():
    with open("isaV4_definitions.json", "r") as file:
        instructionInfo = json.load(file)
    a = assembler(instructionInfo)
    program = ["asudohsduof", "mfr asd fsdgf", "        asduo"]
    validMachineCode = None
    generatedMachineCode = a.assemble(program)
    assert validMachineCode == generatedMachineCode
    assert a.ERRORLOG == ["Invalid instruction found: asudohsduof", "Invalid instruction found: mfr asd fsdgf", "Invalid instruction found: asduo"]