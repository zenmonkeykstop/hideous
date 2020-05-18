import argparse
import hid
from colorsys import rgb_to_hsv

ANIM_SOLID = 1;
ANIM_PULSE = 2;

# taken from /var/lib/qubes/qubes.xml
QUBES_COLORS = {
        "red":    {"value": 0xcc0000, "animation": ANIM_SOLID },
        "orange": {"value": 0xf57900, "animation": ANIM_SOLID },
        "yellow": {"value": 0xedd400, "animation": ANIM_SOLID },
        "green":  {"value": 0x73d216, "animation": ANIM_SOLID },
        "gray":   {"value": 0x555753, "animation": ANIM_SOLID }, 
        "blue":   {"value": 0x3465a4, "animation": ANIM_SOLID }, 
        "purple": {"value": 0x482050, "animation": ANIM_SOLID }, # Qubes purple is 0x75507b but it doesn't look good imo
        "black":  {"value": 0x502050, "animation": ANIM_PULSE }, # setting LEDs to black is pretty dumb 
        "dom0":   {"value": 0x793400, "animation": ANIM_PULSE } # dom0 is the DANGER qube!
        }

def int_to_rgb(i):
    b = i % 256
    g = int( ((i-b)/256) % 256 )      # always an integer
    r = int( ((i-b)/256**2) - g/256 ) # ditto
    return (float(r)/256, float(g)/256, float(b)/256)

parser = argparse.ArgumentParser(
    description="Politely asks a USB keyboard to change its underglow to one of the predefined Qubes VM colors",
    epilog="I like trains, but I am not a fan of raw HID.")
parser.add_argument('--color', choices=list(QUBES_COLORS.keys()))

args = parser.parse_args()
print(args.color)

# default values for rev4 Iris, with hidraw backend on Linux - sub in yours!
# the Iris had 4 (countem!) usb interfaces, the relevant one was the second, 
# which maps to /dev/hidraw1 using the rawhid system assuming the keyboard is
# the only device set up
#
VENDOR_ID = 0xcb10
PRODUCT_ID = 0x4256
DEVICE_PATH = b'/dev/hidraw1'


my_color = int_to_rgb(QUBES_COLORS[args.color]["value"])
my_color = tuple(round(i * 255) for i in rgb_to_hsv(my_color[0], my_color[1], my_color[2]))
my_anim = QUBES_COLORS[args.color]["animation"]

with hid.Device(VENDOR_ID, PRODUCT_ID, path=DEVICE_PATH) as h:
    print(f'Device manufacturer: {h.manufacturer}')
    print(f'Product: {h.product}')
    print(f'Serial Number: {h.serial}')
    d = bytearray(b'\x01')
    d.extend(my_color)
    d.append(my_anim)
    print(bytes(d))
    h.write(bytes(d))
    print(h.read(5))
    h.close()
