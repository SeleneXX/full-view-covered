import collections
import copy
import math
import random

full_view_angle = 1 / 3 * math.pi


def get_angle(v1):
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = 1
    dy2 = 0
    angle1 = math.atan2(dy1, dx1)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    # print(angle2)
    included_angle = angle1 - angle2
    return included_angle


class Point:  # 待检测点类
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.cover = []
        self.coverrate = 0  # 全景覆盖率


class Sensor:
    def __init__(self, radius, orientation, angel, posx, posy):
        self.radius = radius
        self.orientation = orientation
        self.angle = angel
        self.posx = posx
        self.posy = posy

    def is_covered(self, pointx, pointy):
        d2 = (self.posx - pointx) ** 2 + (self.posy - pointy) ** 2
        k = (self.posy - pointy) / (self.posx - pointx)
        ang = abs(math.atan(k) - self.orientation)
        if ang <= self.angle and self.radius ** 2 >= d2:
            return True
        else:
            return False

    def is_full_view_covered(self, pointx, pointy, point_orientation):
        k = (self.posy - pointy) / (self.posx - pointx)
        ang = abs(math.atan(k) - point_orientation)
        if ang <= full_view_angle and self.is_covered(pointx, pointy):
            return True
        else:
            return False


class Area:
    def __init__(self, lenth, height):
        self.maxlenth = lenth
        self.maxheight = height
        self.points = []

    def random_point(self, points_nums):
        while len(self.points) < points_nums:
            new_point = Point(round(random.uniform(1, self.maxlenth - 1), 2),
                              round(random.uniform(1, self.maxheight - 1), 2))
            self.points.append(new_point)

    def init_point(self, center_x, center_y, radius):
        for a in range(0, self.maxlenth*3):
            for b in range(0, self.maxheight*3):
                if abs(center_y - b/3) <= radius and abs(center_x - a/3) <= radius:
                    new_point = Point(a/3, b/3)
                    self.points.append(new_point)

    def clear_area(self):
        self.points = []


class Vsensor:  # 虚拟摄像头类，也就是圆形覆盖模型
    def __init__(self, angle, radius, area):
        self.angle = angle
        self.radius = radius
        self.width = area.maxlenth
        self.height = area.maxheight
        self.points = area.points
        self.all_contri = 0
        self.sensor_pos = collections.defaultdict(list)


    def get_sensor(self):  # 初始化得到能覆盖到点的所有摄像头，位置为均匀分布
        for i in range((self.width + 1) * 3):
            for j in range((self.height + 1) * 3):
                for point in self.points:
                    if (i / 3 - point.posx) ** 2 + (j / 3 - point.posy) ** 2 <= self.radius ** 2:
                        self.sensor_pos[(i / 3, j / 3)].append(point)

    def clear_sensor(self):
        self.sensor_pos = collections.defaultdict(list)
        self.all_contri = 0


    def select_sensor(self):  # 使用贪心法，每一次循环计算出当前摄像头集合中，对全景覆盖率贡献最大的摄像头，直到覆盖率满
        def merge(intervals):  # 区间合并函数，用于计算待检测点在加入一个新的摄像头后的覆盖区间，方便计算覆盖率
            if len(intervals) == 0:
                return []
            res = []
            intervals = list(sorted(intervals))
            low = intervals[0][0]
            high = intervals[0][1]
            for innterval in range(1, len(intervals)):
                # 若当前区间和目前保存区间有交集，则进行判断后修改相应的区间参数；若当前区间和目前保存区间没有交集，则将目前保存区间放入到结果集合中，并将当前区间记录成目前保存区间
                if high >= intervals[innterval][0]:
                    if high < intervals[innterval][1]:
                        high = intervals[innterval][1]
                else:
                    res.append([low, high])
                    low = intervals[innterval][0]
                    high = intervals[innterval][1]
            res.append([low, high])
            return res

        sensor_selected = {}  # 贪心法选择的摄像头，key值为摄像头坐标，value值为覆盖的结点

        while len(self.points) - self.all_contri > 0.05 * len(self.points):  # 循环直到覆盖率满
            contri_dict = collections.defaultdict(float)  # 记录每一次循环摄像头集合中的每一个摄像头的覆盖率
            for key, values in self.sensor_pos.items():  # 第二层循环，计算加入当前摄像头对每个待检测点覆盖率产生的影响
                if key in sensor_selected.keys():
                    continue
                whole_diff = 0  # 当前摄像头所创造的覆盖率增加
                pointcover = []
                for point in values:  # 第三层循环，对于当前摄像头覆盖的每一个点，计算其新增的覆盖区间，计算增加的覆盖率
                    origin_cover = copy.deepcopy(point.cover)
                    k = [key[0], key[1], point.posx, point.posy]  # 计算新增的覆盖区加
                    ang = get_angle(k)
                    if ang < 0:
                        ang += 2 * math.pi
                    lowbound = ang - 0.5 * full_view_angle
                    upbound = ang + 0.5 * full_view_angle
                    if lowbound < 0:
                        point.cover.append([lowbound + 2 * math.pi, 2 * math.pi])
                        point.cover.append([0, upbound])
                    elif upbound > 2 * math.pi:
                        point.cover.append([lowbound, 2 * math.pi])
                        point.cover.append([0, upbound - 2 * math.pi])
                    else:
                        point.cover.append([lowbound, upbound])
                    point.cover = merge(point.cover)  # 合并新增的区间和旧的区间
                    percent = 0
                    for interval in point.cover:  # 计算覆盖率
                        interv = interval[1] - interval[0]
                        twopi = math.pi * 2
                        percent += interv / twopi
                    diff = percent - point.coverrate  # 获得当前待检测点所产生的覆盖率差距
                    whole_diff += diff  #
                    cover_interval = copy.deepcopy(point.cover)
                    pointcover.append([point, percent, cover_interval])
                    point.cover = origin_cover
                contri_dict[key] = (whole_diff, pointcover)  # 记录当前结点产生的覆盖率差距
            new = list(contri_dict.items())
            for i in range(len(new)):
                new[i] = list(new[i])
                new[i].append(new[i][0][0] ** 2 + new[i][0][1] ** 2)
            a = sorted(new, key=lambda x: (-x[1][0], x[2]))  # 排序，按照覆盖率差距降序
            sensor_selected[a[0][0]] = self.sensor_pos[a[0][0]]  # 贪心选择覆盖率差距最大的摄像头，加入选择集合，同时记录其覆盖的待检测点
            self.all_contri += a[0][1][0]  # 增加覆盖率差距
            for point in a[0][1][1]:
                point[0].coverrate = point[1]
                point[0].cover = point[2]
        return sensor_selected

    def select_orientation(self, virtuesensors):
        real_sensor = {}
        for sensor, covered_points in virtuesensors.items():
            pre_covered = []
            point_ang = []
            for point in covered_points:
                k = [sensor[0], sensor[1], point.posx, point.posy]
                ang_begin = get_angle(k)
                if ang_begin < 0:
                    ang_begin += 2 * math.pi
                point_ang.append([point, ang_begin])
                ang_end = ang_begin + self.angle
                if ang_end > 2 * math.pi:
                    pre_covered.append([ang_begin, 2 * math.pi])
                    pre_covered.append([0, ang_end - 2 * math.pi])
                else:
                    pre_covered.append([ang_begin, ang_end])

            point_ang = sorted(point_ang, key=lambda x: x[1])
            cover_list = []
            for ANGLE in point_ang:
                cover_num = 0
                for interval in pre_covered:
                    if interval[0] <= ANGLE[1] <= interval[1]:
                        cover_num += 1
                cover_list.append(cover_num)
            mini = 100
            mini_index = 0
            for i in range(len(cover_list)):
                if mini > cover_list[i]:
                    mini = cover_list[i]
                    mini_index = i
            cover_interval = [[point_ang[mini_index][1], point_ang[mini_index][1] + self.angle]]
            now_index = mini_index
            while True:
                now_index += 1
                if now_index == len(point_ang):
                    now_index -= len(point_ang)
                if now_index == mini_index:
                    break
                if point_ang[now_index][1] >= cover_interval[-1][1]:
                    cover_interval.append([point_ang[now_index][1], point_ang[now_index][1] + self.angle])
            angles = []
            for interval in cover_interval:
                angle = interval[0] + 0.5 * self.angle
                if angle > 2 * math.pi:
                    angle -= 2 * math.pi
                angles.append(angle)
            real_sensor[sensor] = angles
        return real_sensor

    def random_throwin(self):
        #首先初始化该区域
        for point in self.points:
            point.cover = []
            point.coverrate = 0
        self.all_contri = 0
        def merge(intervals):  # 区间合并函数，用于计算待检测点在加入一个新的摄像头后的覆盖区间，方便计算覆盖率
            if len(intervals) == 0:
                return []
            res = []
            intervals = list(sorted(intervals))
            low = intervals[0][0]
            high = intervals[0][1]
            for innterval in range(1, len(intervals)):
                # 若当前区间和目前保存区间有交集，则进行判断后修改相应的区间参数；若当前区间和目前保存区间没有交集，则将目前保存区间放入到结果集合中，并将当前区间记录成目前保存区间
                if high >= intervals[innterval][0]:
                    if high < intervals[innterval][1]:
                        high = intervals[innterval][1]
                else:
                    res.append([low, high])
                    low = intervals[innterval][0]
                    high = intervals[innterval][1]
            res.append([low, high])
            return res

        sensor_selected = {}  # 贪心法选择的摄像头，key值为摄像头坐标，value值为覆盖的结点

        while len(self.points) - self.all_contri > 0.05 * len(self.points):  # 循环直到覆盖率满
            key = random.choice(list(self.sensor_pos.keys()))
            values = self.sensor_pos[key]
            if key in sensor_selected.keys():
                continue
            whole_diff = 0  # 当前摄像头所创造的覆盖率增加
            for point in values:  # 第三层循环，对于当前摄像头覆盖的每一个点，计算其新增的覆盖区间，计算增加的覆盖率
                k = [key[0], key[1], point.posx, point.posy]  # 计算新增的覆盖区加
                ang = get_angle(k)
                if ang < 0:
                    ang += 2 * math.pi
                lowbound = ang - 0.5 * full_view_angle
                upbound = ang + 0.5 * full_view_angle
                if lowbound < 0:
                    point.cover.append([lowbound + 2 * math.pi, 2 * math.pi])
                    point.cover.append([0, upbound])
                elif upbound > 2 * math.pi:
                    point.cover.append([lowbound, 2 * math.pi])
                    point.cover.append([0, upbound - 2 * math.pi])
                else:
                    point.cover.append([lowbound, upbound])
                point.cover = merge(point.cover)  # 合并新增的区间和旧的区间
                percent = 0
                for interval in point.cover:  # 计算覆盖率
                    interv = interval[1] - interval[0]
                    twopi = math.pi * 2
                    percent += interv / twopi
                diff = percent - point.coverrate  # 获得当前待检测点所产生的覆盖率差距
                point.coverrate = percent
                whole_diff += diff  #
            self.all_contri += whole_diff
            sensor_selected[key] = values
        return sensor_selected

    def random_select_orientation(self, virtuesensors):
        real_sensor = {}
        for sensor, covered_points in virtuesensors.items():
            pre_covered = []
            point_ang = []
            for point in covered_points:
                k = [sensor[0], sensor[1], point.posx, point.posy]
                ang_begin = get_angle(k)
                if ang_begin < 0:
                    ang_begin += 2 * math.pi
                point_ang.append([point, ang_begin])
                ang_end = ang_begin + self.angle
                if ang_end > 2 * math.pi:
                    pre_covered.append([ang_begin, 2 * math.pi])
                    pre_covered.append([0, ang_end - 2 * math.pi])
                else:
                    pre_covered.append([ang_begin, ang_end])

            point_ang = sorted(point_ang, key=lambda x: x[1])
            cover_list = []
            for ANGLE in point_ang:
                cover_num = 0
                for interval in pre_covered:
                    if interval[0] <= ANGLE[1] <= interval[1]:
                        cover_num += 1
                cover_list.append(cover_num)
            mini = 100
            mini_index = 0
            for i in range(len(cover_list)):
                if mini > cover_list[i]:
                    mini = cover_list[i]
                    mini_index = i
            cover_interval = [[point_ang[mini_index][1], point_ang[mini_index][1] + self.angle]]
            now_index = mini_index
            while True:
                now_index += 1
                if now_index == len(point_ang):
                    now_index -= len(point_ang)
                if now_index == mini_index:
                    break
                if point_ang[now_index][1] >= cover_interval[-1][1]:
                    cover_interval.append([point_ang[now_index][1], point_ang[now_index][1] + self.angle])
            angles = []
            for interval in cover_interval:
                angle = interval[0] + 0.5 * self.angle
                if angle > 2 * math.pi:
                    angle -= 2 * math.pi
                angles.append(angle)
            real_sensor[sensor] = angles
        return real_sensor

class Area_seperate:
    def __init__(self, lenth, height, sensor):
        self.lenth = lenth
        self.height = height
        self.radius = sensor.radius


    def seperate(self):
        self.lenth = 1



