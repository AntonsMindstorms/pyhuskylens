"""
HuskyLens 2 driver for PyBricks (UART only).
"""

__version__ = "1.0.0"

import struct

from pybricks.iodevices import UARTDevice
from pybricks.tools import wait

_HEADER = b"\x55\xaa"

_CMD_KNOCK = 0x00
_CMD_GET_RESULT = 0x01
_CMD_SET_ALGORITHM = 0x0A
_CMD_SET_MULTI_ALGORITHM = 0x0C
_CMD_RETURN_OK = 0x1A
_CMD_RETURN_INFO = 0x1B
_CMD_RETURN_BLOCK = 0x1C
_CMD_RETURN_ARROW = 0x1D
_CMD_DRAW_TEXT = 0x28
_CMD_CLEAR_TEXT = 0x29
_CMD_DRAW_RECT = 0x26
_CMD_CLEAR_RECT = 0x27

ALGORITHM_MENU = 0
ALGORITHM_FACE_RECOGNITION = 1
ALGORITHM_OBJECT_RECOGNITION = 2
ALGORITHM_OBJECT_TRACKING = 3
ALGORITHM_COLOR_RECOGNITION = 4
ALGORITHM_OBJECT_CLASSIFICATION = 5
ALGORITHM_SELF_LEARNING_CLASSIFICATION = 6
ALGORITHM_SEGMENT = 7
ALGORITHM_HAND_RECOGNITION = 8
ALGORITHM_POSE_RECOGNITION = 9
ALGORITHM_LICENSE_RECOGNITION = 10
ALGORITHM_OCR_RECOGNITION = 11
ALGORITHM_LINE_TRACKING = 12
ALGORITHM_EMOTION_RECOGNITION = 13
ALGORITHM_GAZE_RECOGNITION = 14
ALGORITHM_FACE_ORIENTATION = 15
ALGORITHM_TAG_RECOGNITION = 16
ALGORITHM_BARCODE_RECOGNITION = 17
ALGORITHM_QRCODE_RECOGNITION = 18
ALGORITHM_FALLDOWN_RECOGNITION = 19

COLOR_BLACK = 0
COLOR_WHITE = 1
COLOR_RED = 2
COLOR_GREEN = 3
COLOR_BLUE = 4
COLOR_YELLOW = 5

BLOCKS = "blocks"
LINES = "lines"
FACES = "faces"
HANDS = "hands"
POSES = "poses"


class Line:
    """Line-tracking path vector (RETURN_ARROW 0x1D)."""

    __slots__ = ("ID", "level", "x_target", "y_target", "angle", "length", "type")

    def __init__(self, ID, level, x_target, y_target, angle, length):
        self.ID = ID
        self.level = level
        self.x_target = x_target
        self.y_target = y_target
        self.angle = angle
        self.length = length
        self.type = "LINE"

    def __repr__(self):
        return "Line(ID=%d, level=%d, target=(%d,%d), angle=%d, len=%d)" % (
            self.ID,
            self.level,
            self.x_target,
            self.y_target,
            self.angle,
            self.length,
        )


class Block:
    __slots__ = ("x", "y", "width", "height", "ID", "confidence", "name", "content", "learned", "type")

    def __init__(self, x, y, width, height, ID, confidence=0, name="", content=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ID = ID
        self.confidence = confidence
        self.name = name
        self.content = content
        self.learned = ID > 0
        self.type = "BLOCK"

    def __repr__(self):
        return "Block(x=%d, y=%d, w=%d, h=%d, ID=%d)" % (
            self.x,
            self.y,
            self.width,
            self.height,
            self.ID,
        )


class Face:
    __slots__ = (
        "x",
        "y",
        "width",
        "height",
        "ID",
        "confidence",
        "name",
        "content",
        "learned",
        "type",
        "leye_x",
        "leye_y",
        "reye_x",
        "reye_y",
        "nose_x",
        "nose_y",
        "lmouth_x",
        "lmouth_y",
        "rmouth_x",
        "rmouth_y",
    )

    def __init__(self, x, y, width, height, ID, confidence, name, content, landmarks):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ID = ID
        self.confidence = confidence
        self.name = name
        self.content = content
        self.learned = ID > 0
        self.type = "FACE"
        if len(landmarks) >= 10:
            self.leye_x, self.leye_y = landmarks[0], landmarks[1]
            self.reye_x, self.reye_y = landmarks[2], landmarks[3]
            self.nose_x, self.nose_y = landmarks[4], landmarks[5]
            self.lmouth_x, self.lmouth_y = landmarks[6], landmarks[7]
            self.rmouth_x, self.rmouth_y = landmarks[8], landmarks[9]


class Hand:
    __slots__ = (
        "x",
        "y",
        "width",
        "height",
        "ID",
        "confidence",
        "name",
        "content",
        "learned",
        "type",
        "wrist_x",
        "wrist_y",
    )

    def __init__(self, x, y, width, height, ID, confidence, name, content, keypoints):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ID = ID
        self.confidence = confidence
        self.name = name
        self.content = content
        self.learned = ID > 0
        self.type = "HAND"
        if len(keypoints) >= 2:
            self.wrist_x, self.wrist_y = keypoints[0], keypoints[1]


class Pose:
    __slots__ = (
        "x",
        "y",
        "width",
        "height",
        "ID",
        "confidence",
        "name",
        "content",
        "learned",
        "type",
        "nose_x",
        "nose_y",
    )

    def __init__(self, x, y, width, height, ID, confidence, name, content, keypoints):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ID = ID
        self.confidence = confidence
        self.name = name
        self.content = content
        self.learned = ID > 0
        self.type = "POSE"
        if len(keypoints) >= 2:
            self.nose_x, self.nose_y = keypoints[0], keypoints[1]


class HuskyLens2:
    """HuskyLens 2 UART driver for PyBricks."""

    def __init__(self, port, power_pin=2, baudrate=115200, debug=False):
        self.debug = debug
        self.connected = False
        self.current_algorithm = ALGORITHM_OBJECT_RECOGNITION
        self.uart = UARTDevice(port, baudrate=baudrate, power_pin=power_pin)
        wait(500)

    def _checksum(self, data):
        cs = 0
        for b in data:
            cs += b
        return cs & 0xFF

    def _flush(self):
        try:
            for _ in range(10):
                n = self.uart.waiting()
                if not n:
                    break
                self.uart.read(min(n, 64))
        except Exception as e:
            if self.debug:
                print("Flush error:", e)

    def _write(self, data):
        self._flush()
        self.uart.write(data)
        wait(5)

    def _read(self, size):
        data = b""
        for _ in range(150):
            if self.uart.waiting():
                chunk = self.uart.read(1)
                if chunk:
                    data = data + chunk
            if len(data) >= size:
                return data[:size]
            wait(1)
        return data

    def _cmd(self, command, algorithm=0, content=b""):
        header = bytes([0x55, 0xAA, command, algorithm, len(content)])
        packet = header + content
        self._write(packet + bytes([self._checksum(packet)]))

    def _read_packet(self):
        header = self._read(5)
        if len(header) == 5 and header[:2] == _HEADER:
            size = header[4]
            return header + self._read(size + 1)
        return None

    def knock(self):
        for _ in range(5):
            try:
                self._cmd(_CMD_KNOCK)
                resp = self._read(6)
                if len(resp) >= 3 and resp[:2] == _HEADER and resp[2] == _CMD_RETURN_OK:
                    self.connected = True
                    return True
            except Exception as e:
                if self.debug:
                    print("Knock error:", e)
            wait(50)
        self.connected = False
        return False

    def set_alg(self, algorithm):
        content = bytes([algorithm, 0]) + struct.pack("<hhhh", 0, 0, 0, 0)
        self._cmd(_CMD_SET_ALGORITHM, 0, content)
        self.current_algorithm = algorithm
        return self.knock()

    def mode_object_recognition(self):
        return self.set_alg(ALGORITHM_OBJECT_RECOGNITION)

    def mode_face_recognition(self):
        return self.set_alg(ALGORITHM_FACE_RECOGNITION)

    def mode_line_tracking(self):
        return self.set_alg(ALGORITHM_LINE_TRACKING)

    def mode_color_recognition(self):
        return self.set_alg(ALGORITHM_COLOR_RECOGNITION)

    def mode_tag_recognition(self):
        return self.set_alg(ALGORITHM_TAG_RECOGNITION)

    def set_multi_alg(self, *algorithms):
        if len(algorithms) < 2 or len(algorithms) > 5:
            return False
        content = bytes([len(algorithms), 0])
        for i in range(4):
            content = content + struct.pack("<h", algorithms[i] if i < len(algorithms) else 0)
        self._cmd(_CMD_SET_MULTI_ALGORITHM, 0, content)
        return self.knock()

    def get(self, algorithm=None, ID=None, learned=False):
        if algorithm is None:
            algorithm = self.current_algorithm

        blocks = []
        lines = []
        faces = []
        hands = []
        poses = []

        self._cmd(_CMD_GET_RESULT, algorithm)
        wait(50)

        info = self._read_packet()
        if info and info[2] == _CMD_RETURN_INFO:
            try:
                n_results = struct.unpack("<h", info[7:9])[0]
            except Exception:
                n_results = 0

            for _ in range(n_results):
                wait(10)
                pkt = self._read_packet()
                if not pkt:
                    continue
                obj = self._parse_result(pkt, algorithm)
                if not obj:
                    continue
                if ID is not None and obj.ID != ID:
                    continue
                if learned and getattr(obj, "learned", True) is False:
                    continue
                if obj.type == "BLOCK":
                    blocks.append(obj)
                elif obj.type == "LINE":
                    lines.append(obj)
                elif obj.type == "FACE":
                    faces.append(obj)
                elif obj.type == "HAND":
                    hands.append(obj)
                elif obj.type == "POSE":
                    poses.append(obj)

        self._flush()
        return {
            BLOCKS: blocks,
            LINES: lines,
            FACES: faces,
            HANDS: hands,
            POSES: poses,
        }

    def get_blocks(self, algorithm=None, ID=None, learned=False):
        return self.get(algorithm, ID, learned)[BLOCKS]

    def get_lines(self, algorithm=None, ID=None, level=None):
        lines = self.get(algorithm, ID, learned=False)[LINES]
        if level is None:
            return lines
        return [line for line in lines if line.level == level]

    def get_current_line(self, algorithm=None):
        lines = self.get_lines(algorithm, level=1)
        return lines[0] if lines else None

    def get_branches(self, algorithm=None):
        return [line for line in self.get_lines(algorithm) if line.level != 1]

    def get_faces(self, algorithm=None, ID=None, learned=False):
        return self.get(algorithm, ID, learned)[FACES]

    def get_hands(self, algorithm=None, ID=None, learned=False):
        return self.get(algorithm, ID, learned)[HANDS]

    def get_poses(self, algorithm=None, ID=None, learned=False):
        return self.get(algorithm, ID, learned)[POSES]

    def _parse_result(self, data, algorithm):
        cmd = data[2]
        if cmd == _CMD_RETURN_ARROW:
            return self._parse_line(data)
        if len(data) < 15:
            return None

        size = data[4]
        if size < 10:
            return None

        try:
            obj_id, conf = struct.unpack("bb", data[5:7])
            x, y, w, h = struct.unpack("<hhhh", data[7:15])
        except Exception:
            return None

        name = ""
        content = ""
        offset = 15
        if size > 10 and len(data) > offset:
            try:
                name_len = data[offset]
                offset += 1
                if name_len > 0 and len(data) >= offset + name_len:
                    name = data[offset : offset + name_len].decode("utf-8")
                    offset += name_len
                if len(data) > offset:
                    content_len = data[offset]
                    offset += 1
                    if content_len > 0 and len(data) >= offset + content_len:
                        content = data[offset : offset + content_len].decode("utf-8")
                        offset += content_len
            except Exception:
                pass

        keypoints = []
        if len(data) > offset + 1:
            try:
                count = (len(data) - offset - 1) // 2
                if count > 0:
                    keypoints = list(struct.unpack("<%dh" % count, data[offset : offset + count * 2]))
            except Exception:
                pass

        if cmd == _CMD_RETURN_BLOCK:
            if algorithm == ALGORITHM_FACE_RECOGNITION and keypoints:
                return Face(x, y, w, h, obj_id, conf, name, content, keypoints)
            if algorithm == ALGORITHM_HAND_RECOGNITION and keypoints:
                return Hand(x, y, w, h, obj_id, conf, name, content, keypoints)
            if algorithm == ALGORITHM_POSE_RECOGNITION and keypoints:
                return Pose(x, y, w, h, obj_id, conf, name, content, keypoints)
            return Block(x, y, w, h, obj_id, conf, name, content)
        return None

    def _parse_line(self, data):
        if len(data) < 15 or data[2] != _CMD_RETURN_ARROW or data[4] < 10:
            return None
        obj_id, level = struct.unpack("bb", data[5:7])
        x_target, y_target, angle, length = struct.unpack("<hhhh", data[7:15])
        return Line(obj_id, level, x_target, y_target, angle, length)

    def show_text(self, text, x=10, y=10, color=COLOR_WHITE):
        txt = text.encode("utf-8")
        content = bytes([color, 0]) + struct.pack("<hhhh", x, y, 0, 0) + bytes([len(txt)]) + txt
        self._cmd(_CMD_DRAW_TEXT, 0, content)
        return self.knock()

    def clear_text(self):
        self._cmd(_CMD_CLEAR_TEXT, 0)
        return self.knock()

    def draw_rect(self, x1, y1, x2, y2, color=COLOR_WHITE):
        content = bytes([color, 0]) + struct.pack("<hhhh", x1, y1, x2, y2)
        self._cmd(_CMD_DRAW_RECT, 0, content)
        return self.knock()

    def clear_rect(self):
        self._cmd(_CMD_CLEAR_RECT, 0)
        return self.knock()


def clamp_int(value, min_val=-100, max_val=100):
    return max(min_val, min(max_val, int(value)))
