#coding:utf-8
#Author: Marxlp
import glob
import os
import imghdr
from fpdf import FPDF
import threading

def transfer_images_to_pdf(filepath, filename):
    pdf = FPDF()
    files = sorted(glob.glob(os.path.join(filepath, '*')))
    count = 0
    total_number = len(files)
    print('Generating pdf file. This may take a while')
    for image in files:
        pdf.add_page()
        pdf.image(image,0,0,210,297,imghdr.what(image).upper())
        count += 1
    thread = threading.Thread(target=animate_processing)
    thread.daemon = True
    thread.start()
    pdf.output(filename,'F')


def animate_processing():
    import time
    import sys
    current_char = '/'
    progress_chars = {'-':'\\','\\':'|','|':'/','/':'-'}
    while True:
        sys.stdout.write(current_char)
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b\b')
        sys.stdout.flush()
        current_char = progress_chars[current_char]

if __name__ == '__main__':
    transfer_images_to_pdf('_temp','test2.pdf')

