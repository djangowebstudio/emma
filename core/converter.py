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

Future versions of EMMA must address this issue, possibly by using the Quartz bindings.
One (easy) way out of this is to use sips (a command line interface to Quartz 2D) through subprocess.
See also http://en.wikipedia.org/wiki/Quartz_2D and http://delicious.com/geert2705/quartz

In addition to the above, converter.py includes formatDateTime(), and a simple wrapper to 
ffmpeg. The latter needs to be on your path, obviously.

"""
from __future__ import division
import sys, os, shutil
import unittest
import subprocess
# try:
#     from CoreGraphics import *
# except:
#     pass
from CoreGraphics import *    
from datetime import datetime
from time import strptime, strftime
from fnmatch import fnmatch
import logging
import mimetypes
import subprocess
from PIL import Image
import utes
import codecs
from pyPdf import PdfFileWriter, PdfFileReader
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
    
    def convertDocument(self, input_file, output_dir=None):
        '''Convert input file into PDF, using font_size'''
        font_size=12.0 # Get this from settings in a future release
        text = CGDataProviderCreateWithFilename(input_file)
        if not text: 
            try:
                logging.error('%s is empty' % input_file)
            except:
                print ('%s is empty' % input_file)
            return None
        
        (root, ext) = os.path.splitext(input_file)
        if output_dir:
            output_file = os.path.join(output_dir, '.'.join([os.path.splitext(os.path.basename(input_file))[0], 'pdf']))
        else:
            output_file = '.'.join([root,'pdf'])
        
        pageRect = CGRectMake(0, 0, 612, 792)
        c = CGPDFContextCreateWithFilename(output_file, pageRect)
        c.beginPage(pageRect)
        
        if fnmatch(ext,".txt"):
            f = codecs.open(input_file, 'r', encoding='utf-8')
            try: 
                f.read()
                tr = c.drawPlainTextInRect(text, pageRect, font_size)
            except Exception, inst: 
                try:
                    logging.error('Python failed to read %s because %s, exiting' % (input_file, inst))
                except:
                    print ('Python failed to read %s because %s, exiting' % (input_file, inst))
                return None
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
                
                f = codecs.open(input_file, 'r', encoding='utf-8')
                try: 
                    f.read()
                    tr = c.drawPlainTextInRect(text, pageRect, font_size)
                except Exception, inst: 
                    try:
                        logging.error('Python failed to read %s because %s, exiting' % (input_file, inst))
                    except:
                        print ('Python failed to read %s because %s, exiting' % (input_file, inst))
                    return None
                
            else:
                logging.error( "Tried matching strange extension, but still unknown type '%s' for '%s'"%(ext, input_file))
                return None
        else: 
            
            logging.error( "Nothing matched, giving up. Error: unknown type '%s' for '%s'"%(ext, input_file))
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
        """Resize an image using python CoreGraphics bindings for 32-bit machines"""
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
        """ Resize an image using CoreGraphics python bindings for 32-bit machines.
        http://lists.apple.com/archives/quartz-dev/2008/Aug/msg00013.html"""
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
    
    def sips_reformat(self, source, target, format):
        """ Reformats images using sips. See args:
        1) path to source file
        2) path to target dir
        3) format (one of string jpeg | tiff| png | gif | jp2 | pict | bmp | qtif | psd | sgi | tga | pdf)

        """
        if os.path.exists(source):
            cmd = ["sips", "--setProperty", "format", format, source, "--out", target]
            print cmd
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
                print inst
                base_heightwidth = 210
            resize_cmd = ["sips", "--resampleHeight", str(base_heightwidth), "--cropToHeightWidth", str(target_width), str(target_height), "--setProperty", "format", "png", source, "--out", target]
            action = subprocess.Popen(resize_cmd,stdout=subprocess.PIPE).stdout.read()
            return action

        else:
            return None
            
    def stats(self, source):
        """Get some data from an image using PIL."""
        i = Image.open(source)
        i.convert("1")
        i.save(source)
        i = Image.open(source)
        for item in i.getdata():
            if not item == (255, 255, 255):
                print item           
                
    
    def pcopy(self, finput, foutput):
        """ Copies files. Just a simple python wrapper. """
        try:
            shutil.copy(finput, foutput)
            return foutput
        except Exception, inst:
            logging.error('Error copying item %s %s' % (finput, inst)) 
            
            
    def ffmpeg_simple(self, finput, foutput, dimensions=[None,None], verbose=False):
        """A simple version of the ffmpeg wrapper. Takes input & output, optionally the height/width."""
        if dimensions:
            size = 'x'.join(dimensions)
            cmd = ["ffmpeg","-i", finput, "-s", size, "-y", "-ar","11025", "-b", "800", foutput]
        else:
            cmd = ["ffmpeg","-i", finput, "-y", "-ar","11025", foutput]
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)      
        verbose = proc.communicate()[0]
        
        if not verbose: # Return the full path AND filename if verbose is set to True
            if dimensions: 
                return foutput, dimensions
            else:     
                return foutput
        else:
            return verbose
        
        
    
    def ffmpeg(self, finput, foutput, size="other", defaultwidth=917, format='png', verbose=False):
        """ Converts all sorts of video formats to a clip in .flv format or set of images.
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
            cmd = ["ffmpeg","-i", finput, "-y","-ar","11025", foutput]
        elif size == 'cropped':
            cmd = ["ffmpeg","-i",finput,"-y","-fs","100000",foutput]
        elif size == 'tiny' or size == 'small':
            fname = '/'.join([foutput, os.path.splitext(os.path.basename(finput))[0] + ".png"])
            cmd = ["ffmpeg", "-i", finput, "-y", "-vframes", "1", "-ss", "15", fname]
        elif size == 'fullsize':
            fname = '/'.join([foutput, os.path.splitext(os.path.basename(finput))[0] + ".jpg"])
            print fname
            cmd = ["ffmpeg", "-i", finput, "-y", "-vframes", "1", "-ss", "15", fname]
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
        

if __name__ == '__main__':
    c = Convert()
    for root, dirs, files in os.walk('/Users/geert/Desktop/docs'):
        for f in files:
            if not f.endswith('.pdf'):
                print c.convertDocument(os.path.join(root, f), '/Users/geert/Desktop/tmp')


