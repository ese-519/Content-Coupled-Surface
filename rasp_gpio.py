import RPi.GPIO as GPIO
import time

# Function which controls the motor based on the received data.
# Here, we will be using a de-multiplexer and the raspPi will be controlling the select lines of this demux 

# PWM is boardcom pin 18
pwm_pin = 18 
pwmObj = None
# S0 --- S3
selectLines = [6, 13, 19, 26]
enableDemux_pin = 5

# Initializes input, output for raspberry pi BCM pins
# be sure to init the select lines as well
def initialize_raspi(input, output, default_val):
	print input
	print output
	print default_val
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
	# diable the demux
	GPIO.output(enableDemux_pin, GPIO.LOW)
	global selectLines
	global enableDemux_pin

	for i in range(0, 4):
		if val&(1<<i) > 0:
			GPIO.output(selectLines[i], GPIO.HIGH)
		else:
			GPIO.output(selectLines[i], GPIO.LOW)
	# enable the demux
	GPIO.output(enableDemux_pin, GPIO.LOW) 

initialize_raspi([], selectLines, [1 for i in selectLines])
initialize_raspi([], [enableDemux_pin], [0])
startPwm(0, 100)
# Main controlling logic

while 1:
	# wait for some input
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










