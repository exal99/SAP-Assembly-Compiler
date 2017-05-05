import serial
import argparse
import sys

def get_args():
	parser = argparse.ArgumentParser(description="Uploads a compiled SAP-assembler file to the SAP-Computer via serial connection through an Arduino.")

	parser.add_argument("file", type=argparse.FileType("r"), default=sys.stdin, help="The compiled program")
	parser.add_argument("-p", "--port", default="COM3", choices=["COM3", "COM5"], help="The USB-port for the Arduino")

	return parser.parse_args()

def read_response(ser):
	read = ""
	while not read.endswith("\r\n"):
		read += ser.read(1).decode("ascii")
	ret_code = ""
	while not read.endswith("\r\n"):
		ret_code += ser.read(1).decode("ascii")
	ret_code.strip()
	return read, int(ret_code)



def main():
	args = get_args()
	ser = serial.Serial(port=args.port, timeout=1)
	num_lines = sum(1 for _ in args.file)
	args.file-seek(0)
	response = ""
	for lineno, line in enumerate(map(lambda x: x.strip(), args.file.readlines())):
		print(("SENDING [%d/%d (%d %)]: " + line) %(lineno + 1, num_lines, round((lineno + 1) / num_lines)))
		ser.send(line)
		msg, code = read_response(ser)
		line = "OK! [{}/{}]: " + msg if code == 0 else "FAIL! [{}/{}]: " + msg
		response += line.format(lineno + 1, num_lines) + "\n"
	print("\n" + response, end="")

if __name__ == '__main__':
	main()