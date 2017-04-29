# ASEMBELR 

import re, sys

OP_CODES = {
	"NOP": 0b0000,
	"LDA": 0b0001,
	"STA": 0b0010,
	"LDB": 0b0011,
	"ADD": 0b0100,
	"SUB": 0b0101
}

VARIABLE = "([a-zA-Z]\\w*)"
BINARY 	 = "(0b[0-1]+)"
HEX		 = "(0x[0-9a-fA-F]+)"
BIN_HEX  = "(%s|%s)" %(BINARY, HEX)

DEFINE_STATEMENT = re.compile("#DEFINE {} {}".format(VARIABLE, BIN_HEX))
SET_STATEMENT 	 = re.compile("#SET ({}|{}) {}".format(VARIABLE, BIN_HEX, BIN_HEX))

STATEMENTS = []

def replace_tags(text, tags):
	for key in tags:
		text = text.replace(key, tags[key])
	return text


with open("statements.txt", "r") as statements:
	tags = {
		"#BIN_HEX":  BIN_HEX,
		"#HEX": 	 HEX,
		"#BINARY":   BINARY,
		"#VARIABLE": VARIABLE
	}
	for line in statements.readlines():
		command, regex, nargs = line.split(": ")
		if command not in OP_CODES:
			raise StatementDefenitionError("'" + command + "'" + " has no OP-CODE definition")
		regex = replace_tags(regex, tags)
		STATEMENTS.append((re.compile(regex.strip()), int(nargs)))


class AsemblerParserError(Exception):
	pass

class StatementDefenitionError(Exception):
	pass

def exception_handler(exception_type, exception, traceback):
	if exception_type.__name__ == AsemblerParserError.__name__:
		print("{}: {}".format(exception_type.__name__, exception))
	else:
		sys.excepthook(exception_type, exception, traceback)


def make_error(msg, line, lineno, col):
	caret = "{: >{}}".format("^", col)
	msg = replace_tags(msg, {"#LINE": str(lineno), "#COL": str(col)})
	return AsemblerParserError("{}:\n\n\t{}\n\t{}".format(msg, line, caret))


def isMemAddress(string):
	return bool(re.compile(BIN_HEX).match(string))

def toInteger(string):
	if isinstance(string, str):
		if string.startswith("0b"):
			return int(string, 2)
		elif string.startswith("0x"):
			return int(string, 16)
		else:
			return int(string)
	else:
		return int(string)


def toAddress(var, variables):
	if not isMemAddress(var):
		if  var not in variables:
			raise NameError("name '{}' is not defined".format(var))
		return variables[var]
	return var

def getInvalidArgPos(line, nargs):
	return line.find(' '.join(line.split()[nargs + 1:])) + 1

def parse(text):
	sys.excepthook = exception_handler
	variables = {}
	output = ""
	prog_address = 0
	for lineno, line in enumerate(text.split("\n")):
		print("LINE %d: %s" %(lineno + 1, line))
		if line:
			if DEFINE_STATEMENT.match(line):
				variable, address = line.split()[1:]
				variables[variable] = address

			elif SET_STATEMENT.match(line):
				memAddress, value = line.split()[1:]
				output += "SET " + bin(toInteger(toAddress(memAddress, variables))) + " " + bin(toInteger(value)) + "\n"
			else:
				for statement, nargs in STATEMENTS:
					if statement.match(line.strip()):
						op, *data = line.split() if len(line.split()) == nargs + 1 else (-1, *line.split()[1:])
						if op != -1:
							output_data =  bin(OP_CODES[op] << 4 | toInteger(toAddress(data[0] if len(data) != 0 else "0b0", variables)))[2:].zfill(8)
							output += "SET " + bin(prog_address) + " " + "0b" + output_data[0:4] + " " + output_data[4:] + "\n"
							prog_address += 1
							break
						else:
							print()
							raise make_error("{} takes {} arguments but {} were given".format(line.split()[0], nargs, len(data)), line, lineno + 1, getInvalidArgPos(line, nargs))
				else:
					print()
					raise make_error("Unknow command on line: %d" %(lineno + 1), line, lineno + 1, 0)
	return output


def readProg():
	prog = ""
	line = input()
	while line != "END":
		prog += line + "\n"
		line = input()
	return prog[:-1]

def main():
	prog = parse(readProg())
	print()
	print(prog)

if __name__ == '__main__':
	
	main()