#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scipy.misc import imsave
from numpy import *
from PIL import Image
from img2csv.helper import *

def run_img2csv():
  img = Image.open('input.png')
  parallels = output_img_to_yaml(img, 0.9)

  img = write_parallels_to_img(img, parallels)
  imsave("output.png", img)
