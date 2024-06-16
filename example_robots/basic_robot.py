from sbot import Robot

robot = Robot()

robot.motor_board.motors[0].power = 1
robot.motor_board.motors[1].power = 1

# measure the distance of the right ultrasound sensor
# pin 6 is the trigger pin, pin 7 is the echo pin
distance = robot.arduino.ultrasound_measure(6, 7)
print(f"Right ultrasound distance: {distance / 1000} meters")

# motor board, channel 0 to half power forward
robot.motor_board.motors[0].power = 0.5

# motor board, channel 1 to half power forward,
robot.motor_board.motors[1].power = 0.5
# minimal time has passed at this point so the robot will appear to move forward instead of turning

# sleep for 2 second
robot.sleep(2)

# stop both motors
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0
