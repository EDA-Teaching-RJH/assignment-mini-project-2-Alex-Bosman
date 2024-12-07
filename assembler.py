import re
reservedWords = ("maf", "mfa", "mif", "mfr", "mrf")
reservedWordsFormatted = "".join([("\\b{x}\\b|".format(x=data) if index != len(reservedWords)-1 else "\\b{x}\\b".format(x=data)) for index, data in enumerate(reservedWords)])

print(reservedWordsFormatted)
print(f"^(maf) (\\br[0-9a-f]\\b|(?!(?:{reservedWordsFormatted}))\w+)$")