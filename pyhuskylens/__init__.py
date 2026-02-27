"""
PyHuskyLens - Universal HuskyLens driver for MicroPython
Supports V1 and V2 hardware with I2C and Serial interfaces
"""

from .pyhuskylens import (
    # Main classes
    HuskyLens,
    HuskyLensI2C,
    HuskyLensSerial,
    # Data classes
    Arrow,
    Block,
    Face,
    Hand,
    Pose,
    # Algorithms
    ALGORITHM_MENU,
    ALGORITHM_FACE_RECOGNITION,
    ALGORITHM_OBJECT_TRACKING,
    ALGORITHM_OBJECT_RECOGNITION,
    ALGORITHM_LINE_TRACKING,
    ALGORITHM_COLOR_RECOGNITION,
    ALGORITHM_TAG_RECOGNITION,
    ALGORITHM_OBJECT_CLASSIFICATION,
    ALGORITHM_OCR_RECOGNITION_V2,
    ALGORITHM_LICENSE_RECOGNITION_V2,
    ALGORITHM_QRCODE_RECOGNITION_V2,
    ALGORITHM_BARCODE_RECOGNITION_V2,
    ALGORITHM_EMOTION_RECOGNITION_V2,
    ALGORITHM_POSE_RECOGNITION_V2,
    ALGORITHM_HAND_RECOGNITION_V2,
    # Colors
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_YELLOW,
    # Result dict keys
    BLOCKS,
    ARROWS,
    FRAME,
    FACES,
    HANDS,
    POSES,
    # Utilities
    clamp_int,
)

# Raspberry Pi classes (optional, requires smbus2/pyserial)
try:
    from .rpi import HuskyLensI2C_RPi, HuskyLensSerial_RPi
except ImportError:
    # Not on Raspberry Pi or dependencies not installed
    HuskyLensI2C_RPi = None
    HuskyLensSerial_RPi = None


__version__ = "2.3.0"
__all__ = [
    "HuskyLens",
    "HuskyLensBase",
    "HuskyLensI2C",
    "HuskyLensSerial",
    "HuskyLensI2C_RPi",
    "HuskyLensSerial_RPi",
    "Arrow",
    "Block",
    "Face",
    "Hand",
    "Pose",
    "ALGORITHM_MENU",
    "ALGORITHM_FACE_RECOGNITION",
    "ALGORITHM_OBJECT_TRACKING",
    "ALGORITHM_OBJECT_RECOGNITION",
    "ALGORITHM_LINE_TRACKING",
    "ALGORITHM_COLOR_RECOGNITION",
    "ALGORITHM_TAG_RECOGNITION",
    "ALGORITHM_OBJECT_CLASSIFICATION",
    "ALGORITHM_OCR_RECOGNITION_V2",
    "ALGORITHM_LICENSE_RECOGNITION_V2",
    "ALGORITHM_QRCODE_RECOGNITION_V2",
    "ALGORITHM_BARCODE_RECOGNITION_V2",
    "ALGORITHM_EMOTION_RECOGNITION_V2",
    "ALGORITHM_POSE_RECOGNITION_V2",
    "ALGORITHM_HAND_RECOGNITION_V2",
    "COLOR_BLACK",
    "COLOR_WHITE",
    "COLOR_RED",
    "COLOR_GREEN",
    "COLOR_BLUE",
    "COLOR_YELLOW",
    "BLOCKS",
    "ARROWS",
    "FRAME",
    "FACES",
    "HANDS",
    "POSES",
    "clamp_int",
]
