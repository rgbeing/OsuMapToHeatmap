import copy
import abc
import math
from point import Point

BEZIER_TOLERANCE = 0.25

class Slider(metaclass = abc.ABCMeta):
    __slots__ = ['pos', 'time', 'obj_type', 'curve_type', 'points', 'length']

    def __init__(self, **kwargs):
        self.pos = kwargs['pos'] if 'pos' in kwargs else None
        self.time = kwargs['time'] if 'time' in kwargs else None
        self.obj_type = kwargs['obj_type'] if 'obj_type' in kwargs else None
        self.curve_type = kwargs['curve_type'] if 'curve_type' in kwargs else None
        self.points = kwargs['points'] if 'points' in kwargs else None
        self.length = kwargs['length'] if 'length' in kwargs else None

    def parseSliderString(self, line):
        line = line.split(',')
        points = line[5].split('|')

        self.pos = Point(int(line[0]), int(line[1]))
        self.time = int(line[2])
        self.obj_type = int(line[3])
        self.curve_type = points.pop(0)
        self.points = self.constructControlPoints(self.pos, points)
        self.length = float(line[7])

    def constructControlPoints(self, pos, points):
        control_points = [[pos]]
        points = [Point(*map(int, i.split(':'))) for i in points]

        curve_num = 1
        for pt in points:
            if control_points[curve_num - 1][-1] == pt:
                control_points.append([pt])
                curve_num += 1
            else:
                control_points[curve_num - 1].append(pt)
        
        return control_points

    @abc.abstractmethod
    def getEndPoint(self):
        pass


class BezierSlider(Slider):
    def getEndPoint(self):
        return self.getApproximatedPoints()[-1]

    def getApproximatedPoints(self):
        output = []
        buf = []
        len_left = self.length

        for curve in self.points:
            deg = len(curve) - 1

            # A line(1d bezier)
            if (deg == 1):
                output.append(curve[0])
                if (curve[0] - curve[1]).normSquared() > len_left ** 2:
                    output.append(LinearSlider(length=len_left, points=[curve]).getEndPoint())
                else:
                    output.append(curve[1])
                len_left -= math.sqrt((curve[0] - curve[1]).normSquared())
                continue

            buf = BezierSlider.approximateBezier(curve)
            idx_start = 2 if deg % 2 == 0 else 1

# I used a cutdown polygon here to construct approximated bezier sliders but
# Osu uses a quasi-control polygon to construct the approximation.
# Then why I am using a cutdown polygon?
# To get a quasi-control polygon, additional computations are needed,
# but coding it is hassle for me lol
# and not only that, the number of edges to approximate the curve can be reduced.
# I don't need accurate coordinates, so I just compromised :)
# If you wonder what is a cutdown polygon, you can find it on the following paper: doi:10.1016/j.cagd.2008.08.002

            output.append(buf[0][0])
            for aprx_curve in buf:
                for i in range(idx_start, deg + 1, 2):
                    if math.sqrt((output[-1] - aprx_curve[i]).normSquared()) > len_left:
                        break
                    else:
                        output.append(aprx_curve[i])
                        len_left -= math.sqrt((output[-1] - output[-2]).normSquared())

            if len_left <= 0:
                break

        return output

    @staticmethod
    def subdivide(parent, r):
        num = len(parent)
        mid = copy.deepcopy(parent)
        l = parent

        for i in range(num):
            l[i] = copy.copy(mid[0])
            r[num - i - 1] = copy.copy(mid[num - i - 1])

            for j in range(num - i - 1):
                mid[j] = (mid[j] + mid[j + 1]) / 2

    @staticmethod
    def approximateBezier(control_points, test_needed = True):
        ''' test_needed: boolean value that shows if it is needed to call isFlatEnough function'''
        toFlatten = [copy.copy(control_points)]
        output = []

        if test_needed:
            while len(toFlatten) > 0:
                parent = toFlatten.pop(0)
                
                if BezierSlider.isFlatEnough(parent):
                    output.append(parent)
                else:
                    child = [None] * len(parent)
                    BezierSlider.subdivide(parent, child)
                    toFlatten.insert(0, child)
                    toFlatten.insert(0, parent)           
        else:
            while len(toFlatten) > 0:
                parent = toFlatten.pop(0)
                child = [None] * len(parent)
                BezierSlider.subdivide(parent, child)
                output.extend((parent, child))

        return output

# As it use cutdown polygon to approximate, this flatness test is needed to be modified.
# But I have no idea for this... and its approximations are accurate enough for now!
    @staticmethod
    def isFlatEnough(control_points):
        if len(control_points) <= 2:
            return True
        for i in range(1, len(control_points) - 1):
            p = control_points[i - 1] - control_points[i] * 2 + control_points[i + 1]
        if p.normSquared() > BEZIER_TOLERANCE * BEZIER_TOLERANCE * 4:
            return False
        return True

class LinearSlider(Slider):
    def getEndPoint(self):
        ratio = self.length / math.sqrt((self.points[0][1] - self.points[0][0]).normSquared())
        end = self.points[0][0] + (self.points[0][1] - self.points[0][0]) * ratio
        end.x = round(end.x)
        end.y = round(end.y)
        return end

# Not made yet!
class PerfectCircleSlider(Slider):
    def getEndPoint(self):
        return Point(0, 0)


if __name__ == '__main__':
    curve1 = BezierSlider()
    curve1.parseSliderString(input())
    output = curve1.getEndPoint()

    print(output)
