from assembler import assembler
import json

# run tests by typing in pytest into console


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

test_instruction_mif()
'''
#        "maf" : {"opcode" : "0000", "instructionType" : "typeB"},
        "mfa" : {"opcode" : "0001", "instructionType" : "typeB"},
        "mif" : {"opcode" : "0010", "instructionType" : "typeC"},
        "mfr" : {"opcode" : "0011", "instructionType" : "typeD"},
        "mrf" : {"opcode" : "0100", "instructionType" : "typeD"},
        "add" : {"opcode" : "0101", "instructionType" : "typeB"},
        "sub" : {"opcode" : "0110", "instructionType" : "typeB"},
        "ior" : {"opcode" : "0111", "instructionType" : "typeB"},
        "xor" : {"opcode" : "1000", "instructionType" : "typeB"},
        "and" : {"opcode" : "1001", "instructionType" : "typeB"},
        "inc" : {"opcode" : "1010", "instructionType" : "typeA"},
        "lrs" : {"opcode" : "1011", "instructionType" : "typeA"},
        "brh" : {"opcode" : "1100", "instructionType" : "typeC"},
        "bil" : {"opcode" : "1101", "instructionType" : "typeC"},
        "bge" : {"opcode" : "1110", "instructionType" : "typeC"},
        "bie" : {"opcode" : "1111", "instructionType" : "typeC"}
'''