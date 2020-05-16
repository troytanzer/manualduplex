#!/usr/bin/python

# Config options - move to CLI options
is_duplex = True
pdf_file = "Final.pdf"

# Look up the iterator online and see if it gets a signal from
# the ADF to indicate # of pages
import numpy
import sane
from PIL import Image
import subprocess

def scan_pages(device, start_page, increment):
    num_pages = 0
    #get an iterator over all the pages
    iter = device.multi_scan()
    #ADF should stop once the last page is scanned with a StopIteration error
    while True:
        print('Scanning page %d' % num_pages)
        try:
            page = iter.next()
            num_pages += 1
            file_no = start_page+(num_pages-1)*increment
            page.save('out%04d.pnm' % file_no)
            page.close()
        except StopIteration:
            break
    return num_pages  

#We only have one scanner, so just use the first one returned.  Otherwise, we'd
#want to scan for the make, or pass it in on the CLI
sane.init()
devices = sane.get_devices()
print(devices)
print('Selecting the first device by default : {}'.format(devices[0][0]))
device = sane.open(devices[0][0])
device.mode = 'gray'
device.resolution = 300
print('Device parameters:')
print(device.get_parameters())

#Use dev.get_options() to see everything we can set
#device.start()

# Could check and fix the increment, but it is only for the filename
# and we only care about the sort order
print('Scanning in front side of pages')
num_pages = scan_pages(device, 1, 2)
print('Scanned in %d pages' % num_pages)
if is_duplex:
    # Give time to flip and straighten the pages
    pause = input("Flip (but don't reorder) the pages and place on the document feeder and press Enter - press any other key to cancel the duplex and generate a PDF with the already scanned pages")
    if pause == '':
        print('Scanning back side of pages')
        scan_pages(device, num_pages * 2, -2)
    
# Is there a python library to ImageMagik?  Right now, just shell out
# to convert the pnm files to a multi-page PDF - requires imagemagik to be
# installed and on the path

subprocess.run(['convert', '*.pnm', pdf_file])
print('Concatenated files to %s' % pdf_file)



