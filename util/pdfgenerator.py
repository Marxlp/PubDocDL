#coding:utf-8
#Author: Marxlp
import glob
import os
import imghdr
import threading
from multiprocessing import Process
import math
from fpdf import FPDF
from PyPDF2 import PdfFileMerger

def transfer_images_to_pdf(filepath, filename, pages_num_limit=30):
    print('Generating pdf file. It may take a while.')
    thread = threading.Thread(target=animate_processing)
    thread.daemon = True
    thread.start()

    files = sorted(glob.glob(os.path.join(filepath, '*')))
    if len(files) > pages_num_limit:
        processes = []
        for i in range(math.floor(len(files) / pages_num_limit)):
            process = Process(target=_transfer_images_to_pdf, args=(files[i* pages_num_limit: (i + 1) * pages_num_limit], os.path.join(filepath, str(i) + '_temp.pdf')))
            process.daemon = True
            process.start()
            processes.append(process)

        process = Process(target=_transfer_images_to_pdf, args=(files[(i+1) * pages_num_limit:], os.path.join(filepath, str(i+1) + '_temp.pdf')))
        process.daemon = True
        process.start()
        processes.append(process)

        while processes:
            for process in processes:
                if not process.is_alive():
                    processes.remove(process)
                    break
    
        pdfs = glob.glob(os.path.join(filepath,'*_temp.pdf'))
        merger = PdfFileMerger()
        for pdf in pdfs:
            merger.append(pdf)        
        merger.write(filename)
        
    else:
        _transfer_images_to_pdf(files, filename)
    
    print('Finished.')

def _transfer_images_to_pdf(image_filenames, filename):
    pdf = FPDF()
    if image_filenames:
       for image in image_filenames:
           pdf.add_page()
           pdf.image(image,0,0,210,297,imghdr.what(image).upper())
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

