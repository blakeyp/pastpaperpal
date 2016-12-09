# extracts questions from PDF paper at file path, writes cropped output 
# to PDF files and PNG files, each labelled with question number
# also calls java parser to extract text from the question

#from __future__ import division

import sys, re

from cropping import Crop

import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

def main():

    file_path = '../pastpapers/'+sys.argv[1]+'0.pdf'

    # initialisation stuff for the pdfminer package
    open_pdf = open(file_path, 'rb')
    parser = PDFParser(open_pdf)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = list(PDFPage.create_pages(document))

    page_width = pages[0].mediabox[2]   # gives width each page
    page_height = pages[0].mediabox[3]   # gives height for each page; note, starts at bottom!

    # note PDF origin is at bottom left corner of page
    # bounding box is [lower_left_x, lower_left_y, upper_right_x, upper_right_y]

    # what trying to find: either 'text' (to identify rubric/start of question) 
    # or 'divider' (to identify end of rubric/question)
    find = 'text'

    find_q = 0   # question to find (let question '0' be the rubric)
    find_sect = 'a'   # section to find

    # define regexs (well, at least the ones that I can define out here)
    rubr_re = re.compile(r'.*time.*:')   # matches line containing 'time...: ' to identify rubric
    whitespace_re = re.compile(r'\s*$')
    footer_re = re.compile(r'.{0,20}(?:\bcont[^\s]*d\b|\bend\b).{0,20}$')   # matches footer text

    for i, page in enumerate(pages):   # traverse pages
        
        interpreter.process_page(page)
        layout = device.get_result()

        # populate list of layout objects, extracting child text line objects of text box objects
        lt_objs=[]
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
        in_footer = []
        for lt_obj in reversed(lt_objs):   # find last 3 non-whitespace text items on the page 
            if len(in_footer) == 3:
                break
            if isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal):
                if not whitespace_re.match(lt_obj.get_text()):
                    in_footer.append(lt_obj)
        for lt_obj in in_footer:
            if footer_re.match(lt_obj.get_text().lower()):
                footer = lt_obj.bbox[3]
                break

        # traverse sorted layout objects to identify starts and ends of rubric/questions
        for lt_obj in lt_objs:

            if find == 'text':   # looking for rubric/start of a question
                if isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal):
                    text = lt_obj.get_text().lower()
                    if find_q == 0:   # i.e. looking for rubric
                        if rubr_re.match(text):
                            # set new Crop
                            crop = Crop('rubric',top=page_height, left=0, right=page_width)
                            find = 'divider'   # now want to find where this ends
                    else:   # looking for start of question
                        sect_re = re.compile(r'\s*section\s'+find_sect)
                        q_re = re.compile(r''+str(find_q)+'\.')
                        if sect_re.match(text):   # first check for new section
                            print 'SECTION: '+find_sect.upper()+' FOUND BEFORE Q: '+str(find_q)
                            find_sect = chr(ord(find_sect)+1)   # increment
                        elif q_re.match(text):
                            crop = Crop('q'+str(find_q),top=lt_obj.bbox[3], left=lt_obj.bbox[0], right=lt_obj.bbox[2])
                            find = 'divider'
            
            elif find == 'divider':
                if isinstance(lt_obj, pdfminer.layout.LTTextLineHorizontal):
                    if not whitespace_re.match(lt_obj.get_text()):   # ignore whitespace
                        # reset crop_right if this text stretches further than current crop point
                        this_right = lt_obj.bbox[2];
                        if (this_right > crop.right):
                            crop.set_right(this_right)
                        # set crop_bottom to be at last bit of text before the position of the footer
                        # what if the question ends on some other object i.e. not text ?!
                        this_bottom = lt_obj.bbox[1]
                        if (this_bottom > footer):
                            crop.set_bottom(this_bottom)
                elif is_divider(lt_obj, page_width, page_height):
                    # found divider so now can do crop with the parameters as set above
                    crop.do_crop(file_path, i, page_height)
                    find = 'text'; find_q += 1   # now can look for next question


        if find == 'divider':   # got to end of page and found no divider
            # assume end of page to be the divider, do crop with the parameters as set above
            crop.do_crop(file_path, i, page_height)
            find = 'text'; find_q += 1

        #marks_extractor.main(sys.argv[1])

    if (find_q == 0):
        raise Exception("FATAL ERROR: no rubric found!")
    elif (find_q == 1):
        raise Exception("FATAL ERROR: no questions found!")


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

if __name__=="__main__":   # entry point
   main()