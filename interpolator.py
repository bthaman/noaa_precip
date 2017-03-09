class Interpolator:
    def __init__(self):
        self.known_x = None
        self.interp_y = None
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

    def interpolate(self, known_x, x1, x2, y1, y2):
        self.known_x = float(known_x)
        self.x1 = float(x1)
        self.x2 = float(x2)
        self.y1 = float(y1)
        self.y2 = float(y2)

        self.interp_y = (self.known_x - self.x1) / (self.x2 - self.x1) * (self.y2 - self.y1) + self.y1
        return self.interp_y

if __name__ == '__main__':
    interp = Interpolator()
    result = interp.interpolate(3.14159, 1, 10, 100, 1000)
    print(result)

