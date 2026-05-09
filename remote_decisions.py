import argparse
import curses
import socket
import sys
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False

    # Fallback GPIO stub for non-RPi environments.
    class MockPWM:
        def __init__(self, pin, freq):
            self.pin = pin
            self.freq = freq

        def start(self, _):
            pass

        def ChangeDutyCycle(self, _):
            pass

        def stop(self):
            pass

    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        LOW = 0
        HIGH = 1

        def setmode(self, _):
            pass

        def setwarnings(self, _):
            pass

        def setup(self, *_args, **_kwargs):
            pass

        def output(self, *_args, **_kwargs):
            pass

        def PWM(self, pin, freq):
            return MockPWM(pin, freq)

        def cleanup(self):
            pass

    GPIO = MockGPIO()

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
PWM_FREQ = 60

pwm_right = GPIO.PWM(ENA, PWM_FREQ)
pwm_left = GPIO.PWM(ENB, PWM_FREQ)

pwm_right.start(0)
pwm_left.start(0)

SPEED = 10
LAST_COMMAND = None
COMMANDS = {"FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP"}

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


def left():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    set_speed(SPEED)


def right():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    set_speed(SPEED)


def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    set_speed(SPEED)


def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    set_speed(SPEED)


def execute_command(command: str, silent: bool = False) -> None:
    global LAST_COMMAND
    cmd = command.upper()
    if cmd == LAST_COMMAND and cmd != "STOP":
        return
    LAST_COMMAND = cmd

    if cmd == "FORWARD":
        forward()
    elif cmd == "BACKWARD":
        backward()
    elif cmd == "LEFT":
        left()
    elif cmd == "RIGHT":
        right()
    elif cmd == "STOP":
        stop()
    else:
        return

    if not GPIO_AVAILABLE and not silent:
        print(f"Command: {cmd}")


# ----------------------------
# Cleanup
# ----------------------------

def cleanup(use_curses: bool = False):
    stop()

    pwm_right.stop()
    pwm_left.stop()

    GPIO.cleanup()
    if use_curses:
        try:
            curses.endwin()
        except curses.error:
            pass

    print("Clean exit.")
    sys.exit(0)


# ----------------------------
# Keyboard control
# ----------------------------

def keyboard_loop(stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)

    stdscr.addstr(0, 0, "W/A/S/D to move")
    stdscr.addstr(1, 0, "SPACE to stop")
    stdscr.addstr(2, 0, "Q to quit")

    key_map = {
        ord("w"): ("Forward", "FORWARD"),
        ord("s"): ("Backward", "BACKWARD"),
        ord("a"): ("Rotate Left", "LEFT"),
        ord("d"): ("Rotate Right", "RIGHT"),
        ord(" "): ("Stopped", "STOP"),
    }

    while True:
        key = stdscr.getch()
        if key in key_map:
            label, command = key_map[key]
            execute_command(command)
            stdscr.addstr(4, 0, f"{label:<14}")
        elif key == ord("q"):
            cleanup(use_curses=True)


def udp_loop(host: str, port: int, deadman: float) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(0.1)

    last_rx = time.time()
    print(f"Listening for UDP commands on {host}:{port}")

    while True:
        now = time.time()
        if deadman > 0 and now - last_rx > deadman:
            execute_command("STOP", silent=True)

        try:
            data, _addr = sock.recvfrom(1024)
        except socket.timeout:
            continue

        command = data.decode("utf-8", errors="ignore").strip().upper()
        if not command:
            continue
        if command == "QUIT":
            break
        if command in COMMANDS:
            execute_command(command)
            last_rx = time.time()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robot teleop controller")
    parser.add_argument(
        "--mode",
        choices=["keyboard", "udp"],
        default="keyboard",
        help="Control mode: keyboard or UDP server",
    )
    parser.add_argument("--host", default="0.0.0.0", help="UDP bind host")
    parser.add_argument("--port", type=int, default=5005, help="UDP bind port")
    parser.add_argument("--speed", type=int, default=60, help="PWM duty cycle (0-100)")
    parser.add_argument(
        "--deadman",
        type=float,
        default=0.5,
        help="Stop if no UDP command for N seconds (UDP mode)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    global SPEED
    SPEED = args.speed

    if not GPIO_AVAILABLE:
        print("GPIO not available; running in mock mode.")

    if args.mode == "keyboard":
        try:
            curses.wrapper(keyboard_loop)
        except KeyboardInterrupt:
            cleanup(use_curses=True)
    else:
        try:
            udp_loop(args.host, args.port, args.deadman)
        except KeyboardInterrupt:
            pass
        cleanup(use_curses=False)


if __name__ == "__main__":
    main()
