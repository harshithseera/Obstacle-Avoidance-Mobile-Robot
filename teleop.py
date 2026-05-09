import RPi.GPIO as GPIO
import curses
import sys

# ----------------------------
# Pin definitions
# ----------------------------

# Right motors
ENA = 13
IN1 = 27
IN2 = 22

# Left motors
ENB = 12
IN3 = 24
IN4 = 25

# ----------------------------
# GPIO setup
# ----------------------------

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = [ENA, IN1, IN2, ENB, IN3, IN4]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# PWM setup
PWM_FREQ = 100

pwm_right = GPIO.PWM(ENA, PWM_FREQ)
pwm_left = GPIO.PWM(ENB, PWM_FREQ)

pwm_right.start(0)
pwm_left.start(0)

SPEED = 80

# ----------------------------
# Motor functions
# ----------------------------

def set_speed(speed):
    pwm_right.ChangeDutyCycle(speed)
    pwm_left.ChangeDutyCycle(speed)


def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

    set_speed(0)


def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    set_speed(SPEED)


def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    set_speed(SPEED)


def left():
    # Left in-place rotation
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    set_speed(SPEED)


def right():
    # Right in-place rotation
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    set_speed(SPEED)


# ----------------------------
# Cleanup
# ----------------------------

def cleanup():
    stop()

    pwm_right.stop()
    pwm_left.stop()

    GPIO.cleanup()
    curses.endwin()

    print("Clean exit.")
    sys.exit(0)

# ----------------------------
# Keyboard control
# ----------------------------

def main(stdscr):

    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)

    stdscr.addstr(0, 0, "W/A/S/D to move")
    stdscr.addstr(1, 0, "SPACE to stop")
    stdscr.addstr(2, 0, "Q to quit")

    while True:

        key = stdscr.getch()

        if key == ord('w'):
            forward()
            stdscr.addstr(4, 0, "Forward        ")

        elif key == ord('s'):
            backward()
            stdscr.addstr(4, 0, "Backward       ")

        elif key == ord('a'):
            left()
            stdscr.addstr(4, 0, "Rotate Left    ")

        elif key == ord('d'):
            right()
            stdscr.addstr(4, 0, "Rotate Right   ")

        elif key == ord(' '):
            stop()
            stdscr.addstr(4, 0, "Stopped        ")

        elif key == ord('q'):
            cleanup()


try:
    curses.wrapper(main)

except KeyboardInterrupt:
    cleanup()
