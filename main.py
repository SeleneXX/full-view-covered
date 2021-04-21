import random, math, collections
full_view_angle = 1/3*math.pi       #设置全景角度为60°

class point():      #待检测点类
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.cover = 0        #被摄像头覆盖的数目
        self.coverrate = 0      #全景覆盖率

class sensor():
    def __init__(self, radius, orientation, angel, posx, posy):
        self.radius = radius
        self.orientation = orientation
        self.angle = angel
        self.posx = posx
        self.posy = posy


    def is_covered(self, pointx, pointy):
        d2 = (self.posx - pointx)**2 + (self.posy - pointy)**2
        k = (self.posy - pointy) / (self.posx - pointx)
        ANG = abs(math.atan(k) - self.orientation)
        if ANG <= self.angle and self.radius**2 >= d2:
            return True
        else:
            return False

    def is_full_view_covered(self, pointx, pointy, point_orientation):
        k = (self.posy - pointy) / (self.posx - pointx)
        ANG = abs(math.atan(k) - point_orientation)
        if ANG <= full_view_angle and self.is_covered(pointx, pointy):
            return True
        else:
            return False



class area():
    def __init__(self, lenth, height):
        self.maxlenth = lenth
        self.maxheight = height
        self.points = []


    def random_point(self, points_nums):
         while len(self.points) < points_nums:
            new_point = point(random.random(self.minlenth, self.maxlenth), random.random(self.minheight, self.maxheight))
            self.points.append(new_point)


    def clear_area(self):
        self.points = []



class vsensor():        #虚拟摄像头类，也就是圆形覆盖模型
    def __init__(self, sensor, area):
        self.angle = sensor.angle
        self.radius = sensor.radius
        self.width = area.maxlenth
        self.height = area.maxheight
        self.points = area.points
        self.all_contri = 0
        self.sensor_pos = collections.defaultdict(list)


    def get_sensor(self):       #初始化得到能覆盖到点的所有摄像头，位置为均匀分布
        for i in range(self.width + 1):
            for j in range(self.height + 1):
                for point in self.points:
                    if (i - point.posx)**2 + (j - point.posy)**2 <= self.radius**2:
                        self.sensor_pos[(i, j)].append(point)


    def select_sensor(self):         #使用贪心法，每一次循环计算出当前摄像头集合中，对全景覆盖率贡献最大的摄像头，直到覆盖率满
        def merge(intervals):           #区间合并函数，用于计算待检测点在加入一个新的摄像头后的覆盖区间，方便计算覆盖率
            if len(intervals) == 0:
                return []

            res = []
            intervals = list(sorted(intervals))

            low = intervals[0][0]
            high = intervals[0][1]

            for i in range(1, len(intervals)):
                # 若当前区间和目前保存区间有交集，则进行判断后修改相应的区间参数；若当前区间和目前保存区间没有交集，则将目前保存区间放入到结果集合中，并将当前区间记录成目前保存区间
                if high >= intervals[i][0]:
                    if high < intervals[i][1]:
                        high = intervals[i][1]
                else:
                    res.append([low, high])
                    low = intervals[i][0]
                    high = intervals[i][1]

            res.append([low, high])
            return res

        sensor_selected = {}        #贪心法选择的摄像头，key值为摄像头坐标，value值为覆盖的结点
        while self.all_contri < len(self.points):           #循环直到覆盖率满
            contri_dict = collections.defaultdict(float)        #记录每一次循环摄像头集合中的每一个摄像头的覆盖率
            for key, values in self.sensor_pos.items():     #第二层循环，计算加入当前摄像头对每个待检测点覆盖率产生的影响
                whole_diff = 0      #当前摄像头所创造的覆盖率增加
                for point in values:        #第三层循环，对于当前摄像头覆盖的每一个点，计算其新增的覆盖区间，计算增加的覆盖率
                    k = (point.posy - key[1]) / (point.posx - key[0])              #计算新增的覆盖区加
                    ANG = math.atan(k)
                    lowbound = ANG - 0.5*full_view_angle
                    upbound = ANG + 0.5*full_view_angle
                    if lowbound < 0:
                        point.cover.append([lowbound + 2*math.pi, 2*math.pi])
                        point.cover.append([0, upbound])
                    elif upbound > 2*math.pi:
                        point.cover.append([lowbound, 2*math.pi])
                        point.cover.append([0, upbound - 2*math.pi])
                    else:
                        point.cover.append([lowbound, upbound])
                    point.cover = merge(point.cover)            #合并新增的区间和旧的区间
                    percent = 0
                    for interval in point.cover:            #计算覆盖率
                        interv = interval[1] - interval[0]
                        percent += interv / math.pi*2
                    diff = percent - point.coverrate            #获得当前待检测点所产生的覆盖率差距
                    point.coverrate = percent
                    whole_diff += diff              #累加
                contri_dict[key] = whole_diff       #记录当前结点产生的覆盖率差距
            a = sorted(contri_dict.items(), key=lambda x:x[1], reverse=True)         #排序，按照覆盖率差距降序
            sensor_selected[a[0]] = self.sensor_pos[a[0]]       #贪心选择覆盖率差距最大的摄像头，加入选择集合，同时记录其覆盖的待检测点
            self.all_contri += a[1]             #增加覆盖率差距
            del contri_dict[a[0]]               #删除该摄像头，避免重复运算
        return sensor_selected


    def select_orientation(self, virtuesensors):
        real_sensor = {}
        for sensor, covered_points in virtuesensors.items():
            pre_covered = []
            point_ANG = []
            for point in covered_points:
                k = (point.posy - sensor[1]) / (point.posx - sensor[0])
                ANG_begin = math.atan(k)
                point_ANG.append([point, ANG_begin])
                ANG_end = ANG_begin + self.angle
                if ANG_end > 2 * math.pi:
                    pre_covered.append([ANG_begin, 2 * math.pi])
                    pre_covered.append([0, ANG_end - 2 * math.pi])
                else:
                    pre_covered.append([ANG_begin, ANG_end])

            point_ANG = sorted(point_ANG, key=lambda x: x[1])
            cover_list = []
            for ANGLE in point_ANG:
                cover_num = 0
                for interval in pre_covered:
                    if ANGLE[1] >= interval[0] and ANGLE[1] <= interval[1]:
                        cover_num += 1
                cover_list.append(cover_num)
            mini = 100
            mini_index = 0
            for i in range(len(cover_list)):
                if mini > cover_list[i]:
                    mini = cover_list[i]
                    mini_index = i
            cover_interval = [[point_ANG[mini_index][1], point_ANG[mini_index][1] + self.angle]]
            now_index = mini_index
            while True:
                now_index += 1
                if now_index == len(point_ANG):
                    now_index -= len(point_ANG)
                if now_index == mini_index:
                    break
                if point_ANG[now_index][1] >= cover_interval[-1][1]:
                    cover_interval.append([point_ANG[now_index][1], point_ANG[now_index][1] + self.angle])
            angles = []
            for interval in cover_interval:
                angle = interval[0] + 0.5*self.angle
                if angle > 2*math.pi:
                    angle -= 2*math.pi
                angles.append(angle)
            real_sensor[sensor] = angles
        return real_sensor


