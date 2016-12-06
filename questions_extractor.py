# extracts questions from PDF paper at file path, writes cropped output 
# to PDF files and PNG files, each labelled with question number
# also calls java parser to extract text from the question

from __future__ import division
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer, re

from wand.image import Image, Color

from PyPDF2 import PdfFileWriter, PdfFileReader, pdf

import os, sys

def main():

    file_path = '../pastpapers/'+sys.argv[1]+'0.pdf'

    # Open a PDF file.
    open_pdf = open(file_path, 'rb')

    # Create a PDF parser object associated with the file object.
    parser = PDFParser(open_pdf)

    # Create a PDF document object that stores the document structure.
    # Password for initialization as 2nd parameter
    document = PDFDocument(parser)

    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS
    # Set parameters for analysis.
    laparams = LAParams()

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    pages = list(PDFPage.create_pages(document))
    page_width = pages[0].mediabox[2]   # gives width each page
    page_height = pages[0].mediabox[3]   # gives height for each page; note, starts at bottom

    # note PDF origin is at bottom left corner of page
    # note bounding box is [lower_left_x, lower_left_y, upper_right_x, upper_right_y]

    look_for_q = 1   # question number to search for

    for i, page in enumerate(pages):   # traverse pages
        interpreter.process_page(page)
        layout = device.get_result()

        lt_objs=[]

        # populate list of layout objects, extracting child text line objects of text box objects
        for lt_obj in layout._objs:
            if isinstance(lt_obj, pdfminer.layout.LTTextBoxHorizontal):
                for text_obj in lt_obj._objs:
                    lt_objs.append(text_obj)   # want text lines within text box
            else:
                lt_objs.append(lt_obj)

        # sort layout objects by average y position on page
        lt_objs.sort(key=lambda x: (x.bbox[1]+((x.bbox[1]-x.bbox[3])/2)), reverse=True)

        # identify position of 'top' of footer on this page
        # used to identify question crop end point when there is no divider
        # top of footer *99% of the time* consists of something along the lines of 'continued' or 'end'
        # this implementation is verbose - could be rewritten!
        in_footer = []
        for lt_obj in reversed(lt_objs):   # find last 3 non-whitespace text items on the page 
            if len(in_footer) == 3:
                break
            if isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal):
                whitespace_re = re.compile(r'\s*$')
                if not whitespace_re.match(lt_obj.get_text()):
                    in_footer.append(lt_obj)
        for lt_obj in in_footer:
            footer_re = re.compile(r'.{0,20}(?:\bcont[^\s]*d\b|\bend\b).{0,20}$')
            if footer_re.match(lt_obj.get_text().lower()):
                footer_pos = lt_obj.bbox[3]
                break

        find_q = True   # whether looking for start of question or not

        # traverse sorted layout objects to identify starts and ends of questions
        for lt_obj in lt_objs:

            if find_q:   # looking for start of a question
                if isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal):
                    # regex to match start of question e.g. '2.'
                    q_re = re.compile(r''+str(look_for_q)+'\.')
                    if q_re.match(lt_obj.get_text()):
                        crop_top = lt_obj.bbox[3]   # top *y* position of crop
                        crop_left = lt_obj.bbox[0]   # left *x* position of crop
                        crop_right = lt_obj.bbox[2]   # to be updated if necessary
                        find_q = False   # switch

            else:   # looking for end of question
                end_q_re = re.compile(r'\[[0-9]{0,3}(?:\s?marks?)?\]$')   # matches marks in a question e.g. '[5 marks]'
                if is_divider(lt_obj, page_width, page_height):   # found question divider
                    crop(file_path,i,page_height,look_for_q,crop_top,crop_left,crop_end,crop_right)
                    look_for_q += 1   # moving on to look for next question
                    find_q = True
                    crop_right = 0   # reset
                else:
                    if isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal):
                        #print lt_obj, '\n'
                        # right *x* position of crop to be farthest right reaching text within question
                        if (lt_obj.bbox[2] > crop_right):
                            crop_right = lt_obj.bbox[2]
                        # bottom *y* position of crop to be at last item before question divider
                        if not whitespace_re.match(lt_obj.get_text()):   # ignore whitespace
                            pos = lt_obj.bbox[1]
                            if (not pos <= footer_pos):   # still above footer
                                crop_end = pos
                # what if the question ends on some other object i.e. not text ?!

        if not find_q:   # got to end of page and found no divider
            # assume end of page to be the divider, do the crop with the values found above
            crop(file_path,i,page_height,look_for_q,crop_top,crop_left,crop_end,crop_right)
            look_for_q+=1   # ready to look for next question
            find_q = True
            crop_right = 0   # reset


# match different types of horizontal lines that represent question dividers
def is_divider(lt_obj, page_width, page_height):
    if (isinstance(lt_obj, pdfminer.layout.LTLine)
            and lt_obj.bbox[1] == lt_obj.bbox[3]    # is horizontal
            and lt_obj.bbox[2]-lt_obj.bbox[0] > 0.65*page_width):   # sufficiently pans page width
        return True

    if (isinstance(lt_obj, pdfminer.layout.LTRect)   # is a rectangle object
            and round(lt_obj.bbox[3])-round(lt_obj.bbox[1]) <= 3   # is sufficiently thin
            and lt_obj.bbox[2]-lt_obj.bbox[0] > 0.65*page_width):   # sufficiently pans page width
        return True

    # regex to match at least 70 underscores (sometimes used to represent lines!!)
    line_re = re.compile(r'_{70,}')
    if (isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal)
            and line_re.match(lt_obj.get_text())
            and lt_obj.bbox[2]-lt_obj.bbox[0] > 0.65*page_width):   # sufficiently pans page width
        return True

    return False

# crop an area of a PDF page, write to a PNG image file
def crop(file_path, page_num, page_height, q_num, top, left, bottom, right):
    pdf = PdfFileReader(file_path)
    page = pdf.getPage(page_num)

    #print '\nQUESTION %d' %q_num
    #print 'lowerLeft: (%d,%d)' %(left,bottom)
    #print 'upperRight: (%d,%d)' %(right,top)

    page.mediaBox.lowerLeft = (left, bottom)
    page.mediaBox.upperRight = (right, top)

    # page.trimBox.lowerLeft = (left-5, bottom-5)
    # page.trimBox.upperRight = (right+5, start+5)

    # page.cropBox.lowerLeft = (left-20, bottom-20)
    # page.cropBox.upperRight = (right+20, start+20)

    output = PdfFileWriter()
    output.addPage(page)
    outputStream = file("../questions/q"+str(q_num)+".pdf", "wb")
    output.write(outputStream)   # crop to end of page
    outputStream.close()

    # write direct to image then crop image??

    with Image(filename=('../questions/q'+str(q_num)+'.pdf'), resolution=300) as img:
        img.background_color = Color('white')
        img.alpha_channel = 'remove'
        img.save(filename=('../questions/q'+str(q_num)+'.png'))

    # pass in as arguments: path_to_pdf, page_height, page_num, q_num, x0, y0, x1, y1
    command = "java -cp '.:pdfbox.jar' ParserByArea %s %f %d %d %f %f %f %f" %(file_path,page_height,page_num,q_num,left,bottom,right,top)

    #print command

    os.system(command)

if __name__=="__main__":   # entry point
   main()