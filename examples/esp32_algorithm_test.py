from phld import HuskyLens
from machine import Pin, I2C
from time import sleep_ms

# Test multiple HuskyLens on ESP32 with I2C interface
i2c0 = I2C(0, scl=Pin(22), sda=Pin(21))
i2c1 = I2C(1, scl=Pin(20), sda=Pin(19))

hl1 = HuskyLens(i2c1, debug=True)
hl2 = HuskyLens(i2c0, debug=True)

hls = [hl1,hl2]

def get_num_blocks(hl, n=5):
    print("Get {} objects on {}".format(n, hl))
    while n > 0:
        blocks = hl.get_blocks()
        if blocks:
            print(blocks)
            n-=1
            sleep_ms(500)

def get_num_arrows(hl, n=5):
    print("Get {} objects on {}".format(n, hl))
    while n > 0:
        arrows = hl.get_arrows()
        if arrows:
            print(arrows)
            n-=1
            sleep_ms(500)
            
# Hl1 tests
hl1.knock()
hl1.mode_face_recognition()
print("Point the camera at faces")
get_num_blocks(hl1)
hl1.mode_object_recognition()
print("Point the camera at objects")
get_num_blocks(hl1)
hl1.mode_line_tracking()
print("Point the camera at lines")
get_num_arrows(hl1)
hl1.mode_color_recognition()
print("Point the camera at colors") 
get_num_blocks(hl1)
hl1.mode_tag_recognition()
print("Point the camera at tags")
sleep_ms(2000)
hl1.mode_object_classification()
print("Point the camera at objects")
get_num_blocks(hl1)

# Hl2 tests
def get_num_faces(hl, n=5):
    print("Get {} face on {}".format(n, hl))
    while n > 0:
        faces = hl.get_faces()
        if faces:
            print(faces)
            n-=1
            sleep_ms(500)
hl2.knock()
hl2.mode_face_recognition()
print("Point the camera at faces")
get_num_faces(hl2)
hl2.mode_object_recognition()
print("Point the camera at objects")
get_num_blocks(hl2)
hl2.mode_line_tracking()
print("Point the camera at lines")
get_num_arrows(hl2)
hl2.mode_color_recognition()
print("Point the camera at colors") 
get_num_blocks(hl2)
hl2.mode_tag_recognition()
print("Point the camera at tags")
sleep_ms(2000)
hl2.mode_object_classification()
print("Point the camera at objects")
get_num_blocks(hl2)