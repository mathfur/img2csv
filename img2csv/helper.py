# -*- coding: utf-8 -*-

from scipy.misc import imsave
from numpy import *
from scipy import ndimage
from scipy.ndimage import filters
import tempfile
import os
import random
from PIL import Image

# white image
def create_blank_img(size):
  matrix = []
  for x in range(size):
    row = []
    for y in range(size):
      row.append([255,255,255,255])
    matrix.append(row)
  return matrix

def is_blank_pixel(pixel):
  return (pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255)

def is_present_pixel(pixel):
  return (not is_blank_pixel(pixel))

def get_lines(img):
  start_pixel = None
  last_pixel = None
  lines = []

  def close_line(end_pixel):
    lines.append((start_pixel[1], start_pixel[0], end_pixel[1], end_pixel[0]))

  for x in range(len(img)):
    insize_line = False
    for y in range(len(img[x])):
      if insize_line:
        if is_blank_pixel(img[x][y]):
          close_line(last_pixel)
          start_pixel = False
          insize_line = False
      else:
        if is_present_pixel(img[x][y]):
          insize_line = True
          start_pixel = [x, y]
      last_pixel = [x, y]
    if start_pixel:
      close_line([x, y])
      start_pixel = False

  return lines

# :: Line -> Line -> Bool
def is_adjacent(line1, line2):
  y1 = line1[1]
  y2 = line2[1]

  x1 = line1[0]
  x2 = line1[2]
  x3 = line2[0]
  x4 = line2[2]

  return (
           (abs(y1 - y2) <= 1)
           and
           (
             (x3 <= x2 and x2 <= x4)
             or
             (x3 <= x1 and x1 <= x4)
             or
             (x1 <= x3 and x4 <= x2)
           )
         )

# :: Img -> [Line]
def get_longest_lines(img, min_length=30):
  def line_length(line_):
    return abs(line[0] - line[2])

  lines = get_lines(img)
  adjacent_groups = []

  for line in lines:
    if line_length(line) < min_length:
      continue
    any_group_appended = False
    for group in adjacent_groups:
      filtered = filter(lambda e: is_adjacent(e, line), group)
      # groupのある要素と隣接している場合
      if 0 < len(filtered):
        group.append(line)
        any_group_appended = True
        break
    # どことも隣接していなかった場合
    if not any_group_appended:
      adjacent_groups.append([line])

  longest_lines = []
  for line_group in adjacent_groups:
    max_result = None
    for line in line_group:
      if (not max_result) or max_result[1] < line_length(line):
        max_result = [line, line_length(line)]
    longest_lines.append(max_result[0])

  return longest_lines

# 2直線(x1, y, x2, y), (x3, y', x4, y')の間の距離を計算する.
#   この距離は、「この2直線がパラレルなペアかどうか」の量を意味する
def get_distance_between_2_lines(line1, line2):
  return (abs(line2[0] - line1[0]) + abs(line2[2] - line1[2]))

def get_parallels_from_lines(lines, acceptable_diff=0):
  lines = lines[:]
  result = []

  if len(lines) <= 1:
    return []

  while 1:
    line1 = lines[0]
    for i in range(len(lines) - 1):
      line2 = lines[i+1]
      if get_distance_between_2_lines(line1, line2) <= acceptable_diff:
        result.append((line1, line2))
        lines.remove(line1)
        lines.remove(line2)
        break
      if i == (len(lines) - 2):
        lines.remove(line1)
    if len(lines) <= 1:
      break

  return result

def get_parallels(img, acceptable_diff=0):
  lines = get_longest_lines(img)
  return get_parallels_from_lines(lines, acceptable_diff)

def invert_img(img):
  img = copy(img)
  for y in range(len(img)):
    for x in range(len(img[y])):
      img[y][x] = [255 - img[y][x][0], 255 - img[y][x][1], 255 - img[y][x][2], img[y][x][3]]
  return img

# 直線のペアpair1が、別の直線のペアpair2をその内側に持つならTrue
# e.g. (0, 0, 10, 0), (5, 2, 8, 2), (5, 7, 8, 7), (0, 10, 10, 10)
def is_inside_parallel(pair1_fst, pair1_snd, pair2_fst, pair2_snd):
  cond1 = (pair1_fst[1] < pair2_fst[1] and pair2_fst[1] < pair1_snd[1])
  cond2 = (pair1_fst[1] < pair2_snd[1] and pair2_snd[1] < pair1_snd[1])
  cond3 = (pair1_fst[0] <= pair2_fst[0] and pair2_fst[2] <= pair1_fst[2])
  cond4 = (pair1_snd[0] <= pair2_snd[0] and pair2_snd[2] <= pair1_snd[2])

  return cond1 and cond2 and cond3 and cond4

# 見つかればそのインデックスを返す。見つからなければ-1を返す
def have_inside_parallel(parallels, pair1_fst, pair1_snd):
  idx = 0
  for parallel in parallels:
    if parallel and is_inside_parallel(pair1_fst, pair1_snd, parallel[0], parallel[1]):
      return idx
    idx = idx + 1
  return -1

def get_parent_indexes(parallels_):
  parallels = parallels_[:]
  parents = [None] * len(parallels)
  old_len = len(parallels)
  while True:
    idx = 0
    for parallel in parallels:
      if (not parallel) or parents[idx]:
        continue
      child_idx = have_inside_parallel(parallels, parallel[0], parallel[1])
      if 0 <= child_idx:
        if (0 > have_inside_parallel(parallels, parallels[child_idx][0], parallels[child_idx][1])):
          parents[child_idx] = idx
          parallels[child_idx] = None
          break
      idx = idx + 1
    if old_len == len(filter(lambda e: e, parallels)):
      return parents
    else:
      old_len = len(filter(lambda e: e, parallels))

# 半分以上が黒ならTrue
def is_black(img):
  black_count = 0
  for y in range(len(img)):
    for x in range(len(img[y])):
      if (img[y][x][0] == 0 and img[y][x][1] == 0 and img[y][x][2] == 0):
        black_count += 1
  return (len(img) * len(img[0]) <= black_count*2)

# (p1, p2)領域を切り取った画像を得る
def get_partial_image(img, p1, p2):
  x1, y1, x2, y2 = p1[0], p1[1], p2[0]+1, p2[1]+1
  return array(img)[y1:y2, x1:x2]

def get_text(img):
  img_file = tempfile.NamedTemporaryFile()
  output_file = tempfile.NamedTemporaryFile()

  img_fname = img_file.name + ".jpg"
  output_fname = output_file.name + ".txt"

  imsave(img_fname, img)
  os.system("tesseract %(input)s %(output)s -l eng" % {"input": img_fname, "output": output_file.name})
  result_text = output_file.read()

  img_file.close()
  output_file.close()
  return result_text

# rect, small_rect :: (左上x, 左上y, 右下x, 右下y)
# small_rectがrectに含まれているか?
def is_inside_rect(rect, small_rect):
  return (
           rect[0] <= small_rect[0] and
           rect[1] <= small_rect[1] and
           small_rect[2] <= rect[2] and
           small_rect[3] <= rect[3]
         )

# rect :: (左上x, 左上y, 右下x, 右下y)
# rectより小さいrectをランダムに得る
def get_random_rect(rect):
  x1, y1, x2, y2 = rect

  middle_xs = [random.randint(x1, x2), random.randint(x1, x2)]
  middle_ys = [random.randint(y1, y2), random.randint(y1, y2)]

  middle_xs.sort()
  middle_ys.sort()

  return (middle_xs[0], middle_ys[0], middle_xs[1], middle_ys[1])

# rectのidx要素を1縮める
def step_decrease(rect, idx):
  x1, y1, x2, y2 = rect
  idx = idx % 4

  def step_decrease_for_one_axis(a, b, idx_):
    if a == b:
      return None
    else:
      if idx_ == 0:
        return (a + 1, b)
      else:
        return (a, b - 1)

  if idx == 0 or idx == 2:
    result = step_decrease_for_one_axis(x1, x2, idx)

    if result:
      return (result[0], rect[1], result[1], rect[3])
    else:
      return rect
  if idx == 1 or idx == 3:
    result = step_decrease_for_one_axis(y1, y2, idx - 1)

    if result:
      return (rect[0], result[0], rect[2], result[1])
    else:
      return rect

def have_point_in_border(img, rect):
  x1, y1, x2, y2 = rect

  point_detected = False
  for x in range(x1, x2+1):
    if is_present_pixel(img[y1][x]) or is_present_pixel(img[y2][x]):
      point_detected = True

  for y in range(y1, y2+1):
    if is_present_pixel(img[y][x1]) or is_present_pixel(img[y][x2]):
      point_detected = True

  return point_detected

# imgの中から最小の4角形(複数個)を得る
def get_minimum_rects(img, loop_num=1000):
  base_rect = (0, 0, len(img[0])-1, len(img)-1)
  minimum_rects = []

  for i in range(loop_num):
    start_rect = get_random_rect(base_rect)
    minimum_rect = get_minimum_rect(img, start_rect)
    if minimum_rect:
      if not any(map(lambda rect: is_inside_rect(minimum_rect, rect), minimum_rects)):
        minimum_rects.append(minimum_rect)

  return minimum_rects


# imgの中でbase_rectを点に触れる直前まで縮めてそのrectを返す. 1点まで縮んだらNoneを返す
def get_minimum_rect(img, base_rect):
  if base_rect[0] == base_rect[1] and base_rect[0] == base_rect[2] and base_rect[0] == base_rect[3]:
    return None

  if have_point_in_border(img, base_rect):
    return None

  current_rect = base_rect
  max_loop_num = 10000*2
  for i in range(max_loop_num): # 10000ピクセル^2を限度とする
    if max_loop_num - 1 == i:
      raise "reach loop limit"

    # 4方向に、順に試行(スタートはランダム)
    next_rect = None
    start_idx = random.randint(0, 3)
    for i in range(4):
      next_candidate = step_decrease(current_rect, start_idx + i)
      if next_candidate == current_rect:
        return None

      if not have_point_in_border(img, next_candidate):
        next_rect = next_candidate
        break

    if not next_rect:
      return current_rect

    current_rect = next_rect

# TODO: 未テスト
# :: 方眼紙の各セルにOXが入っているような状態の画像 -> [(x1, y1, x2, y2)]
def get_cells(img):
  img = invert_img(img)
  lines = get_longest_lines(img)
  ys = [0] + map(lambda line: line[1], lines)
  ys.append(len(img))

  img = img.T
  lines = get_longest_lines(img)
  xs = [0] + map(lambda line: line[1], lines)
  ys.append(len(img))

  cells = []
  for i in (len(xs) - 1):
    for j in (len(ys) - 1):
      cells.append((xs[i], ys[j], xs[i+1], ys[j+1]))

# TODO: 未テスト
def expand_img(img, width, height):
  w, h = img.shape

  start_x = (width - w) / 2
  end_x = width - w - w1
  start_y = (height - h) / 2
  end_y = height - h - h1

  matrix = []
  for x in range(width):
    row = []
    for y in range(height):
      if (start_x <= x and x < end_x) and (start_y <= y and y < end_y):
        row.append(img[y - start_y][x - start_x])
      else:
        row.append([255,255,255,255])
    matrix.append(row)
  return matrix

# TODO: 未テスト
# 画像の黒部分をふくらませる
def dilate(img):
  return ndimage.grey_erosion(img, size=(5, 5, 5))

# TODO: 未テスト
# sobelフィルタをかける(微分係数が大きい部分ほど白い、小さいほど黒い画像を得る)
# :: Image -> Image
def sobel(img):
  imx = zeros(img.shape)
  filters.sobel(img, 0, imx)
  imy = zeros(img.shape)
  filters.sobel(img, 1, imy)
  return sqrt(imx**2 + imy**2)

def convert_black_white_img(img):
  img = copy(img)
  for y in range(len(img)):
    for x in range(len(img[y])):
      if not (img[y][x][0] == 255 and img[y][x][1] == 255 and img[y][x][2] == 255 and img[y][x][3] == 255):
        img[y][x] = array([0, 0, 0, 255])
  return img

# TODO: 未テスト
# imgからRectの階層構造を読み取ってYAML出力
def output_img_to_yaml(img, threshold):
  img = dilate(array(img))

  threshold_ = img.max() * threshold
  img = (img >= threshold_)*255
  img = convert_black_white_img(img)

  parallels = get_parallels(img, 50)

  print "nodes:"
  for i in range(len(parallels)):
    parallel = parallels[i]
    line1 = parallel[0]
    line2 = parallel[1]
    print "  name: %d" % i
    print "  x1: %d" % line1[0]
    print "  y1: %d" % line1[1]
    print "  x2: %d" % line2[2]
    print "  y2: %d" % line2[3]

  parents = get_parent_indexes(parallels)
  print "edges:"
  for i in range(len(parents)):
    if parents[i] != None:
      print " -start: %d" % i
      print "  end: %d"   % parents[i]

  return parallels

# imgにparallelsを描画する(デバッグ用)
def write_parallels_to_img(img, parallels):
  img = copy(array(img))

  for parallel in parallels:
    line1 = parallel[0]
    line2 = parallel[1]

    x1 = line1[0]
    x2 = line1[2]
    y1 = line1[1]

    x3 = line2[0]
    x4 = line2[2]
    y2 = line2[1]

    for x in range(x1, x2+1):
      img[y1][x] = [0, 150, 0, 255]

    for x in range(x3, x4+1):
      img[y2][x] = [0, 150, 0, 255]

  return img
