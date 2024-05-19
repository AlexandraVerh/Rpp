class IncorrectTriangleSides(Exception):
    pass


def get_triangle_type(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("Длина сторон должна быть положительной")
    if a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Длины сторон не образуют треугольника")
    if a == b and b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"




