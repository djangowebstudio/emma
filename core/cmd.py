#!/usr/bin/env python
# encoding: utf-8
"""
cmd.py

Created by Geert Dekkers on 2010-03-28.
Copyright (c) 2010 Geert Dekkers Web Studio. All rights reserved.

Class dedicated to subprocess functions

"""

import sys
import os
import unittest
import subprocess
from pyPdf import PdfFileWriter, PdfFileReader

class Command:
    def __init__(self):
        pass
        
    def ffmpeg_simple(self, finput, foutput, dimensions=None, verbose=False):
        """A simple version of the ffmpeg wrapper. Takes input & output, optionally the height/width."""
        if dimensions:
            size = 'x'.join(dimensions)
            cmd = [ 'ffmpeg ', '-i', finput,  '-s', size,  '-y',  '-ar', '11025',  '-b',  '800', foutput]
        else:
            cmd = [ 'ffmpeg', '-i', finput,  '-y',  '-ar', '11025', foutput]
        proc = subprocess.Popen(cmd)      
        verbose = proc.communicate()[0]

        if not verbose: # Return the full path AND filename if verbose is set to True
            if dimensions: 
                return foutput, dimensions
            else:     
                return foutput
        else:
            return verbose

    
    

    def ffmpeg(self, finput, foutput, size="other", defaultwidth=917, frame=1, format='png', verbose=False):
        """ 
        Wrapper for ffmpeg
        ------------------
        
        Converts all sorts of video formats to a clip in .flv format or set of images.
        The number of frames can be set in de args.
        Just a python wrapper for ffmpeg.

        Takes:
        1. finput (str), a path
        2. foutput (str). This can be:
        a) full path including a filename if arg 3 is "large", or "cropped".
        b) full path to a directory if arg 3 is "tiny", "small", or "fullsize"
        3. size (str), either one of the above, or left blank. In the latter
        case, ffmpeg will be instructed to get the first 180 frames of the source 
        file.
        4. defaultwidth (int), a fallback in case a child function fails to return a value
        5. Image format is png by default -- only if you want a slice of the vid back. 
        Needs to be something that both ffmpeg and sips can handle.
        6. Return the full cammand list

        For sound only files, use "large".

        (from man ffmpeg)
        *You can extract images from a video: 
        ffmpeg −i foo.avi −r 1 −s WxH −f image2 foo−%03d.jpeg 
        This will extract one video frame per second from the video and will output them in ﬁles named 
        foo−001.jpeg,foo−002.jpeg,etc. Images will be rescaled to ﬁt the newWxH values. 
        The syntax foo−%03d.jpeg speciﬁes to use a decimal number composed of three digits padded with 
        zeroes to express the sequence number. It is the same syntax supported by the C printf function, but only 
        formats accepting a normal integer are suitable. 
        If you want to extract just a limited number of frames, you can use the above command in combination 
        with the −vframes or −t option, or in combination with −ss to start extracting from a certain point in time. 

        """
        dimensions = {} # Init a dict to hold dimensions

        if size == 'large':
            cmd = ["ffmpeg","-i", finput, "-y","-ar","11025", "-b", "1400kb", foutput]
        elif size == 'cropped':
            cmd = ["ffmpeg","-i",finput,"-y","-fs","100000",foutput]
        elif size == 'tiny' or size == 'small':
            fname = '/'.join([foutput, os.path.splitext(os.path.basename(finput))[0] + ".png"])
            cmd = ["ffmpeg", "-i", finput, "-y", "-vframes", "1", "-ss", unicode(frame), fname]
        elif size == 'fullsize':
            fname = '/'.join([foutput, os.path.splitext(os.path.basename(finput))[0] + ".jpg"])
            cmd = ["ffmpeg", "-i", finput, "-y", "-vframes", "1", "-ss", unicode(frame), fname]
        else:
            cmd = ["ffmpeg","-i",finput,"-y","-vframes","180","-an","-s","qqvga",foutput]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        verbose = proc.communicate()[0]
        if size == 'tiny': self.crop_to_center(fname, foutput,29,29)
        if size == 'small': self.crop_to_center(fname, foutput,148,148)
        if size == 'fullsize': 
            dimensions = self.sips_get_properties(fname)
            if dimensions: width = dimensions['pixelWidth'] if dimensions.has_key('pixelWidth') else defaultwidth
            self.sips_resize(fname, foutput, width, format)

        if not verbose: # Return the full path AND filename if verbose is set to True
            if dimensions: 
                return foutput, dimensions
            else:     
                return foutput
        else:
            return verbose

    
    def sips_get_properties(self, source):
        """ Gets item propertes (including a PDF) using sips"""
        # Get all properties in a dict        
        properties = {} 
        optimized = [] # List in which to optimise items (ie strip white space)
        prop_cmd = ["sips", "-g", "all", source] 

        result = subprocess.Popen(prop_cmd, stdout=subprocess.PIPE).stdout.read()
        r = result.split('\n')
        r[0] = ':'.join(['file', r[0]])

        for item in r:
            if item:
                optimized.append(item.strip())
        for kv in optimized:
            try:
                properties.setdefault(* kv.split(':'))
            except Exception, inst:
                pass

        if properties:
            for k, v in properties.iteritems(): properties[k] = v.strip()
            return properties
        else:
            return None

    def sips_reformat(self, source, target, format):
        """ Reformats images using sips. See args:
        1) path to source file
        2) path to target dir
        3) format (one of string jpeg | tiff| png | gif | jp2 | pict | bmp | qtif | psd | sgi | tga | pdf)

        """
        if os.path.exists(source):
            cmd = ["sips", "--setProperty", "format", format, source, "--out", target]
            action = subprocess.Popen(cmd,stdout=subprocess.PIPE).stdout.read()
            return action
        else:
            return None

    def sips_resize(self, source, target, target_width, format):
        """Scales any source to specified width, respecting aspect using sips.
        Takes source (full path), target (can be directory), target_width (string or int), format (one of string jpeg| tiff| png | gif | jp2 | pict | bmp | qtif | psd | sgi | tga )"""

        if os.path.exists(source):
            resize_cmd = ["sips", "--resampleWidth", str(target_width), "--setProperty", "format", format, source, "--out", target]
            action = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            return action
        else:
            return None

    def crop_to_center(self, source, target, target_width, target_height):
        """ Scales and then crops source (including a PDF) to center with sips in relation to size. Uses sips.
        Takes source (full path), target (can be a directory), target_width (string or int), target_height ( string or int)"""     

        if os.path.exists(source):           
            # We don't want the entire function breaking if we can't get the properties (but if we can't get them what else will break?)
            try:
                properties = self.sips_get_properties(source)
                width, height = int(properties['pixelWidth']), int(properties['pixelHeight'])
                if width > 0 and height > 0:
                    aspect = target_width/target_height
                    widthfactor = target_width/width  
                    heightfactor = target_height/height
                else:
                    return None

                base_heightwidth = (width/7) if widthfactor > heightfactor else (height/8)
            except Exception, inst:
                pass
                base_heightwidth = 210
            resize_cmd = ["sips", "--resampleHeight", str(base_heightwidth), "--cropToHeightWidth", str(target_width), str(target_height), "--setProperty", "format", "png", source, "--out", target]
            action = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            return action

        else:
            return None

    def get_pdf_dimensions(self, path):
        """Get pdf dimensions using pyPdf"""
        try:
            pdf = PdfFileReader(file(path, "rb"))
        except:
            return None
        page_list = []
        if pdf.getNumPages() > 0:
            for page_number in range(0, pdf.getNumPages()):
                page = pdf.getPage(page_number)
                page_list.append({'page': page_number, 'width': page.mediaBox.getLowerRight_x(), 'height': page.mediaBox.getUpperLeft_y()})
            return page_list
        else: return None
        
        
    def joinpdf(self, input_list, output_file):
        """Join list of pdfs to multipage using pyPdf."""
        output = PdfFileWriter()
        for f in input_list:
            input_file = PdfFileReader(file(f, "rb"))
            output.addPage(input_file.getPage(0))
        outputStream = file(output_file, "wb")
        output.write(outputStream)
        outputStream.close()


    def pdf_get_no_pages(self, input_file):
        """Return number of pages in a pdf using pyPdf."""
        try:
            pdf_input = PdfFileReader(file(input_file, "rb"))
            return pdf_input.getNumPages()
        except:
            return None

    def splitpdf(self, input_file, output_dir):
        """Split pdf to single-page files using pyPdf"""  
        try:    
            input1 = PdfFileReader(file(input_file, "rb"))
        except Exception, inst:
            return inst
        files = []
        for page_number in range(0, input1.getNumPages()):
            page = input1.getPage(page_number)
            fname = os.path.basename(input_file).replace('.pdf', '_%s.pdf' % (page_number + 1))
            fpath = os.path.join(output_dir, fname)
            files.append(fpath)
            output = PdfFileWriter()
            output.addPage(page)
            output_stream = file(fpath, "wb")
            output.write(output_stream) 
        return 'saved %s' % files

    


class CommandTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()