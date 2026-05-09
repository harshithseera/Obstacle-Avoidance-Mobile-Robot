# Include the library files
import RPi.GPIO as GPIO
from time import sleep
import signal
import sys

# Include the motor control pins
ENA = 17
IN1 = 27
IN2 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# PWM for speed control
pwm = GPIO.PWM(ENA, 1000)   # 1 kHz frequency
pwm.start(0)                # Start with 0% duty cycle

# Lower value = slower motor
SPEED = 35   # Try values between 20-50


def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)


def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(SPEED)


def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(SPEED)


# Ctrl+C handler
def cleanup(sig, frame):
    print("\nStopping motors and cleaning up GPIO...")
    stop()
    pwm.stop()
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)

try:
    while True:
        forward()
        sleep(1)

        stop()
        sleep(0.5)

        backward()
        sleep(1)

        stop()
        sleep(0.5)

except KeyboardInterrupt:
    cleanup(None, None)
