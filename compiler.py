import asm_parser
import argparse
import sys


def get_args():
	parser = argparse.ArgumentParser(description="A compiler for the SAP (Simple As Posible) computer")

	parser.add_argument("file", type=argparse.FileType("r"), default=sys.stdin, help="The program file to compile")
	parser.add_argument("-o", "--out", default="a.sap", help="The output file name", metavar="<file name>")
	parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output. Prints the binary contentent in a fomrated way.")

	return parser.parse_args()


def main():
	args = get_args()
	program = args.file.read()
	text, compiled = asm_parser.parse(program)
	if args.verbose:
		print(text)
	with open(args.out, "wb") as f:
		f.write(compiled)

if __name__ == '__main__':
	main()
