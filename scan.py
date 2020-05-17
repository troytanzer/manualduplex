#!/usr/bin/python

import argparse
import numpy
import os
from pathlib import Path
from PIL import Image
import sane
import subprocess
import tempfile

parser = argparse.ArgumentParser(description='A quick and easy way to scan \
multipage documents and put into a PDF file.  Used mostly for paper-reduction \
and the like', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--duplex', type=bool, dest='is_duplex', default=True, help='By default, we \
assume the documents are duplex and we scan all fronts, then all backs.  If \
present, this skips the second step')
parser.add_argument('--outfile', type=str, dest='pdf_file', default='Final.pdf',
                    help='Specify the output file name')
parser.add_argument('--tempdir', type=str, dest='tmp_dir', default='None', \
                    help='Temp file directory for single scan images, if not specified it will create a unique temp dir')
parser.add_argument('--cleantemp', type=bool, dest='clean_tmp', default=True, help='Whether or not to delete the single-page scans after the final pdf is created')
args = parser.parse_args()
print(args)

# set up the options based on CLI args

is_duplex = args.is_duplex
pdf_file = args.pdf_file
if args.tmp_dir is None:
    tmp_dir = mkdtemp(prefix='DuplexScan', dir='/tmp')
else:
    tmp_dir = args.tmp_dir

clean_tmp = args.clean_tmp

# Helper functions

def scan_pages(device, start_page, increment, tmp_file):
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
            save_file = tmp_file % file_no
            print('Saving to {}'.format(save_file))
            page.save(save_file)
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

# Check temp directory and create if needed
test_dir = Path(tmp_dir)
if not test_dir.exists():
    test_dir.mkdir(parents=True)
    
outfilepattern=os.path.join(tmp_dir, 'out%04d.pnm')

# Could check and fix the increment, but it is only for the filename
# and we only care about the sort order
print('Scanning in front side of pages')
if is_duplex:
    increment = 2
else:
    increment = 1
    
num_pages = scan_pages(device, 1, increment, outfilepattern)
print('Scanned in %d pages' % num_pages)
if is_duplex:
    # Give time to flip and straighten the pages
    pause = input("Flip (but don't reorder) the pages and place on the document feeder and press Enter - press any other key to cancel the duplex and generate a PDF with the already scanned pages")
    if pause == '':
        print('Scanning back side of pages')
        scan_pages(device, num_pages * 2, -2, outfilepattern)
    
# There is a python library to bind to the ImageMagik program called Wand.  But, for one
# command, just skip that dependency.

# Note that this depends on convert ordering the files correctly, which it
# does right now, otherwise we'd want to glob the files in the dir and sort 1st
subprocess.run(['convert', '{}/*.pnm'.format(tmp_dir), pdf_file])
print('Concatenated files to %s' % pdf_file)
if clean_tmp:
    print('Cleaning up temp .pnm files from {}'.format(tmp_dir))
    dir_path = Path(tmp_dir)
    for tmpfile in dir_path.glob('*.pnm'):
        tmpfile.unlink()
    dir_path.rmdir()
    
