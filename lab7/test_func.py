import unittest#предоставляет инфраструктуру для написания и запуска тестов предоставляет инфраструктуру для написания и запуска тестов
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestTriangleType(unittest.TestCase):
    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")
        #используется для сравнения двух значений и утверждения, что они равны

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(6, 6, 8), "isosceles")
        # используется для сравнения двух значений и утверждения, что они равны
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(9, 9, 9), "equilateral")
        # используется для сравнения двух значений и утверждения, что они равны

    def test_negative_side_length(self):
        with self.assertRaises(IncorrectTriangleSides) as cm:
            #используется для проверки, что при выполнении определенной операции будет выброшено исключение определенного типа.
            # self.assertRaises() помогает убедиться, что  код правильно обрабатывает исключения в различных сценариях
            get_triangle_type(0, 4, 5)
        self.assertEqual(str(cm.exception), "Длина сторон должна быть положительной")
        # используется для сравнения двух значений и утверждения, что они равны

        with self.assertRaises(IncorrectTriangleSides) as cm:
            # self.assertRaises() помогает убедиться, что  код правильно обрабатывает исключения в различных сценариях
            get_triangle_type(3, -4, 5)
        self.assertEqual(str(cm.exception), "Длина сторон должна быть положительной")
        # используется для сравнения двух значений и утверждения, что они равны

        with self.assertRaises(IncorrectTriangleSides) as cm:
            # self.assertRaises() помогает убедиться, что  код правильно обрабатывает исключения в различных сценариях
            get_triangle_type(3, 4, 0)
        self.assertEqual(str(cm.exception), "Длина сторон должна быть положительной")
        # используется для сравнения двух значений и утверждения, что они равны

    def test_incorrect_side_lengths(self):
        with self.assertRaises(IncorrectTriangleSides) as cm:
            # self.assertRaises() помогает убедиться, что  код правильно обрабатывает исключения в различных сценариях
            get_triangle_type(1, 1, 3)
        self.assertEqual(str(cm.exception), "Длины сторон не образуют треугольника")
        # используется для сравнения двух значений и утверждения, что они равны

        with self.assertRaises(IncorrectTriangleSides) as cm:
            # self.assertRaises() помогает убедиться, что  код правильно обрабатывает исключения в различных сценариях
            get_triangle_type(3, 4, 10)
        self.assertEqual(str(cm.exception), "Длины сторон не образуют треугольника")
        # используется для сравнения двух значений и утверждения, что они равны

if __name__ == '__main__':
    unittest.main()
