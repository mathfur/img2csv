# -*- coding:utf-8 -*-

import unittest
from img2csv.helper import *

from scipy.misc import imsave
from numpy import *
import math

class TestGetLines(unittest.TestCase):
  # 画像に横線をline_num本引く(軸最初のx値はx1, 末尾はx2)
  def draw_horizontal_line(self, img, x1, x2, line_num):
    for i in range(line_num):
      for x in range(x2 - x1 + 1):
        img[10 + 10*i][x1 + x][0] = 0
        img[10 + 10*i][x1 + x][1] = 0
        img[10 + 10*i][x1 + x][2] = 0

  def setUp(self):
    self.img = create_blank_img(100)

  def test_get_lines(self):
    for i in range(4):
      self.draw_horizontal_line(self.img, 50, 70, i)
      lines = get_lines(self.img)
      self.assertEqual(i, len(lines))
      for line in lines:
        self.assertEqual(50, line[0])
        self.assertEqual(70, line[2])

class TestIsAdjacent(unittest.TestCase):
  def test_is_adjacent(self):
    self.assertTrue(is_adjacent((0, 0, 5, 0), (3, 1, 6, 1)))
    self.assertTrue(is_adjacent((0, 1, 5, 1), (3, 0, 6, 0)))
    self.assertFalse(is_adjacent((0, 0, 5, 0), (3, 2, 6, 2)))
    self.assertFalse(is_adjacent((0, 0, 5, 0), (6, 1, 7, 1)))
    self.assertFalse(is_adjacent((6, 0, 7, 0), (0, 1, 5, 1)))
    self.assertTrue(is_adjacent((15, 0, 40, 0), (20, 1, 21, 1)))

class TestGetLongestLines(unittest.TestCase):
  # (x1, y)-(x2, y)の直線を引く
  def draw_horizontal_line(self, img, x1, x2, y):
    for x in range(x2 - x1 + 1):
      img[y][x1 + x][0] = 0
      img[y][x1 + x][1] = 0
      img[y][x1 + x][2] = 0

  def setUp(self):
    self.img = create_blank_img(100)

  def test_get_longest_lines__0_line(self):
    lines = get_longest_lines(self.img)
    self.assertEqual(0, len(lines))

  def test_get_longest_lines__1_line(self):
    self.draw_horizontal_line(self.img, 10, 20, 0)
    lines = get_longest_lines(self.img, 2)
    self.assertEqual([(10, 0, 20, 0)], lines)

  def test_get_longest_lines__2_line_adjacent(self):
    self.draw_horizontal_line(self.img, 10, 20, 0)
    self.draw_horizontal_line(self.img, 15, 30, 1)
    lines = get_longest_lines(self.img, 2)
    self.assertEqual([(15, 1, 30, 1)], lines)

  def test_get_longest_lines__2_line_not_adjacent(self):
    self.draw_horizontal_line(self.img, 10, 20, 0)
    self.draw_horizontal_line(self.img, 15, 30, 2)
    lines = get_longest_lines(self.img, 2)
    self.assertEqual([(10, 0, 20, 0), (15, 2, 30, 2)], lines)

  def test_get_longest_lines__more_lines(self):
    self.draw_horizontal_line(self.img, 15, 40, 0)
    self.draw_horizontal_line(self.img, 10, 16, 1)
    self.draw_horizontal_line(self.img, 35, 45, 1)
    self.draw_horizontal_line(self.img, 44, 50, 1)

    self.draw_horizontal_line(self.img, 18, 19, 2)
    self.draw_horizontal_line(self.img, 18, 30, 3)

    lines = get_longest_lines(self.img, 2)

    self.assertEqual([(15, 0, 40, 0), (18, 3, 30, 3)], lines)

class TestInvertImg(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(100)

  def test_invert_img(self):
    img = invert_img(self.img)
    self.assertTrue(is_present_pixel(img[0][0]))
    img = invert_img(img)
    self.assertFalse(is_present_pixel(img[0][0]))

class TestIsInsidePararell(unittest.TestCase):
  def test_is_inside_pararell(self):
    self.assertTrue(is_inside_parallel((0, 0, 10, 0), (0, 10, 10, 10), (5, 2, 8, 2), (5, 7, 8, 7)))       # (A), 4つの横平行線
    self.assertFalse(is_inside_parallel((0, 0, 10, 0), (0, 10, 10, 10), (5, 12, 8, 12), (5, 17, 8, 17)))  # (A)の真ん中のペアを外に出した
    self.assertFalse(is_inside_parallel((0, 3, 10, 3), (0, 10, 10, 10), (5, 2, 8, 2), (5, 7, 8, 7)))      # (A)の真ん中のペアの片方を外に出した
    self.assertFalse(is_inside_parallel((10, 0, 20, 0), (0, 10, 10, 10), (5, 2, 8, 2), (5, 7, 8, 7)))     # (A), 1個目の横線を横に移動させた

class TestHaveInsideParallel(unittest.TestCase):
  def test_have_inside_parallel(self):
    self.assertEqual(-1, have_inside_parallel([], (5, 2, 8, 2), (5, 7, 8, 7)))
    self.assertEqual(-1, have_inside_parallel([[(5, 2, 8, 2), (5, 7, 8, 7)]], (10, 0, 20, 0), (0, 10, 10, 10)))
    self.assertEqual(-1, have_inside_parallel([[(5, 2, 8, 2), (5, 7, 8, 7)]], (5, 2, 8, 2), (5, 7, 8, 7)))
    self.assertEqual(0, have_inside_parallel([[(5, 2, 8, 2), (5, 7, 8, 7)], [(0, 0, 10, 0), (0, 10, 10, 10)]], (0, 0, 10, 0), (0, 10, 10, 10)))
    self.assertEqual(-1, have_inside_parallel([[(5, 2, 8, 2), (5, 7, 8, 7)], [(0, 0, 10, 0), (0, 10, 10, 10)]], (5, 2, 8, 2), (5, 7, 8, 7)))
    self.assertEqual(-1, have_inside_parallel([[(5, 2, 8, 2), (5, 7, 8, 7)], None, [(0, 0, 10, 0), (0, 10, 10, 10)]], (5, 2, 8, 2), (5, 7, 8, 7)))

class TestGetParentIndexes(unittest.TestCase):
  def test_get_parent_indexes(self):
    self.assertEqual([None], get_parent_indexes([[(5, 2, 8, 2), (5, 7, 8, 7)]]))                                                                       # *
    self.assertEqual([1, None], get_parent_indexes([[(5, 2, 8, 2), (5, 7, 8, 7)], [(0, 0, 10, 0), (0, 10, 10, 10)]]))                                  # *->*
    self.assertEqual([None, 0], get_parent_indexes([[(0, 0, 10, 0), (0, 10, 10, 10)], [(5, 2, 8, 2), (5, 7, 8, 7)]]))                                  # *<-*の関係
    self.assertEqual([None, 0, 1], get_parent_indexes([[(0, 0, 10, 0), (0, 10, 10, 10)], [(5, 2, 8, 2), (5, 7, 8, 7)], [(6, 3, 7, 3), (6, 6, 7, 6)]])) # *->*->*の関係

class TestIsBlack(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(2)

  def test_is_black__0_pixel(self):
    self.assertFalse(is_black(self.img))

  def test_is_black__1_pixel(self):
    self.img[0][0] = [0, 0, 0, 255]
    self.assertFalse(is_black(self.img))

  def test_is_black__2_pixel(self):
    self.img[0][0] = [0, 0, 0, 255]
    self.img[0][1] = [0, 0, 0, 255]
    self.assertTrue(is_black(self.img))

  def test_is_black__3_pixel(self):
    self.img[0][0] = [0, 0, 0, 255]
    self.img[0][1] = [0, 0, 0, 255]
    self.img[1][0] = [0, 0, 0, 255]
    self.assertTrue(is_black(self.img))

class TestGetPartialImage(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(3)

  def test_get_partial_image(self):
    self.img[2][2] = [0, 0, 0, 255]
    partial_img = get_partial_image(self.img, (1, 1), (2, 2))
    self.assertEqual([255, 255, 255, 255], partial_img[0][0].tolist())
    self.assertEqual([255, 255, 255, 255], partial_img[0][1].tolist())
    self.assertEqual([255, 255, 255, 255], partial_img[1][0].tolist())
    self.assertEqual([0, 0, 0, 255],       partial_img[1][1].tolist())

class TestGetText(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(3)

  def test_get_text(self):
    get_text(self.img)

class TestIsInsideRect(unittest.TestCase):
  def test_is_inside_rect(self):
    self.assertTrue(is_inside_rect((1, 1, 2, 2), (1, 1, 1, 1)))  # (左上x, 左上y, 右下x, 右下y)
    self.assertTrue(is_inside_rect((1, 1, 2, 2), (1, 1, 1, 2)))
    self.assertTrue(is_inside_rect((1, 1, 2, 2), (1, 1, 2, 1)))
    self.assertTrue(is_inside_rect((1, 1, 2, 2), (1, 1, 2, 2)))
    self.assertFalse(is_inside_rect((1, 1, 2, 2), (0, 1, 1, 1)))
    self.assertFalse(is_inside_rect((1, 1, 2, 2), (0, 1, 2, 2)))

class TestGetRandomRect(unittest.TestCase):
  def test_get_random_rect(self):
    for i in range(10):
      inside_rect = get_random_rect((0, 0, 2, 2))
      self.assertTrue(is_inside_rect((0, 0, 2, 2), inside_rect))

class TestStepDecrease(unittest.TestCase):
  def rect_diff(self, rect1, rect2):
    sum = 0
    for i in range(len(rect1)):
      sum += (rect1[i] - rect2[i]) ** 2
    return math.sqrt(sum)

  def test_step_decrease(self):
    self.assertEqual(step_decrease((0, 0, 0, 0), 0), (0, 0, 0, 0))
    self.assertEqual(step_decrease((0, 0, 0, 0), 1), (0, 0, 0, 0))
    self.assertEqual(step_decrease((0, 0, 0, 0), 2), (0, 0, 0, 0))
    self.assertEqual(step_decrease((0, 0, 0, 0), 3), (0, 0, 0, 0))

    self.assertEqual(step_decrease((0, 1, 1, 1), 0), (1, 1, 1, 1))
    self.assertEqual(step_decrease((0, 1, 1, 1), 1), (0, 1, 1, 1))
    self.assertEqual(step_decrease((0, 1, 1, 1), 2), (0, 1, 0, 1))
    self.assertEqual(step_decrease((0, 1, 1, 1), 3), (0, 1, 1, 1))

    self.assertEqual(step_decrease((0, 0, 1, 1), 0), (1, 0, 1, 1))
    self.assertEqual(step_decrease((0, 0, 1, 1), 1), (0, 1, 1, 1))
    self.assertEqual(step_decrease((0, 0, 1, 1), 2), (0, 0, 0, 1))
    self.assertEqual(step_decrease((0, 0, 1, 1), 3), (0, 0, 1, 0))

class TestHavePointInBorder(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(3)
    self.img[1][1] = [0, 0, 0, 0]

  def test_have_point_in_border(self):
    self.assertFalse(have_point_in_border(self.img, (0, 0, 2, 2)))
    self.assertFalse(have_point_in_border(self.img, (0, 0, 0, 0)))
    self.assertFalse(have_point_in_border(self.img, (2, 2, 2, 2)))

    self.assertTrue(have_point_in_border(self.img, (0, 0, 1, 1)))
    self.assertTrue(have_point_in_border(self.img, (1, 0, 1, 1)))
    self.assertTrue(have_point_in_border(self.img, (1, 1, 2, 2)))

class TestGetMinimumRect(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(3)
    self.img[1][1] = [0, 0, 0, 0]

  def test_get_minimum_rect(self):
    self.assertEqual((0, 0, 2, 2), get_minimum_rect(self.img, (0, 0, 2, 2)))
    self.assertEqual(None,         get_minimum_rect(self.img, (0, 1, 2, 2)))

class TestGetMinimumRects(unittest.TestCase):
  def setUp(self):
    self.img = create_blank_img(5)

  def test_get_minimum_rects__0_point(self):
    self.assertEqual([], get_minimum_rects(self.img, 200))

  def test_get_minimum_rects__1_point(self):
    self.img[1][1] = [0, 0, 0, 0]
    self.assertEqual([(0, 0, 2, 2)], get_minimum_rects(self.img, 200))

  def test_get_minimum_rects__2_point(self):
    self.img[1][1] = [0, 0, 0, 0]
    self.img[3][3] = [0, 0, 0, 0]

    expected = [(0, 0, 2, 2), (2, 2, 4, 4)]
    actual = get_minimum_rects(self.img, 200)

    expected.sort()
    actual.sort()
    self.assertEqual(expected, actual)

  def test_get_minimum_rects__2_point(self):
    self.img[1][1] = [0, 0, 0, 0]
    self.img[3][1] = [0, 0, 0, 0]
    self.img[3][3] = [0, 0, 0, 0]

    expected = [(0, 0, 2, 2), (0, 2, 2, 4), (2, 2, 4, 4)]
    actual = get_minimum_rects(self.img, 200)

    expected.sort()
    actual.sort()
    self.assertEqual(expected, actual)

class TestGetParallels(unittest.TestCase):
  def test_get_parallels_from_lines__no_line(self):
    self.assertEqual([], get_parallels([]))

  def test_get_parallels_from_lines__one_line(self):
    self.assertEqual([], get_parallels([(0, 2, 10, 2)]))

  def test_get_parallels_from_lines__one_paralles(self):
    self.assertEqual([((0, 2, 10, 2), (0, 8, 10, 8))], get_parallels_from_lines([(0, 2, 10, 2), (0, 8, 10, 8)], 0))

    self.assertEqual([((0, 2, 10, 2), (1, 8, 10, 8))], get_parallels_from_lines([(0, 2, 10, 2), (1, 8, 10, 8)], 1))
    self.assertEqual([],                               get_parallels_from_lines([(0, 2, 10, 2), (1, 8, 10, 8)], 0))

    self.assertEqual([((0, 2, 10, 2), (1, 8, 9,  8))], get_parallels_from_lines([(0, 2, 10, 2), (1, 8, 9, 8)], 2))
    self.assertEqual([],                               get_parallels_from_lines([(0, 2, 10, 2), (1, 8, 9, 8)], 1))

if __name__ == '__main__':
  unittest.main()
