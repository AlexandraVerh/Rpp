class IncorrectTriangleSides(Exception):
    pass

class Triangle:
    def __init__(self, a, b, c):#Он проверяет, что переданные стороны треугольника являются положительными числами и что они могут образовать треугольник.
        # Если проверки не выполняются, вызывается исключение
        # "self" используется для обращения к текущему экземпляру объекта
        if a <= 0 or b <= 0 or c <= 0:
            raise IncorrectTriangleSides("Длина сторон должна быть положительной")
        if a + b <= c or a + c <= b or b + c <= a:
            raise IncorrectTriangleSides("Длины сторон не образуют треугольника")
        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):#используется для определения типа треугольника на основе длин его сторон
        #"self" используется для обращения к текущему экземпляру объекта
        if self.a == self.b and self.b == self.c:
            return "equilateral"
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"
        else:
            return "nonequilateral"

    def perimeter(self):
        return self.a + self.b + self.c


