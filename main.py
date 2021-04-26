from model import Area, Vsensor
import math
import numpy as np
from PIL import Image
from PIL import ImageDraw

new_area = Area(5, 5)
new_area.random_point(15)
print("create area suceesful, the points are in these position:")
for point in new_area.points:
    print("({}, {})".format(point.posx, point.posy), end=" |||| ")
print()
V_sensor = Vsensor(1 / 4 * math.pi, 2, new_area)
V_sensor.get_sensor()
print("Initialize the sensor position:")
for key in V_sensor.sensor_pos.keys():
    print(key, end=";")
selected = V_sensor.select_sensor()
print("\nSelected {} virtual sensors. Their position are:".format(len(selected)))
for key in selected.keys():
    print("({:.2f}, {:.2f})".format(key[0], key[1]), end="; ")
real_sensor = V_sensor.select_orientation(selected)
array = np.ndarray((100 * new_area.maxlenth, 100 * new_area.maxheight, 3), np.uint8)
array[:, :, 0] = 255
array[:, :, 1] = 255
array[:, :, 2] = 255
image = Image.fromarray(array)
draw = ImageDraw.Draw(image)

print("\nGet the position and orientaton of real sensor:")
for key, value in real_sensor.items():
    for orientation in value:
        print("pos: ({:.2}, {:.2})".format(key[0], key[1]), "ori %.2f" % orientation, end="; ")
        begin = (orientation - (1 / 2 * V_sensor.angle)) / math.pi * 180
        end = (orientation + (1 / 2 * V_sensor.angle)) / math.pi * 180
        draw.pieslice((key[0] * 100 - 100 * V_sensor.radius, key[1] * 100 - 100 * V_sensor.radius,
                       key[0] * 100 + 100 * V_sensor.radius, key[1] * 100 + 100 * V_sensor.radius), begin, end,
                      outline=(255, 0, 0))
    draw.ellipse((key[0] * 100 - 4, key[1] * 100 - 4, key[0] * 100 + 4, key[1] * 100 + 4), fill=(0, 255, 0))

for point in new_area.points:
    draw.ellipse((point.posx * 100 - 4, point.posy * 100 - 4, point.posx * 100 + 4, point.posy * 100 + 4),
                 fill=(0, 0, 255))

print("Drawing...")

image.show()
