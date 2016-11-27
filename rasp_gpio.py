import RPi.GPIO as GPIO
import time
import serial
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.pyplot as pltHeat
import numpy as np
from matplotlib import cm
import sys
import numpy as np
import thread
from threading import Lock

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
inflation_deflation_delay = 5
def_delay = 1

vmaxHeat = 0
# Demo 1 edits
inflating = [10, 22]
deflating = [27, 17]
motors = [9, 11]
cbar = None

doneHeatMap = 0
doneID = 0

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


def createImage(xSet1, ySet1, level):
	global mutex
	global ax1
	global matrix
	global doneID
	try:
		mutex.acquire()
		# fig = plt.figure(1)
		for idx, xco in enumerate(xSet1):
			setRowColumn(xco, ySet1[idx], level[idx], matrix)

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
	finally:
		'Created image for mat'
		doneID = 1
		mutex.release()


def updateHeatMap(x, y, val):
	try:
		global mutex
		global heatMapMatrix
		global vmaxHeat
		global axHeat
		global fig
		global cbar
		global doneHeatMap
		mutex.acquire()
		fig = plt.figure(2)
		for idx, xco in enumerate(x):
			heatMapMatrix[xco][y[idx]] = val[idx]
			if val[idx] > vmaxHeat:
				vmaxHeat = val[idx]
	finally:
		print 'Inner heat map changed'
		doneHeatMap = 1
		mutex.release()


def processHeatMap(listToHandle):
	while 1:
		if len(listToHandle) > 0:
			xList = []
			yList = []
			valList = []
			while len(listToHandle) > 0:	
				parsed = listToHandle.pop(0)
				# print 'Size of heat list' + str(len(listToHandle)) 
				if parsed[0] == 'H':
					xList.append(int(parsed[1]))
					yList.append(int(parsed[2]))	
					valList.append(int(parsed[3]))
			# print 'Sent heat list for batch processing'
			updateHeatMap(xList, yList, valList)
		else:
			time.sleep(0.1)

def readData():
	global listToHandleID, listToHandleHeat, ser
	while 1:
		x = ser.readline()
		if x != "":
			# print x
			parsed = x.split(" ")
			if len(parsed) == 2:
				# print 'Added to Inf/def'
				print x
				listToHandleID.append(parsed)
			elif len(parsed) == 4:
				# print x
				# print 'Added to heat map'
				listToHandleHeat.append(parsed)


def processInflateDeflate(listToHandle):
	global status_Matrix, inflation_deflation_delay, motors, inflating, deflating, def_delay
	while 1:
		if len(listToHandle) > 0:
			xList = []
			yList = []
			valList = []
			while len(listToHandle) > 0:
				parsed = listToHandle.pop(0)
				row = int(parsed[0])
				columns = int(parsed[1])
				val = 0
				if status_Matrix[row][columns] == 0:
					val = 0.1
				if status_Matrix[row][columns] == 0:
					print "Inflating"
					status_Matrix[row][columns] = 1
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
					print "Deflating"
					status_Matrix[row][columns] = 0
					if row == 0 and columns == 0:
						# inflate this co-ordinate
						GPIO.output(deflating[0], GPIO.HIGH)
						time.sleep(def_delay)
						GPIO.output(deflating[0], GPIO.LOW)
					elif row == 0 and columns == 1:
						# inflate this co-ordinate
						GPIO.output(deflating[1], GPIO.HIGH)
						time.sleep(def_delay)
						GPIO.output(deflating[1], GPIO.LOW)
				xList.append(row)
				yList.append(columns)
				valList.append(val)
			createImage(xList, yList, valList)
		else:
			time.sleep(0.1)


ser = serial.Serial(
   port='/dev/ttyS0',
   baudrate = 9600,
   timeout=1
)
fig = plt.figure(1)
ax1 = fig.add_subplot(111, projection='3d')
matrix = initZerosMatrix(4, 4)
status_Matrix = initZerosMatrix(4, 4)


# figHeat = plt.figure()
# axHeat = fig.add_subplot(111, projection='2d')

fig = plt.figure(2)
axHeat = fig.add_subplot(111)
heatMapMatrix = initZerosMatrix(16, 16)


GPIO.setmode(GPIO.BCM)
initialize_raspi([], [inflating], [0 for i in inflating])
initialize_raspi([], [deflating], [0 for i in deflating])
initialize_raspi([], [motors], [0 for i in motors])
ser.flushInput()
listToHandleHeat = []
listToHandleID = []

mutex = Lock()
# start the two threads
thread.start_new_thread( processInflateDeflate, (listToHandleID, ) )
thread.start_new_thread( processHeatMap, (listToHandleHeat, ) )
thread.start_new_thread( readData, ())

while 1:
	# time.sleep(3)
	mutex.acquire()
	if doneID == 1:
		print 'Saving new Images'
		plt.figure(1)
		plt.savefig('gen.png', bbox_inches='tight')
		doneID = 0
	if doneHeatMap == 1:	
		print 'Saving new Images'
		plt.figure(2)
		heatmap = axHeat.pcolor(np.array(heatMapMatrix), cmap='hot', vmin=-10, vmax = vmaxHeat + 10, edgecolors='black')
		if cbar != None:
			cbar.remove()
		cbar = fig.colorbar(heatmap)
		labels= [i for i in range(0, len(heatMapMatrix[0]))]
		#cbar.set_ticks(range(100)) # Integer colorbar tick locations
		axHeat.set_xticklabels(labels, minor = False)
		axHeat.set_yticklabels(labels, minor = False)
		plt.savefig('heatMap.png', bbox_inches='tight')
		doneHeatMap = 0;
	mutex.release()


# while 1:

# 	# Maybe test it with the user input 1st
# 	# get the number to input
# 	inp = raw_input('Enter the selectline number\n')
# 	if inp == 'quit':
# 		exit()
# 		GPIO.cleanup()
# 	try:
# 		val = int(inp)
# 		# select the select lines
# 		setSelectLinesTo(val)
# 		# start PWM
# 		pwmObj.stop()
# 		startPwm(75, 100)
# 		time.sleep(3)
# 		pwmObj.stop()
# 		startPwm(0, 100)
# 	except ValueError:
# 		print('Please enter a number')
# 	time.sleep(1)


# def PlotHeatMap(x,y,val):

# 	# row, col = 16,16
# 	# Matrix = [[0 for x in range(row)]for y in range(col)]
# 	Matrix[10][5] = val

# 	vmax = val + 20
# 	labels= [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
# 	fig, ax = plt.subplots()
# 	heatmap = ax.pcolor(Matrix, cmap='hot',vmin=-10,vmax=vmax, edgecolors='black')
# 	cbar = fig.colorbar(heatmap)

# 	#cbar.set_ticks(range(100)) # Integer colorbar tick locations
# 	ax.set_xticklabels(labels, minor=False)
# 	ax.set_yticklabels(labels, minor=False)


# 	ax.invert_yaxis()

