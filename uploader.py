import serial
import argparse
import sys
import serial.tools.list_ports as ports
import time

ARDUINO_START_TIME = 5

def get_args():
	parser = argparse.ArgumentParser(description="Uploads a compiled SAP-assembler file to the SAP-Computer via serial connection through an Arduino.")

	parser.add_argument("file", type=argparse.FileType("r"), default=sys.stdin, help="The compiled program")
	parser.add_argument("-p", "--port", default="COM3", choices=[port.device for port in ports.comports()], help="The USB-port for the Arduino")

	return parser.parse_args()

def read_response(ser):
	read = ser.readline().decode("ascii").strip()
	ret_code = ser.readline().decode("ascii").strip()
	return read, int(ret_code)



def main():
	args = get_args()
	ser = serial.Serial(port=args.port, timeout=20)
	print("ARDUINO STARTING ", end="")
	for _ in range(ARDUINO_START_TIME):
		print(".", end="")
		sys.stdout.flush()
		time.sleep(1)
	print("\t[DONE]\n")
	print("\t-------\n")
	num_lines = sum(1 for _ in args.file)
	args.file.seek(0)
	response = ""
	for lineno, line in enumerate(map(lambda x: x.strip(), args.file.readlines())):
		print(("SENDING [{}/{} ({} %)]: " + line).format(lineno + 1, num_lines, round((lineno + 1) / num_lines * 100)))
		ser.write(line.encode('ascii'))
		ser.flush()
		msg, code = read_response(ser)
		line = "OK! [{}/{}]: " + msg if code == 0 else "FAIL! [{}/{}]: " + msg
		response += line.format(lineno + 1, num_lines) + "\n"
	print("\n\t-------\n")
	print(response, end="")

if __name__ == '__main__':
	main()
