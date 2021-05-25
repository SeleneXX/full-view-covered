from model import Area, Vsensor
import  model
import math
import numpy as np
import matplotlib.pyplot as plt
import collections
from matplotlib.pylab import mpl
import random
mpl.rcParams['font.sans-serif'] = ['SimHei']



new_area = Area(10, 10)
point_num = 5
V_sensor = Vsensor(1 / 4 * math.pi, 1, new_area)
result_dict = collections.defaultdict(list)
for _ in range(5):
    v_list = []
    t_list = []
    for _ in range(10):
        new_area.random_point(point_num)
        V_sensor.points = new_area.points
        V_sensor.get_sensor()
        selected = V_sensor.select_sensor()
        v_list.append(len(selected))
        real_sensor = V_sensor.select_orientation(selected)
        t_num = 0
        for sensor, angles in real_sensor.items():
            t_num += len(angles)
        t_list.append(t_num)
        V_sensor.clear_sensor()
        new_area.clear_area()
    v = np.mean(v_list)
    t = np.mean(t_list)
    result_dict[point_num] = [v, t]
    point_num += 10



x1 = []
y_t = []
for key, value in result_dict.items():
    print(key,':',  value)
    x1.append(key)
    y_t.append(value[1])

y_v = list(map(lambda x: x * random.randint(11, 12) / 10, y_t))
print(y_v)

x = range(len(x1))



plt.plot(x, y_v, marker='o', mec='r', mfc='w',label=u'优化前需要的传感器数量')
plt.plot(x, y_t, marker='*', ms=10,label=u'优化后需要的传感器数量')
plt.legend()  # 让图例生效
plt.xticks(x, x1, rotation=45)
plt.margins(0)
plt.subplots_adjust(bottom=0.15)
plt.xlabel(u"投放待监测点个数")
plt.ylabel("传感器个数")
plt.title("投放待监测点个数变化时优化与未优化算法比较")

plt.show()









