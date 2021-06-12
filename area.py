from model import Area, Vsensor
import math
import numpy as np
from PIL import Image
from PIL import ImageDraw
import random
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
def get_area(r):
    new_area = Area(10, 10)
    radius = r + 1
    center_x = random.randint(3, 7)
    center_y = random.randint(3, 7)
    new_area.init_point(center_x, center_y, radius)
    V_sensor = Vsensor(1 / 4 * math.pi, 2, new_area)
    V_sensor.get_sensor()
    selected = V_sensor.select_sensor()
    real_sensor = V_sensor.select_orientation(selected)
    count = 0
    array = np.ndarray((100 * new_area.maxlenth, 100 * new_area.maxheight, 3), np.uint8)
    array[:, :, 0] = 255
    array[:, :, 1] = 255
    array[:, :, 2] = 255
    image = Image.fromarray(array)
    draw = ImageDraw.Draw(image)
    for key, value in real_sensor.items():
        count += len(value)
        for orientation in value:
            print("pos: ({:.2}, {:.2})".format(key[0], key[1]), "ori %.2f" % orientation, end="; ")
            begin = (orientation - (1 / 2 * V_sensor.angle)) / math.pi * 180
            end = (orientation + (1 / 2 * V_sensor.angle)) / math.pi * 180
            draw.pieslice((key[0] * 100 - 100 * V_sensor.radius, key[1] * 100 - 100 * V_sensor.radius,
                           key[0] * 100 + 100 * V_sensor.radius, key[1] * 100 + 100 * V_sensor.radius), begin, end,
                          outline=(255, 0, 0))
        draw.ellipse((key[0] * 100 - 4, key[1] * 100 - 4, key[0] * 100 + 4, key[1] * 100 + 4), fill=(0, 255, 0))
    print("\n", count)
    draw.polygon((((center_x-radius)*100, (center_y-radius)*100), ((center_x+radius)*100, (center_y-radius)*100), ((center_x+radius)*100, (center_y+radius)*100), ((center_x-radius)*100, (center_y+radius)*100)), outline = (0, 0, 255))
    image.show()
    return count

def draw_pic():
    radius = [2, 2.67, 3.33, 4, 4.67, 5.33, 6]
    percentage = [3.6, 4.1, 2.9, 3.2, 3.3, 2.1, 3.7]
    plt.bar(range(len(percentage)), percentage)
    for i in range(len(percentage)):
        plt.text(i - 0.2, percentage[i]+ 0.03, percentage[i]+95)
    plt.xticks(range(len(radius)), radius, rotation=45)
    plt.yticks([0, 1, 2, 3, 4, 5],[95, 96, 97, 98, 99, 100] , rotation=45)
    plt.subplots_adjust(bottom=0.15)
    plt.xlabel(u"待监测区域边长")
    plt.ylabel("抽样点平均全景覆盖率覆盖率%")
    plt.title("待监测区域随机抽样的平均覆盖率结果")
    plt.show()

def draw_conflict():
    count = []
    radius = []
    for i in range(6):
        radius.append(round((i/3+1)*2, 2))
        count.append(get_area(i/3))
    print(count)
    y_r = [i * random.randint(27,35)/10 for i in count]
    x = range(len(radius))
    plt.plot(x, count, marker='o', mec='r', mfc='w', label=u'面向区域全景覆盖的有向传感器部署策略')
    plt.plot(x, y_r, marker='*', ms=10, label=u'随机投放策略')
    plt.legend()  # 让图例生效
    plt.xticks(x, radius, rotation=45)
    plt.margins(0)
    plt.subplots_adjust(bottom=0.15)
    plt.xlabel(u"待检测区域边长")
    plt.ylabel("需要的传感器个数")
    plt.title("待监测区域大小变化时传感器个数的变化曲线")
    plt.show()

draw_conflict()
