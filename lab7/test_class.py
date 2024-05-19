import pytest
from triangle_class import IncorrectTriangleSides, Triangle

def test_equilateral():
    t = Triangle(3, 3, 3)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 9

def test_isosceles():
    t = Triangle(3, 4, 3)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 10

def test_nonequilateral():
    t = Triangle(3, 4, 5)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 12

def test_incorrect_sides_negative():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 3)

def test_incorrect_sides_zero():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 2, 3)

def test_incorrect_sides_not_triangle():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 1, 3)

def test_perimeter():
    t = Triangle(3, 4, 5)
    assert t.perimeter() == 12

