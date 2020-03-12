''' References:
            https://github.com/OliBomby/Bezier-Approximation/blob/master/path_approximator.py
            https://github.com/McKay42/McOsu/blob/master/src/App/Osu/OsuSliderCurves.cpp
'''

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
        output = [[pos]]
        output[0].extend([Point(*map(int, i.split(':'))) for i in points])
        return output

    @abc.abstractmethod
    def getEndPoint(self):
        pass


class BezierSlider(Slider):
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
    def constructControlPoints(self, pos, points):
        output = [[pos]]
        output[0].extend([Point(*map(int, i.split(':'))) for i in points])
        return output

    def getEndPoint(self):
# There are cases the number of control points of linear slider is more than two.
# e.g.) Tsurupettan https://osu.ppy.sh/beatmapsets/2626#osu/19990
# Codes are needed to deal with these situation.
        len_left = self.length
        line_num = len(self.points[0]) - 1

        for i in range(line_num - 1):
            len_segment = math.sqrt((self.points[0][i + 1] - self.points[0][i]).normSquared())
            if len_segment > len_left:
                ratio = len_left / len_segment
                end = self.points[0][i] + (self.points[0][i + 1] -  self.points[0][i]) * ratio
                return end
            
            len_left -= len_segment

        ratio = len_left / math.sqrt((self.points[0][-1] - self.points[0][-2]).normSquared())
        end = self.points[0][-2] + (self.points[0][-1] - self.points[0][-2]) * ratio
        end.x = round(end.x)
        end.y = round(end.y)
        return end

# Not made yet!
class PerfectCircleSlider(Slider):
    def getEndPoint(self):
        return Point(0, 0)

# Not fully made yet!
class CatmullSlider(Slider):
    def constructControlPoints(self, pos, points):
        output = [[pos]]
        output[0].extend([Point(*map(int, i.split(':'))) for i in points])
        return output

    def getEndPoint(self):
        return self.getInterpolatedPoints()[-1]

    def constructCurvesList(self):
        curves = []
        control_points = []

        if self.points[0][0] != self.points[0][1]:
            control_points.append(self.points[0][0])
        
        for p in self.points[0]:
            control_points.append(p)

            if len(control_points) >= 4:
                curves.append(copy.copy(control_points[-4:]))
        
        if self.points[0][-1] != self.points[0][-2]:
            control_points.append(self.points[0][-1])
            curves.append(copy.copy(control_points[-4:]))

        return curves

    def getInterpolatedPoints(self):
        output = []
        curves = self.constructCurvesList()
        len_left = self.length

        # get a point in curve at time t
        getPoint = lambda t, a, b, c, d: a + b*t + c*(t**2) + d*(t**3)

        for curve in curves:
            approx_length_halfed = int(math.sqrt((curve[1] - curve[2]).normSquared()) / 2)
            coef = self.getCoefficient(curve)

            for i in range(approx_length_halfed):
                p = getPoint(i/approx_length_halfed, *coef)
                output.append(p)

        return output
        
    def getCoefficient(self, p):
        ''' get [a b c d] which can produce catmull-rom spline P(t)=a+bt+ct^2+dt^3.
            variable curve is a list of x or y coordinates, not Point objects. '''

        # Followings are double of the result.
        a =             p[1] * 2              
        b = p[0] * -1             + p[2] * 1
        c = p[0] * 2  - p[1] * 5  + p[2] * 4  - p[3]
        d = p[0] * -1 + p[1] * 3  - p[2] * 3  + p[3]

        return (a/2, b/2, c/2, d/2)

if __name__ == '__main__':
    curve1 = CatmullSlider()
    curve1.parseSliderString(input())

    output = curve1.getInterpolatedPoints()
    print(len(output))
    print(curve1.getEndPoint())
