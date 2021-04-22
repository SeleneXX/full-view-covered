from model import area, vsensor, sensor, point
import math
new_area = area(10, 10)
new_area.random_point(1)
print("create area suceesful, the points are in these position:")
for point in new_area.points:
    print("({}, {})".format(point.posx, point.posy), end=" |||| ")
print()
V_sensor = vsensor(1/4*math.pi, 4, new_area)
V_sensor.get_sensor()
print("Initialize the sensor position:")
for key in V_sensor.sensor_pos.keys():
    print(key, end=";")
selected = V_sensor.select_sensor()
print("\nSelected {} sensors. Their position are:".format(len(selected)))
for key in selected.keys():
    print("({:.2f}, {:.2f})".format(key[0], key[1]), end="; ")
real_sensor = V_sensor.select_orientation(selected)
print("\nGet the position and orientaton of real sensor:")
for key, value in real_sensor.items():
    for orientation in value:
        print("pos: ({:.2}, {:.2})".format(key[0], key[1]), "ori %.2f" %orientation, end="; ")

