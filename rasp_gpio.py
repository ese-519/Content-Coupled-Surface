import RPi.GPIO as GPIO
import time
# Function which controls the motor based on the received data.
# Here, we will be using a de-multiplexer and the raspPi will be controlling the select lines of this demux 

# PWM is boardcom pin 18
pwm_pin = 18 
pwmObj = None
# S0 --- S3
selectLines = [5, 6, 13, 19]


# Initializes input, output for raspberry pi BCM pins
# be sure to init the select lines as well
def initialize_raspi(input, output, default_val):
	GPIO.setmode(GPIO.BCM)
	for num in input:
		GPIO.setup(num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	for idx, num in enumerate(output):
		if default_val[i] = 1:
			GPIO.setup(num, GPIO.OUT, GPIO.HIGH)
		else:
			GPIO.setup(num, GPIO.OUT, GPIO.LOW)


# creates the PWM object and starts the PWM on raspi
def startPwm(duty_cycle, freq):
	if pwmObj == None:
		GPIO.setup(pwm_pin, GPIO.OUT)
		pwmObj = GPIO.PWM(pwm_pin, freq)
	pwmObj.start(duty_cycle)


# This will set the select lines to the wanted value
def setSelectLinesTo(val):
	for i in range(0, 4):
		if val&(1<<i) > 0:
			GPIO.output(selectLines[i], HIGH)
		else:
			GPIO.output(selectLines[i], LOW)

# Main controlling logic
while 1:
	# wait for some input
	# Maybe test it with the user input 1st
	# get the number to input
	inp = raw_input('Enter the selectline number\n')
	try:
		val = int(inp)
		# select the select lines
		setSelectLinesTo(int(val))
		# start PWM
		startPwm(50, 100)
		time.sleep(5)
		# stop PWM after a particular delay
		pwmObj.stop()
	except ValueError:
		print('Please enter a number')
	time.Sleep(1)











