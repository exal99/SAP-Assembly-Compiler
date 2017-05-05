import asm_parser
import argparse


def get_args():
	parser = argparse.ArgumentParser(description="A compiler for the SAP (Simple As Posible) computer")

	parser.add_argument("file", type=argparse.FileType("r"), help="The program file to compile")
	parser.add_argument("-o", "--out", default="a.sap", help="The output file name", metavar="<file name>")

	return parser.parse_args()


def main():
	args = get_args()
	program = args.file.read()
	compiled = asm_parser.parse(program)
	print(compiled, file=open(args.out, "w"), end="")

if __name__ == '__main__':
	main()