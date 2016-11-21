import RPi.GPIO as GPIO
import time
import serial
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import sys
# scp rasp_gpio.py pi@10.251.87.217:/home/pi/Desktop/code-rep
# http://10.251.87.217:8080/frontend.html
# Function which controls the motor based on the received data.
# Here, we will be using a de-multiplexer and the raspPi will be controlling the select lines of this demux 

# PWM is boardcom pin 18
pwm_pin = 18
pwmObj = None
# S0 --- S3
selectLines = [6, 13, 19, 26]
enableDemux_pin = 5
demuxInput_pin = 23
inflation_deflation_delay = 4


# Demo 1 edits
inflating = [10, 22]
deflating = [27, 17]
motors = [9, 11]

# Initializes input, output for raspberry pi BCM pins
# be sure to init the select lines as well
def initialize_raspi(input, output, default_val):
	GPIO.setmode(GPIO.BCM)
	for num in input:
		GPIO.setup(num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	for idx, num in enumerate(output):
		GPIO.setup(output[idx], GPIO.OUT)
		if default_val[idx] == 1:
			GPIO.output(output[idx], GPIO.HIGH)
		else:
			GPIO.output(output[idx], GPIO.LOW)


# creates the PWM object and starts the PWM on raspi
def startPwm(duty_cycle, freq):
	global pwmObj
	global pwm_pin
	if pwmObj == None:
		GPIO.setup(pwm_pin, GPIO.OUT)
	pwmObj = GPIO.PWM(pwm_pin, freq)
	pwmObj.start(duty_cycle)


# This will set the select lines to the wanted value
def setSelectLinesTo(val):
	global selectLines
	global enableDemux_pin
	# diable the demux
	# GPIO.output(enableDemux_pin, GPIO.LOW)

	for i in range(0, 4):
		if val&(1<<i) > 0:
			GPIO.output(selectLines[i], GPIO.HIGH)
		else:
			GPIO.output(selectLines[i], GPIO.LOW)
	# enable the demux
	# GPIO.output(enableDemux_pin, GPIO.HIGH)

def initZerosMatrix(rows, columns):
	return [[0 for j in range(0, columns)] for i in range(0, rows)]


def setRowColumn(row, column, value, matrix):
	matrix[row][column] = value


def plot3DMatrix(matrix):
	rows = len(matrix)
	columns = len(matrix[0])
	# print rows
	# print columns
	xRows = []
	yCols =[]
	height = []
	for i in range(0, rows):
		for j in range(0, columns):
			# put the rows and columns 
			xRows.append(i)
			yCols.append(j)
			height.append(matrix[i][j]) 
	return xRows, yCols, height


# initialize_raspi([], [enableDemux_pin], [0])
# startPwm(0, 100)


def createImage(xSet1, ySet1, level):
	global fig
	global ax1
	global matrix

	setRowColumn(xSet1, ySet1, level, matrix)

	xPos, yPos, dz = plot3DMatrix(matrix)

	zPos = [0 for i in range(0, len(dz))]
	dx = np.ones(len(xPos))
	dy = np.ones(len(yPos))
	ax1.set_zlim(0, 0.5)

	colors = []
	for i in range(0, len(zPos)):
		if dz[i] > 0.3:
			colors.append('b')
		elif dz[i] > 0:
			colors.append('r')
		else:
			colors.append('g')
	 
	ax1.bar3d(xPos, yPos, zPos, dx, dy, dz, color=colors)
	plt.savefig('gen.png', bbox_inches='tight')	

ser = serial.Serial(
   port='/dev/ttyS0',
   baudrate = 9600,
   timeout=1
)
fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d')
matrix = initZerosMatrix(4, 4)
status_Matrix = initZerosMatrix(4, 4)

GPIO.setmode(GPIO.BCM)
# init select lines
# initialize_raspi([], selectLines, [0 for i in selectLines])
# set output to be 0
# initialize_raspi([], [demuxInput_pin], [0])
# maybe have a demux for valves as well with same select lines but different output
initialize_raspi([], [inflating], [0 for i in inflating])
initialize_raspi([], [deflating], [0 for i in deflating])
initialize_raspi([], [motors], [0 for i in motors])



while 1:
	x = ser.readline()
	if x != "":
		print x
		parsed = x.split(" ")
		if len(parsed) == 2:
			row = int(parsed[0])
			column = int(parsed[1])
			if status_Matrix[row][columns] == 0:
				status_Matrix[row][columns] = 1
				createImage(row, columns, 0.1)
				if row == 0 and columns == 0:
					# inflate this co-ordinate
					GPIO.output(inflating[0], GPIO.HIGH)
					GPIO.output(motors[0], GPIO.HIGH)
					time.sleep(inflation_deflation_delay)
					GPIO.output(inflating[0], GPIO.LOW)
					GPIO.output(motors[0], GPIO.LOW)
				elif row == 0 and columns == 1:
					# inflate this co-ordinate
					GPIO.output(inflating[1], GPIO.HIGH)
					GPIO.output(motors[1], GPIO.HIGH)
					time.sleep(inflation_deflation_delay)
					GPIO.output(inflating[1], GPIO.LOW)
					GPIO.output(motors[1], GPIO.LOW)

			else:
				createImage(row, columns, 0)
				status_Matrix[row][columns] = 0
				if row == 0 and columns == 0:
					# inflate this co-ordinate
					GPIO.output(deflating[0], GPIO.HIGH)
					time.sleep(inflation_deflation_delay)
					GPIO.output(deflating[0], GPIO.LOW)
				elif row == 0 and columns == 1:
					# inflate this co-ordinate
					GPIO.output(deflating[1], GPIO.HIGH)
					time.sleep(inflation_deflation_delay)
					GPIO.output(deflating[1], GPIO.LOW)

# while 1:
# 	x = ser.readline()
# 	if x != "":
# 		print x
# 		parsed = x.split(" ")
# 		if len(parsed) == 2:
# 			row = int(parsed[0])
# 			column = int(parsed[1])
# 			if status_Matrix[row][columns] == 0:
# 				val = parsed[0]*4 + parsed[1]
# 				setSelectLinesTo(val)
# 				status_Matrix[row][columns] = 1
# 				createImage(row, columns, 0.1)
# 				GPIO.output(demuxInput_pin, GPIO.HIGH)
# 				time.sleep(inflation_deflation_delay)
# 				GPIO.output(demuxInput_pin, GPIO.LOW)
# 			else:
# 				createImage(row, columns, 0)
# 				status_Matrix[row][columns] = 0

while 1:

	# Maybe test it with the user input 1st
	# get the number to input
	inp = raw_input('Enter the selectline number\n')
	if inp == 'quit':
		exit()
		GPIO.cleanup()
	try:
		val = int(inp)
		# select the select lines
		setSelectLinesTo(val)
		# start PWM
		pwmObj.stop()
		startPwm(75, 100)
		time.sleep(3)
		pwmObj.stop()
		startPwm(0, 100)
	except ValueError:
		print('Please enter a number')
	time.sleep(1)










