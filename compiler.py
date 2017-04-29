import asm_parser
import argparse


def get_args():
	parser = argparse.ArgumentParser(description="A compiler for the SPA (Simple As Posible) computer")

	parser.add_argument("file", type=argparse.FileType("r"), help="The program file to compile")

	return parser.parse_args()


def main():
	program = get_args().file.read()
	compiled = asm_parser.parse(program)
	print()
	print(compiled)

if __name__ == '__main__':
	main()