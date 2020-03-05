class Point:
    ''' 2-dimensional vector.'''
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({:4f}, {:4f})'.format(self.x, self.y)

    def __eq__(self, obj):
        return isinstance(obj, Point) and self.x == obj.x and self.y == obj.y

    def __add__(self, obj):
        if isinstance(obj, Point):
            return Point(self.x + obj.x, self.y + obj.y)
        else:
            return Point(self.x, self.y)

    def __sub__(self, obj):
        if isinstance(obj, Point):
            return Point(self.x - obj.x, self.y - obj.y)
        else:
            return Point(self.x, self.y)

    def __mul__(self, obj):
        if isinstance(obj, int) or isinstance(obj, float):
            return Point(self.x * obj, self.y * obj)
        else:
            return Point(self.x, self.y)

    def __truediv__(self, obj):
        if isinstance(obj, int) or isinstance(obj, float):
            return Point(self.x / obj, self.y / obj)
        else:
            return Point(self.x, self.y)

    def normSquared(self):
        ''' Squared value of the vector's length'''
        return self.x ** 2 + self.y ** 2

if __name__ == '__main__':
    p1 = Point(16, 14)

    str1 = "16:14"
    p2 = Point(*map(int, str1.split(':')))

    print(p1, p2, sep=' ')
    print(p1 == p2)
