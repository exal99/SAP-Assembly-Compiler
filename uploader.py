import serial
import argparse
import sys
import serial.tools.list_ports as ports
import time

ARDUINO_START_TIME = 2

RESPONSES = {
	"OK": 0x00,
	"FAIL": 0x1
}

def get_args():
	parser = argparse.ArgumentParser(description="Uploads a compiled SAP-assembler file to the SAP-Computer via serial connection through an Arduino.")

	parser.add_argument("file", type=argparse.FileType("rb"), help="The compiled program")
	parser.add_argument("-p", "--port", default="COM3", choices=[port.device for port in ports.comports()], help="The USB-port for the Arduino")

	return parser.parse_args()

def read_response(ser):
	return ser.read(1)[0]

def get_num_instructions(file):
	byte = file.read(1)
	instructions = 0
	while byte:
		if byte[0] == 0x01:
			instructions += 1
			file.seek(2, 1)
			byte = file.read(1)
		elif byte[0] == 0x02:
			instructions += 1
			file.seek(1, 1)
			byte = file.read(1)
		else:
			raise ValueError("Unknown instruction: 0x%0.2X" %(byte[0]))
	file.seek(0)
	return instructions

def send_instructions(file, ser, num_instructs):
	barray = file.read(32)
	response = ""
	curr_instruct = 1
	print("SENDING")
	dots = 0
	while barray:
		curr_end = 0
		counting = True
		instructs = 0
		while counting:
			if barray[curr_end] == 0x01:
				counting = curr_end + 3 < len(barray)
				curr_end += (3 if curr_end + 3 <= len(barray) else 0)
				instructs += (1 if curr_end + 3 <= len(barray) else 0)
			elif barray[curr_end] == 0x02:
				counting = curr_end + 2 < len(barray)
				curr_end += (2 if curr_end + 2 <= len(barray) else 0)
				instructs += (1 if curr_end + 3 <= len(barray) else 0)
		dots += round((((curr_instruct + instructs)/num_instructs * 100) // 10 - dots))
		sys.stdout.flush()
		ser.write(barray[0:curr_end])
		ser.flush()
		while instructs >= 0:
			ret_code = read_response(ser)
			print(("OK! [{}/{}]" if ret_code == RESPONSES["OK"] else "FAIL! [{}/{}]").format(curr_instruct, num_instructs))
			if ret_code != RESPONSES["OK"]:
				return -1
			curr_instruct += 1
			instructs -= 1
		barray = barray[curr_end:] + file.read(32)
	return 0

def main():
	args = get_args()
	ser = serial.Serial(port=args.port, timeout=5)
	print("ARDUINO STARTING ", end="")
	multiplier = 2
	for _ in range(ARDUINO_START_TIME * multiplier):
		print(".", end="")
		sys.stdout.flush()
		time.sleep(1/multiplier)
	ser.write(b"BIN")
	if ser.read(1)[0] != RESPONSES["OK"]:
		raise Exception("ARDUINO FAIL!")
	print(" [DONE]\n")
	num_instructs = get_num_instructions(args.file)
	ser.write(b"BIN")
	resp = read_response(ser)
	if  resp == RESPONSES["OK"]:
		response = send_instructions(args.file, ser, num_instructs)
	else:
		raise Exception("Failed to set BIN-Mode code: %d" %(resp))


if __name__ == '__main__':
	main()
