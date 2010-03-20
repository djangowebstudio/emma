#!/usr/bin/env python2.5
# encoding: utf-8
"""
compare.py

Created by Geert Dekkers on 2010-03-10.
Copyright (c) 2010 Geert Dekkers Web Studio. All rights reserved.
"""

import sys
import os
import unittest
from PIL import Image, ImageStat, ImageChops
import glob
import binascii
import md5
import math, operator

class Compare:
	def __init__(self):
		pass
    def is_equal(self, im1, im2):
        """
        Compare two images
        The quickest way to determine if two images have exactly the same contents is to get the 
        difference between the two images, and then calculate the bounding box of the non-zero regions 
        in this image. If the images are identical, all pixels in the difference image are zero, and 
        the bounding box function returns None.
        http://effbot.org/zone/pil-comparing-images.htm
        """
        return ImageChops.difference(im1, im2).getbbox() is None

    def rmsdiff(self, im1, im2):
        """Calculate the root-mean-square difference between two images
        http://effbot.org/zone/pil-comparing-images.htm"""

        h = ImageChops.difference(im1, im2).histogram()
        # calculate rms
        return math.sqrt(reduce(operator.add,map(lambda h, i: h*(pow(1,2)), h, range(256))) / (float(im1.size[0]) * im1.size[1]))


    def img_compare(self, img_path_1, img_path_2):
        """
        Compare two images by calculating the root-mean-square difference between their histograms
        http://snipplr.com/view/757/compare-two-pil-images-in-python/
        """
        h1 = Image.open(img_path_1).histogram()
        h2 = Image.open(img_path_2).histogram()

        return math.sqrt(reduce(operator.add,
        	map(lambda a,b: (a-b)**2, h1, h2))/len(h1))


    def histogram_md5(self, im):
        """
        compare jpg image files using histogram
        use progressively more costly method to see if two jpg files are different
        http://snippets.dzone.com/posts/show/6690
        """
        m = md5.new()
        h = im.histogram()
        m.update(str(h))
        return m.digest()

        if len(sys.argv) < 1:
            print "No file names provided."
            sys.exit()

        if len(sys.argv) is not 3:
            print "two files only!"
            sys.exit()

        file1 = sys.argv[1]
        file2 = sys.argv[2]

        print "open ", file1
        im1 = Image.open(file1)

        print "open ", file2
        im2 = Image.open(file2)

        print "sizes: ", im1.size, " " , im2.size

        if im1.size != im2.size:
            print file1, " and ", file2 , " are different"
            sys.exit()


        print "info: " ,im1.info , " " , im2.info

        if (im1.info != im2.info):
            print file1, " and ", file2 , " are different"
            sys.exit()


        print "mode: " ,im1.mode , " ", im2.mode

        if im1.mode != im2.mode:
            print file1, " and ", file2 , " are different"
            sys.exit()

        file1_hm5 = histogram_md5(im1)
        file2_hm5 = histogram_md5(im2)

        print "histogram md5: ", binascii.b2a_hex(file1_hm5), " ", binascii.b2a_hex(file2_hm5)

        if file1_hm5 != file2_hm5:
            print file1, " and ", file2 , " are different"
            sys.exit()

        f1 = os.path.getsize(file1)
        f2 = os.path.getsize(file2)

        if f1 != f2:
            print file1, " and ", file2 , " have different sizes."
            print "possibly because they have different meta data."

        print "looking at every bit of each file. this can take a while..."

        imc1 = list(im1.getdata())
        l1 = len(imc1)
        imc2 = list(im2.getdata())
        l2 = len(imc2)

        if l1 != l2:
            print file1, " and ", file2 , " are different"
            sys.exit()

        if imc1 != imc2:
            print file1, " and ", file2 , " are different"
            sys.exit()

        print file1, " and ", file2 , " contain the same image data."


class compareTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	pass