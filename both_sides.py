# Differential Drive Motor Test
# Right motor  -> ENA=17, IN1=27, IN2=22
# Left motor   -> ENB=23, IN3=24, IN4=25

import RPi.GPIO as GPIO
from time import sleep
import signal
import sys

# ----------------------------
# Pin definitions
# ----------------------------

# Right motor
ENA = 13
IN1 = 27
IN2 = 22

# Left motor
ENB = 12
IN3 = 25
IN4 = 24

# ----------------------------
# GPIO setup
# ----------------------------

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

motor_pins = [ENA, IN1, IN2, ENB, IN3, IN4]

for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# PWM setup
pwm_right = GPIO.PWM(ENA, 100)
pwm_left = GPIO.PWM(ENB, 100)

pwm_right.start(0)
pwm_left.start(0)

# Speed control (0-100)
SPEED = 40

# ----------------------------
# Motor control functions
# ----------------------------

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

    pwm_right.ChangeDutyCycle(0)
    pwm_left.ChangeDutyCycle(0)


def forward():
    # Right wheel forward
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    # Left wheel forward
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    pwm_right.ChangeDutyCycle(SPEED)
    pwm_left.ChangeDutyCycle(SPEED)


def backward():
    # Right wheel backward
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    # Left wheel backward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    pwm_right.ChangeDutyCycle(SPEED)
    pwm_left.ChangeDutyCycle(SPEED)


def rotate_left():
    # Right wheel forward
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    # Left wheel backward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    pwm_right.ChangeDutyCycle(SPEED)
    pwm_left.ChangeDutyCycle(SPEED)


def rotate_right():
    # Right wheel backward
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    # Left wheel forward
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    pwm_right.ChangeDutyCycle(SPEED)
    pwm_left.ChangeDutyCycle(SPEED)

# ----------------------------
# Ctrl+C cleanup handler
# ----------------------------

def cleanup(sig=None, frame=None):
    print("\nStopping motors and cleaning up GPIO...")
    stop()

    pwm_right.stop()
    pwm_left.stop()

    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

# ----------------------------
# Main loop
# ----------------------------

s_continue = 1
s_interval = 1

try:
    while True:

        print("Forward")
        forward()
        sleep(s_continue)

#         stop()
        sleep(s_interval)

        print("Backward")
        backward()
        sleep(s_continue)

#        stop()
        sleep(s_interval)

        print("Rotate Left")
        rotate_left()
        sleep(s_continue)

#        stop()
        sleep(s_interval)

        print("Rotate Right")
        rotate_right()
        sleep(s_continue)

#        stop()
        sleep(s_interval)

except KeyboardInterrupt:
    cleanup()
