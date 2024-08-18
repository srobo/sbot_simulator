import math

from controller import Keyboard
from sr.robot3 import A0, A1, A2, Robot

# Any keys still pressed in the following period will be handled again
# leading to rprinting sensors multiple times
KEYBOARD_SAMPLING_PERIOD = 100
NO_KEY_PRESSED = -1

CONTROLS = {
    "forward": (ord("W"), ord("I")),
    "reverse": (ord("S"), ord("K")),
    "left": (ord("A"), ord("J")),
    "right": (ord("D"), ord("L")),
    "sense": (ord("Q"), ord("U")),
    "see": (ord("E"), ord("O")),
    "led": (ord("R"), ord("P")),
    "boost": (Keyboard.SHIFT, Keyboard.CONTROL),
    "angle_unit": (ord("B"), ord("B")),
}

USE_DEGREES = False


class KeyboardInterface:
    def __init__(self):
        self.keyboard = Keyboard()
        self.keyboard.enable(KEYBOARD_SAMPLING_PERIOD)
        self.pressed_keys = set()

    def process_keys(self):
        new_keys = set()
        key = self.keyboard.getKey()

        while key != NO_KEY_PRESSED:
            key_ascii = key & 0x7F  # mask out modifier keys
            key_mod = key & (~0x7F)

            new_keys.add(key_ascii)
            if key_mod:
                new_keys.add(key_mod)

            key = self.keyboard.getKey()

        key_summary = {
            "pressed": new_keys - self.pressed_keys,
            "held": new_keys,
            "released": self.pressed_keys - new_keys,
        }

        self.pressed_keys = new_keys

        return key_summary


def angle_str(angle: float) -> str:
    if USE_DEGREES:
        degrees = math.degrees(angle)
        return f"{degrees:.1f}°"
    else:
        return f"{angle:.4f} rad"


def print_sensors(robot: Robot) -> None:
    ultrasonic_sensor_names = {
        (2, 3): "Front",
        (4, 5): "Left",
        (6, 7): "Right",
        (8, 9): "Back",
    }
    reflectance_sensor_names = {
        A0: "Left",
        A1: "Center",
        A2: "Right",
    }
    touch_sensor_names = {
        10: "Front Left",
        11: "Front Right",
        12: "Rear Left",
        13: "Rear Right",
    }

    print("Distance sensor readings:")
    for (trigger_pin, echo_pin), name in ultrasonic_sensor_names.items():
        dist = robot.arduino.ultrasound_measure(trigger_pin, echo_pin)
        print(f"({trigger_pin}, {echo_pin}) {name: <12}: {dist:.0f} mm")

    print("Touch sensor readings:")
    for pin, name in touch_sensor_names.items():
        touching = robot.arduino.pins[pin].digital_value
        print(f"{pin} {name: <6}: {touching}")

    print("Reflectance sensor readings:")
    for Apin, name in reflectance_sensor_names.items():
        reflectance = robot.arduino.pins[Apin].analog_value
        print(f"{Apin} {name: <12}: {reflectance:.2f} V")


def print_camera_detection(robot: Robot) -> None:
    markers = robot.camera.see()
    if markers:
        print(f"Found {len(markers)} makers:")
        for marker in markers:
            print(f" #{marker.id}")
            print(
                f" Position: {marker.distance:.0f} mm, azi: {angle_str(marker.azimuth)}, "
                f"elev: {angle_str(marker.elevation)}",
            )
            yaw, pitch, roll = marker.orientation
            print(
                f" Orientation: yaw: {angle_str(yaw)}, pitch: {angle_str(pitch)}, "
                f"roll: {angle_str(roll)}",
            )
            print()
    else:
        print("No markers")

    print()


robot = Robot()

keyboard = KeyboardInterface()

key_sense = CONTROLS["sense"][robot.zone]

print(
    "Note: you need to click on 3D viewport for keyboard events to be picked "
    "up by webots",
)

while True:
    boost = False
    left_power = 0.0
    right_power = 0.0

    keys = keyboard.process_keys()

    # Actions that are run continuously while the key is held
    if CONTROLS["forward"][robot.zone] in keys["held"]:
        left_power += 0.5
        right_power += 0.5

    if CONTROLS["reverse"][robot.zone] in keys["held"]:
        left_power += -0.5
        right_power += -0.5

    if CONTROLS["left"][robot.zone] in keys["held"]:
        left_power -= 0.25
        right_power += 0.25

    if CONTROLS["right"][robot.zone] in keys["held"]:
        left_power += 0.25
        right_power -= 0.25

    if CONTROLS["boost"][robot.zone] in keys["held"]:
        boost = True

    # Actions that are run once when the key is pressed
    if CONTROLS["sense"][robot.zone] in keys["pressed"]:
        print_sensors(robot)

    if CONTROLS["see"][robot.zone] in keys["pressed"]:
        print_camera_detection(robot)

    if CONTROLS["led"][robot.zone] in keys["pressed"]:
        pass

    if CONTROLS["angle_unit"][robot.zone] in keys["pressed"]:
        USE_DEGREES = not USE_DEGREES
        print(f"Angle unit set to {'degrees' if USE_DEGREES else 'radians'}")

    if boost:
        # double power values but constrain to [-1, 1]
        left_power = max(min(left_power * 2, 1), -1)
        right_power = max(min(right_power * 2, 1), -1)

    robot.motor_board.motors[0].power = left_power
    robot.motor_board.motors[1].power = right_power

    robot.sleep(KEYBOARD_SAMPLING_PERIOD / 1000)
