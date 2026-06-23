"""
PyBricks line follower for HuskyLens 2.

Hardware:
- HuskyLens UART on Port B, power on pin 2
- Left motor on Port F, right motor on Port E

Setup:
1. Copy pbhuskylens2.py into your PyBricks project.
2. On the HuskyLens, switch to line tracking and learn the line.
3. Run this program.
"""

from pybricks.parameters import Port, Stop, Direction
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait

from pbhuskylens2 import HuskyLens2, ALGORITHM_LINE_TRACKING, clamp_int

hl = HuskyLens2(Port.B)
left = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
right = Motor(Port.E)
db = DriveBase(left, right, wheel_diameter=89, axle_track=88)

while not hl.knock():
    wait(1000)
    # Yes. The Huskylens2 takes its sweet time to boot.
    print("Waiting for Huskylens 2 to come online")

hl.set_alg(ALGORITHM_LINE_TRACKING)

while True:
    line = hl.get_current_line()
    if line:
        print(line.angle, line.x_target)
        # The Huskylens 2 is SOOOOOOO slow that we can only drive a bit and then
        # we should wait for a new line to come in.
        db.turn(line.angle * 0.02 + line.x_target * 0.08)
        db.straight(30)
    else:
        db.stop()
    wait(10)

