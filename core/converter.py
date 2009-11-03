#!/usr/bin/env python
# encoding: utf-8
"""
converter.py

Created by Geert Dekkers on 2008-02-11.
Copyright (c) 2008, 2009 Geert Dekkers Web Studio. All rights reserved.

Interfaces CoreGraphics to do the image conversions. The functions are taken from the 
examples given in the macosx dev tools at /Developer/Examples/Quartz/Python. Used with
just minor changes, mostly error handling.

The idea is that while there are native python graphics packages out there (PIL), these don't do all the 
formats we want. The imaging capabilities of macosx surpass these packages easily. So why not use them?

There are drawbacks, however. One apparent drawback is that CoreGraphics can't be used with Apache running as 64 bit app. 
And the interface also seems to be a one-off deal, introduced in 10.3 and supposedly supported by Python 2.3 only
(but it runs happily in 2.5 anyway).

Future versions of eam must address this issue, possibly by using the Quartz bindings. Here, creating context is the problem.
One (easy) way out of this is to use sips (a command line interface to Quartz 2D) through subprocess.
See also http://en.wikipedia.org/wiki/Quartz_2D and http://delicious.com/geert2705/quartz

In addition to the above, converter.py includes formatDateTime(), and a simple wrapper to 
ffmpeg. The latter needs to be on your path, obviously.

"""
from __future__ import division
import sys, os, shutil
import unittest
import subprocess
from CoreGraphics import *
from datetime import datetime
from time import strptime, strftime
from fnmatch import fnmatch
import logging
import mimetypes
import subprocess
from PIL import Image
#--------------------------------------------------------------------------------------------------
# Logging (disabled - uncomment to enable logging for this script)
# The logging calls here are handled by the caller. Only uncomment if you wish to debug this
# script as standalone.
#--------------------------------------------------------------------------------------------------
#
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s %(levelname)-8s %(message)s',
#                    datefmt='%a, %d %b %Y %H:%M:%S',
#                   filename=settings.APP_ROOT + '/logs/converter.log',
#                    filemode='w')
#
#--------------------------------------------------------------------------------------------------

class Convert:
    def __init__(self):
        pass
    
    def convertDocument(self, input_file, font_size=12.0):
        '''Convert input file into PDF, using font_size'''
        text = CGDataProviderCreateWithFilename(input_file)
        if not text: return None
        (root, ext) = os.path.splitext(input_file)
        output_file = root + ".pdf"
        pageRect = CGRectMake(0, 0, 612, 792)
        
        c = CGPDFContextCreateWithFilename(output_file, pageRect)
        c.beginPage(pageRect)
        
        if fnmatch(ext,".txt"):
            tr = c.drawPlainTextInRect(text, pageRect, font_size)
        elif fnmatch(ext,".rtf"):
            tr = c.drawRTFTextInRect(text, pageRect, font_size)
        elif fnmatch(ext,".htm*") or fnmatch(ext,".php"):
            tr = c.drawHTMLTextInRect(text, pageRect, font_size)
        elif fnmatch(ext,".doc"):
            tr = c.drawDocFormatTextInRect(text, pageRect, font_size)
        elif fnmatch(ext,"*ml"):
            tr = c.drawWordMLFormatTextInRect(text, pageRect, font_size)
        elif fnmatch(ext,".?") or fnmatch(ext,".??") or fnmatch(ext,""):
            # Provide one more check on the file to be converted
            if subprocess.Popen('file -bi "%s"' % input_file,shell=True, stdout=subprocess.PIPE).communicate()[0].find('text') == 0:
                tr = c.drawPlainTextInRect(text, pageRect, font_size)
            else:
                logging.error( "Error: unknown type '%s' for '%s'"%(ext, input_file))
                return None
        else: 
            
            logging.error( "Error: unknown type '%s' for '%s'"%(ext, input_file))
            return None
    
        c.endPage()
        c.finish()
        return output_file
    
    def image_from_file(self, filename):
        # special case JPG files and render directly with CG -- this keeps created PDFs smaller
        if (os.path.splitext(filename)[1].upper() == '.JPG') :
            return Image(CGImageCreateWithJPEGDataProvider(CGDataProviderCreateWithFilename (filename), [0,1,0,1,0,1], 1, kCGRenderingIntentDefault))
        return Image(CGImageImport (CGDataProviderCreateWithFilename (filename)))    

    
    def generate_pdf(self, input_list, output_file):
        """ Generates a multipage pdf from a list of JPEG images """
        pageRect = CGRectMake(0, 0, 600, 700) # Give some rect dimensions to init
        context = CGPDFContextCreateWithFilename(str(output_file), pageRect)
        for f in input_list:
            img = CGImageImport(CGDataProviderCreateWithFilename(str(f)))
            pageRect = CGRectMake(0, 0, img.getWidth(), img.getHeight())
            context.beginPage(pageRect)
            success = context.drawImage(pageRect, img)
            context.endPage()
        context.finish()
           
    def convertToBitmap(self, in_file, out_file):
        pdf_file = "/tmp/ps-to-cmyk." + str (os.getpid ()) + ".pdf"

        # Create a PostScript converter and use it to generate a PDF
        # document for our input file

        if not CGPSConverterCreateWithoutCallbacks().convert(CGDataProviderCreateWithFilename(in_file),CGDataConsumerCreateWithFilename(pdf_file)):
            logging.error( "Error while converting %s" % in_file)
        # Open the PDF we just created and delete the temp. file
        try: 
            pdf = CGPDFDocumentCreateWithProvider(CGDataProviderCreateWithFilename(pdf_file))
            os.unlink (pdf_file)
        except Exception, inst:
            logging.error("Failed to create PDF object %s" % inst)

        # Get the bounding box of the content, create a bitmap context
        # of the same size with a white background, and draw the PDF into
        # the context

        try:
            page = pdf.getPage(1)
            r = page.getBoxRect(1)

            cs = CGColorSpaceCreateWithName (kCGColorSpaceUserRGB)
            ctx = CGBitmapContextCreateWithColor ( int(r.size.width), int(r.size.height), cs, (0, 0, 0, 0, 1))
            ctx.drawPDFDocument (r, pdf, 1)
            # Output everything
            ctx.writeToFile (out_file, kCGImageFormatJPEG)    
            return out_file

        except Exception, inst:
            logging.error( "Error converting PDF %(inst)s" % {'inst': inst})
            return None

    
    def convPDF(self, in_file, out_file):
        try:
            pdf = CGPDFDocumentCreateWithProvider (CGDataProviderCreateWithFilename (in_file))
        except Exception, inst:
            logging.error("Error getting pdf from %(in_file)s %(inst)s" % {'in_file' : in_file, 'inst': inst})
            return None
        try:
            page = pdf.getPage(1)
            r = page.getBoxRect(1) 
            cs = CGColorSpaceCreateWithName (kCGColorSpaceUserRGB)
            ctx = CGBitmapContextCreateWithColor ( int(r.size.width), int(r.size.height), cs, (0, 0, 0, 0, 1))
            ctx.drawPDFDocument (r, pdf, 1)

            # Output everything
            ctx.writeToFile (out_file, kCGImageFormatJPEG)    
            return out_file        
        except Exception, inst:
            logging.error( "Error getting PDF %s" % inst)
            return None
    
    def convertPDF(self, pdf_filename, out_path):
        """ Convert a PDF to JPG format. 
        If the input is a multipage PDF, numbered jpg's are outputted.
        Otherwise, the output filename is equal to the input filename, except
        of course for the extension. """
        # Get the filename minus extension.  And from that, the base filname.
        # We're building the output filename(s) from this.
        pdf_name, ext = os.path.splitext( pdf_filename )
        out_name = pdf_name.split('/').pop()

        if pdf_filename == None: return None

        # NOTE: on Panther use cs = CGColorSpaceCreateDeviceRGB()
        cs = CGColorSpaceCreateWithName( kCGColorSpaceGenericRGB )

        # Create the input PDF document
        try:
            provider = CGDataProviderCreateWithFilename( pdf_filename )
            pdf = CGPDFDocumentCreateWithProvider( provider )
        except Exception, inst:
            logging.error("Core Graphics Error %s" % inst)
            logging.error("Error reading PDF document - check that the supplied filename points to a PDF file")
            return None
                    
        try:
            # page number index is 1-based
            for page_number in range( 1, pdf.getNumberOfPages() + 1 ):
                page = pdf.getPage(page_number)
                page_rect = page.getBoxRect(1) 
                if int(page_rect.getWidth()) < 1000:
                    page_rect_resized = CGRectMake(1, 1, (int(page_rect.getWidth()) * 2), (int(page_rect.getHeight()) * 2))
                else:
                    page_rect_resized = CGRectMake(1, 1, int(page_rect.getWidth()), int(page_rect.getHeight()))

                page_width = int(page_rect_resized.getWidth())
                page_height = int(page_rect_resized.getHeight())


                # Create an appropriate bitmap and draw the PDF    
                bitmap = CGBitmapContextCreateWithColor( page_width, page_height, cs, (1, 1, 1, 1) )
                bitmap.drawPDFDocument( page_rect_resized, pdf,  page_number )

                # Write out the bitmap. If the number of pages is greater than 1,
                # add an incremental suffix. 
            
                if pdf.getNumberOfPages() == 1:
                    page_filename = "%s.jpg" % (out_name)
                
                else:
                    page_filename = "%s_%d.jpg" % (out_name, page_number)

            
                out_file = os.path.join(out_path, page_filename)
                bitmap.writeToFile( out_file, kCGImageFormatJPEG )
                logging.info( "Written image: %s, width x height: (%d x %d)" % (out_file, page_width, page_height))
                # Resizing results.
                # This might not be the most efficient way to handle the resizing (most certainly not!), so
                # todo: resize immediately, then build thumbnails based on that.

                self.resize(out_file, out_file, 800, 800)
                self.resize(out_file, out_file.replace('images','thumbs'), 148, 148)
                self.resize(out_file, out_file.replace('images', 'miniThumbs'), 37, 37)
                logging.info("Written resized images to images, thumbs and miniThumbs.")

            return out_file, pdf.getNumberOfPages()
        except Exception, inst:
            logging.error("Error manipulating PDF %s" % inst)
            return None, None
        
    
    def resizeimagePIL(self, source, target, tw, th):
        """ Resize and center image to absolute square with PIL """
        from PIL import Image        
        img = Image.open(source)    
        sw, sh = img.size
        original_aspect = sh/sw
        # resize the image according to its size ratio
        if original_aspect > 1:
            s = (tw, int(original_aspect * tw))            
            img = img.resize(s)
            sw, sh = img.size
            top = int((sh - th) / 2)
            left = int(sw - tw)
            right = int(sw)
            bottom = int(top + th)        
        else:
            s = (int((sw/sh) * th),th)
            img = img.resize(s)
            sw, sh = img.size
            top = 0
            left = int((sw - tw) / 2)
            right = int(left + tw)
            bottom = th
        # crop the image
        box = (left, top, right, bottom)
        area = img.crop(box)
        area.save(target)
        
        
    
    def resize(self, inputfile, outputfile, width=98, height=128):
        try:
            img = CGImageImport(CGDataProviderCreateWithFilename(inputfile))
        except Exception, inst:
            logging.error("Error getting image object from %(in_file)s %(inst)s" % {'in_file' : inputfile, 'inst': inst})
            return None
            
        # Get new dimensions
        try:
            aspect = img.getWidth() / float(img.getHeight())
            h = height
            w = h * aspect
            if w > width:
                w = width
                h = w / aspect
            w = int(w)
            h = int(h)

            # Create new imoge
            c = CGBitmapContextCreateWithColor(w, h, CGColorSpaceCreateDeviceRGB(), (0, 0, 0, 0))
            c.setRGBFillColor(1.0, 1.0, 1.0, 1.0)
            pageRect = CGRectMake(0, 0, w, h)
            c.drawImage(pageRect.inset(0, 0), img)
            # Write image
            c.writeToFile(outputfile, kCGImageFormatJPEG)
            return outputfile
        except Exception, inst:
            logging.error( "an error occurred within CoreGraphics %s" % inst)
            return None
            
    def resizeimage(self, srcimage, targetimage, tw, th):
        """http://lists.apple.com/archives/quartz-dev/2008/Aug/msg00013.html"""
        try:
            srcimg = CGImageImport(CGDataProviderCreateWithFilename(srcimage))
        except Exception, inst:
            logging.error('An error occurred %s' % inst)
            return None
        
        try: 
            sw = srcimg.getWidth()
            sh = srcimg.getHeight()
            aspect = tw/th
            widthfactor = tw/sw    
            heightfactor = th/sh

            if widthfactor < heightfactor:
                #src height stays the same
                #src width gets cropped
                cropwidth = sh * aspect
                x1 = ((sw-cropwidth)/2)
                y1 = 0
                x2 = sw-((sw-cropwidth))
                y2 = sh
            else:
                #src height gets cropped
                #src width stays the same
                cropheight = sw / aspect
                x1 = 0
                y1 = ((sh-cropheight)/2)
                x2 = sw
                y2 = sh-((sh-cropheight))    

            cliprect = CGRectMake(x1, y1, x2, y2)
            croppedimg = srcimg.createWithImageInRect(cliprect)
            c = CGBitmapContextCreateWithColor(tw, th, CGColorSpaceCreateDeviceRGB(), (0,0,0,0))
            # c.setInterpolationQuality(kCGInterpolationLow)
            # newRect = CGRectMake(0, 0, tw, th)
            # c.drawImage(newRect, croppedimg)
            # c.writeToFile(targetimage, kCGImageFormatJPEG)
        except Exception, inst:
            logging.error('An error occurred %s' % inst)
            return None
    
    def resize_with_sips(self, source, target, target_width, target_height):
        """Crops image using sips (command line interface to Quartz 2D)"""
        if os.path.exists(source):
            try:
                i = Image.open(source)
            except:
                return None
            width, height = i.size
            if width > 0 and height > 0:
                aspect = target_width/target_height
                widthfactor = target_width/width  
                heightfactor = target_height/height
            else:
                return None
                
            if widthfactor > heightfactor:
                resize_cmd = ["sips", "--resampleWidth", str(target_width), source, "--out", target]
                resize = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            else:
                resize_cmd = ["sips", "--resampleHeight", str(target_height), source, "--out", target]
                resize = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            
            crop_cmd = ["sips", "--cropToHeightWidth", str(target_width), str(target_height), target]
            crop = subprocess.Popen(crop_cmd, stdout=subprocess.PIPE).stdout.read()
            return crop
    
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
                print inst
        
        if properties:
            for k, v in properties.iteritems(): properties[k] = v.strip()
            return properties
        else:
            return None
                  
    def sips_resize(self, source, target, target_width, format):
        """Scales any source to specified width, respecting aspect.
        Takes source (full path), target (can be directory), target_width (string or int), format (one of string jpeg| tiff| png | gif | jp2 | pict | bmp | qtif | psd | sgi | tga )"""
        
        if os.path.exists(source):
            resize_cmd = ["sips", "--resampleWidth", str(target_width), "--setProperty", "format", format, source, "--out", target]
            print resize_cmd
            action = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            return action
        else:
            return None
            
    def crop_to_center(self, source, target, target_width, target_height):
        """ Scales and then crops source (including a PDF) to center with sips in relation to size.
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
                print inst
                base_heightwidth = 210
            resize_cmd = ["sips", "--resampleHeight", str(base_heightwidth), "--cropToHeightWidth", str(target_width), str(target_height), "--setProperty", "format", "png", source, "--out", target]
            action = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            return action

        else:
            return None
            
    def stats(self, source):
        i = Image.open(source)
        i.convert("1")
        i.save(source)
        i = Image.open(source)
        for item in i.getdata():
            if not item == (255, 255, 255):
                print item           
        
    def crop_to_top_left(self, source, target, target_width, target_height):
        """ Crops source (including a PDF) from top left to square. This function uses sips. """
        # Get all properties in a dict        
        properties = self.sips_get_properties(source)
        
        height = int(properties['pixelHeight'])
        width = int(properties['pixelWidth'])
                
            
    
    # def resize_with_quartz(self, source, target, target_width, target_height):
    #     """ resizes and crops a JPEG (unfinished)"""
    #     from Quartz import * # Quartz and CoreGraphics don't mix! (because of -- obvious -- namespace conflicts)
    #     
    #     d = CGDataProviderCreateWithFilename(source)
    #     i = CGImageCreateWithJPEGDataProvider(d, None, True, kCGRenderingIntentDefault)
    #     width = CGImageGetWidth(i)
    #     height = CGImageGetHeight(i)
    #     print width, height
    #     if width > 0 and height > 0:
    #         aspect = target_width/target_height
    #         widthfactor = target_width/width  
    #         heightfactor = target_height/height
    #         
    #         if widthfactor < heightfactor:
    #             #src height stays the same
    #             #src width gets cropped
    #             cropwidth = height * aspect
    #             x1 = int((width-cropwidth)/2)
    #             y1 = 0
    #             x2 = int(width-((width-cropwidth)))
    #             y2 = int(height)
    #         else:
    #             #src height gets cropped
    #             #src width stays the same
    #             cropheight = width / aspect
    #             x1 = 0
    #             y1 = int(((height-cropheight)/2))
    #             x2 = int(width)
    #             y2 = int(height-((height-cropheight)))    
    #         
    #         cliprect = CGRectMake(x1, y1, x2, y2)
    #         cropped_image = CGImageCreateWithImageInRect(i, cliprect)
    #         print cropped_image
        
  
    # def create_quartz_context(self, width, height):
    #     bitmap_bytes_per_row = int(width * 4)
    #     bitmap_byte_count = int(bitmap_bytes_per_row * height)
    #     color_space = CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB)
    #     bitmap_data = malloc(bitmap_byte_count)
    
    def pcopy(self, finput, foutput):
        """ Copies files. Just a simple python wrapper. """
        try:
            shutil.copy(finput, foutput)
            return foutput
        except Exception, inst:
            logging.error('Error copying item %s %s' % (finput, inst)) 
        
    
    def ffmpeg(self, finput, foutput, size="other", defaultwidth=917):
        """ Converts all sorts of video formats to a clip in .flv format or set of images.
        The number of frames can be set in de args.
        Just a python wrapper to ffmpeg
        
        Takes:
        1. finput (str), a path
        2. foutput (str). This can be:
        a) full path including a filename if arg 3 is "large", or "cropped".
        b) full path to a directory if arg 3 is "tiny", "small", or "fullsize"
        3. size (str), either one of the above, or left blank. In the latter
        case, ffmpeg will be instructed to get the first 180 frames of the source 
        file.
        4. defaultwidth (int), a fallback in case a child function fails to return a value
        
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
        
        # First of all, test the input file 
        if not os.path.exists(finput): return None
        
        dimensions = {} # Init a dict to hold dimensions
        if size == 'large':
            cmd = ["ffmpeg","-i", finput, "-y","-ar","11025", foutput]
        elif size == 'cropped':
            cmd = ["ffmpeg","-i",finput,"-y","-fs","100000",foutput]
        elif size == 'tiny' or size == 'small':
            fname = '/'.join([foutput, os.path.splitext(os.path.basename(finput))[0] + ".png"])
            print fname
            cmd = ["ffmpeg", "-i", finput, "-y", "-vframes", "1", "-ss", "5", fname]
        elif size == 'fullsize':
            fname = '/'.join([foutput, os.path.splitext(os.path.basename(finput))[0] + ".jpg"])
            cmd = ["ffmpeg", "-i", finput, "-y", "-vframes", "1", "-ss", "5", fname]
        else:
            cmd = ["ffmpeg","-i",finput,"-y","-vframes","180","-an","-s","qqvga",foutput]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)      
        print proc.communicate()[0]
        if size == 'tiny': self.crop_to_center(fname, foutput,29,29)
        if size == 'small': self.crop_to_center(fname, foutput,148,148)
        if size == 'fullsize': 
            dimensions = self.sips_get_properties(fname)
            if dimensions: width = dimensions['pixelWidth'] if dimensions.has_key('pixelWidth') else defaultwidth
            self.sips_resize(fname, foutput, width, 'jpeg')
        if dimensions: 
            return foutput, dimensions
        else:     
            return foutput
        
    def formatDateTime(self, d_input):
        if d_input == '':
            return None
        else:

            try:
                dt =  datetime.strptime(d_input, "%Y:%m:%d %H:%M:%S+02:00")
                return dt.isoformat(' ')
            except:
                try:
                    dt = datetime.strptime(d_input, "%Y:%m:%d %H:%M:%S")
                    return dt.isoformat(' ')
                except:
                    try:
                        dt = datetime.strptime(d_input, "%d/%m/%y %H:%M AM")
                        return dt.isoformat(' ')
                    except:
                        try:
                            dt = datetime.strptime(d_input, "%d/%m/%y %H:%M PM")
                            return dt.isoformat(' ')
                        except:
                            try:
                                dt = datetime.strptime(d_input, "%d-%m-%Y %H:%M")
                                return dt.isoformat(' ')
                            except:
                                try:
                                    dt =  datetime.strptime(d_input, "%Y:%m:%d %H:%M:%S+01:00")
                                    return dt.isoformat(' ')
                                except ValueError, inst:
                                    logging.error( "None of the date formats at formatDateTime worked. Given up. %s" % inst)
                                    return None
                                
                        



class ConverterTests(unittest.TestCase):
    def setUp(self):
        pass
        

if __name__ == '__main__': pass
    # c = Convert()
    # for root, dirs, files in os.walk('/Users/geert/Desktop/imgs'):
    #     for f in files:
    #         if not f.startswith('.'):
    #             c.resizeimagePIL(os.path.join(root,f), os.path.join('/Users/geert/Desktop/', f), 148, 148)
    
    #c.resizeimagePIL('/Users/geert/Sites/convert/gallery/images/ANP-logo-fc.jpg','/Users/geert/Desktop/ANP-logo-fc.jpg', 148, 148)
    # c.resizeimage('/Users/geert/Sites/convert/gallery/images/ANP-logo-fc.jpg','/Users/geert/Desktop/ANP-logo-fc.jpg', 148, 148)
    
    # for root, dirs, files in os.walk('/Users/geert/Sites/convert/gallery/images'):
    #     for f in files:
    #         if not f.startswith('.'):
    #             target = os.path.join('/Users/geert/Desktop/results', '.'.join([os.path.splitext(f)[0], 'jpg']))
    #             source = os.path.join(root,f)
    #             c.resize(source, target, 210,210)
    #             c.resizeimage(target, target, 148, 148)
    # for root, dirs, files in os.walk('/Users/geert/Sites/miniNET/httpdocs/gallery/images'):
    #     for f in files:
    #         if not f.startswith('.'):            
    #             print f
    #             source = os.path.join(root, f)
    #             target = os.path.join('/Users/geert/Desktop/test', '.'.join([os.path.splitext(f)[0], 'jpg']))
    #             c.resize_with_sips(source, target, 148, 148)
    #     
        
        
    # print c.crop_to_center('/Volumes/miniHD-red/ccnet2.0/content/Singlepage/0176.99.10_v.pdf', '/Users/geert/Sites/ccnet2.0/gallery/minithumbs', 29, 29)
    #print c.sips_resize('/Volumes/miniHD-red/ccnet2.0/content/Singlepage/0176.99.10_v.pdf', '/Users/geert/Sites/ccnet2.0/gallery/images', 917, 'png')
    # c.stats('/Users/geert/Desktop/test.png')
    # r, d = c.ffmpeg('/Users/geert/Sites/ccnet2.0/content/MOV/NPL.tvcom.JP.020401_20s.mov', '/Users/geert/Desktop', 'fullsize')
    # height = d['pixelHeight']
    # width = d['pixelWidth']
    # print r, d, height, width
    # print c.ffmpeg('/Volumes/miniHD-red/ccnet2.0/content/MOV/NPL.tvcom.JP.020401_20s.mov', '/Users/geert/Desktop', 'fullsize')

