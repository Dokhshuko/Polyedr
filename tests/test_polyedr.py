import unittest
from unittest.mock import patch, mock_open

from shadow.polyedr import Polyedr, Facet, Edge, Segment
from common.r3 import R3
from common.tk_drawer import TkDrawer
from math import *

tk = TkDrawer()


class TestPolyedr(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """10.0  0.0  0.0  0.0
8  2  8
1   1   1
3   1   1
3   3   1
1   3   1
1.5 1.5 0
2   1.5 0
2   2   0
1.5 2   0
4  1    2    3    4
4  5    6    7    8"""
        fake_file_path = 'data/holey_box.geom'
        with (patch('shadow.polyedr.open',
                    new=mock_open(read_data=fake_file_content)) as _file):
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.assertEqual(len(self.polyedr.vertexes), 8)

    def test_num_facets(self):
        self.assertEqual(len(self.polyedr.facets), 2)

    def test_num_edges(self):
        self.assertEqual(len(self.polyedr.edges), 8)

    def test_area(self):
        self.polyedr.draw(tk)
        self.assertEqual(self.polyedr.calculate_area(), 0.25)

    def test_triangle_area(self):
        # Создание грани с вершинами, образующими треугольник
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(0, 1, 0)]
        facet = Facet(vertexes)
        expected_area = 0.5  # Площадь треугольника
        self.assertAlmostEqual(facet.area(), expected_area)

    def test_square_area(self):
        # Создание грани с вершинами, образующими квадрат
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(1, 1, 0), R3(0, 1, 0)]
        facet = Facet(vertexes)
        expected_area = 1.0  # Площадь квадрата
        self.assertAlmostEqual(facet.area(), expected_area)

    def test_angle_with_horizontal_horizontal(self):
        # Грань, лежащая на горизонтальной плоскости
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(1, 1, 0), R3(0, 1, 0)]
        facet = Facet(vertexes)
        expected_angle = 0.0
        # Угол между нормалью горизонтальной грани и вертикалью равен 0
        self.assertAlmostEqual(facet.angle_with_horizontal(), expected_angle)

    def test_angle_with_horizontal_vertical(self):
        # Грань, лежащая на вертикальной плоскости
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(1, 0, 1), R3(0, 0, 1)]
        facet = Facet(vertexes)
        expected_angle = pi / 2
        # Угол между нормалью вертикальной грани и вертикалью равен pi/2
        self.assertAlmostEqual(facet.angle_with_horizontal(), expected_angle)

    def test_angle_with_horizontal_45_degrees(self):
        # Грань, наклоненная под 45 градусов
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(0, 1, 1)]
        facet = Facet(vertexes)
        expected_angle = pi / 4
        # Угол между нормалью грани и вертикалью равен pi/4
        self.assertAlmostEqual(facet.angle_with_horizontal(),
                               expected_angle, places=5)

    def test_is_outside_unit_cube_inside(self):
        # Грань, центр которой находится внутри единичного куба
        vertexes = [R3(-0.25, -0.25, -0.25), R3(0.25, -0.25, -0.25),
                    R3(0.25, 0.25, -0.25), R3(-0.25, 0.25, -0.25)]
        facet = Facet(vertexes)
        self.assertFalse(facet.is_outside_unit_cube())

    def test_is_outside_unit_cube_outside(self):
        # Грань, центр которой находится вне единичного куба
        vertexes = [R3(1.0, 1.0, 1.0), R3(2.0, 1.0, 1.0),
                    R3(2.0, 2.0, 1.0), R3(1.0, 2.0, 1.0)]
        facet = Facet(vertexes)
        self.assertTrue(facet.is_outside_unit_cube())

    def test_is_outside_unit_cube_on_edge(self):
        # Грань, центр которой находится на грани единичного куба
        vertexes = [R3(-0.5, -0.5, 0), R3(0.5, -0.5, 0),
                    R3(0.5, 0.5, 0), R3(-0.5, 0.5, 0)]
        facet = Facet(vertexes)
        self.assertFalse(facet.is_outside_unit_cube())

    def test_is_fully_invisible_all_invisible(self):
        # Создание грани с невидимыми рёбрами
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(1, 1, 0)]
        facet = Facet(vertexes)
        for edge in facet.edges:
            edge.gaps = []  # Нет сегментов, т.е. рёбра невидимы
        self.assertTrue(facet.is_fully_invisible())

    def test_is_fully_invisible_some_visible(self):
        # Создание грани с частично видимыми рёбрами
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(1, 1, 0)]
        facet = Facet(vertexes)
        facet.edges[0].gaps = [Segment(0, 0.5)]
        # Первое ребро частично видимо
        facet.edges[1].gaps = []  # Второе ребро невидимо
        facet.edges[2].gaps = []  # Третье ребро невидимо
        self.assertFalse(facet.is_fully_invisible())

    def test_is_fully_invisible_all_visible(self):
        # Создание грани с полностью видимыми рёбрами
        vertexes = [R3(0, 0, 0), R3(1, 0, 0), R3(1, 1, 0)]
        facet = Facet(vertexes)
        for edge in facet.edges:
            edge.gaps = [Segment(0, 1)]
            # Все сегменты невырожденные, т.е. рёбра видимы
        self.assertFalse(facet.is_fully_invisible())
