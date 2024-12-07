import re

'''
reservedWords = ("maf", "mfa", "mif", "mfr", "mrf")
reservedWordsFormatted = "".join([("\\b{x}\\b|".format(x=data) if index != len(reservedWords)-1 else "\\b{x}\\b".format(x=data)) for index, data in enumerate(reservedWords)])

print(reservedWordsFormatted)
print(f"^(maf) (\\br[0-9a-f]\\b|(?!(?:{reservedWordsFormatted}))\w+)$")
'''

def assemble(assemblyArray):

    ## preprocessing

    assemblyArray = [x.split(";")[0].strip().casefold() for x in assemblyArray if x.split(";")[0].strip().casefold() != ""]

    print(assemblyArray)
    pattern = re.compile("^(lrs)$")




def main():
    with open("assembly.txt", "r") as file:
        assemblyArray = file.readlines()
        #print(assemblyArray)
        assemble(assemblyArray)


if __name__ == __name__:
    main()