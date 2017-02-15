import sys, re, os, shutil

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTTextLineHorizontal, LTLine, LTRect
from pdfminer.converter import PDFPageAggregator

from PyPDF2 import PdfFileWriter, PdfFileReader, pdf

from wand.image import Image, Color

# extracts questions from PDF paper at file path, writes cropped output 
# to PDF files and PNG files, each labelled with question number
# also calls java parser to extract text from the question
def extract_questions(file_name, paper_id):

    file_path = 'media/'+file_name   # get uploaded paper

    # make new dir to store this paper's questions
    paper_dir = 'media/papers/'+str(paper_id)+'/'
    os.mkdir(paper_dir)

    device, interpreter, pages = init_pdf(open(file_path, 'rb'))

    page_width = pages[0].mediabox[2]   # gives width each page
    page_height = pages[0].mediabox[3]   # gives height for each page; note, starts at bottom!

    # note PDF origin is at bottom left corner of page
    # bounding box is [lower_left_x, lower_left_y, upper_right_x, upper_right_y]

    _Crop.crop_sizes = []   # clear

    # what trying to find: either 'text' (to identify rubric/start of question) 
    # or 'divider' (to identify end of rubric/question)
    find = 'text'

    find_q = 0   # question to find (let question '0' be the rubric)
    find_sect = 'a'   # section to find

    num_qs = 0   # to tally number of questions before a new section
    has_sections = False   # whether this paper is formed of multiple 'Sections' or not

    part = 'b'   # part of question to look for
    has_parts = False
    part_cut = None   # might be None if no standard marks declaration is found

    footer = 0;   # default

    # define regexs (well, at least the ones that I can define out here)
    rubr_re = re.compile(r'.*time.*:')   # matches line containing 'time...: ' to identify rubric
    whitespace_re = re.compile(r'\s*$')
    footer_re = re.compile(r'.{0,20}(?:\bcont[^\s]*d\b|\bend\b).{0,20}$')   # matches footer text

    for i, page in enumerate(pages):   # traverse pages
        
        lt_objs = process_page(device, interpreter, page)

        # sort layout objects by bottom y position then avg x position
        lt_objs.sort(key=lambda x: (page_height-x.bbox[3],(x.bbox[0]+x.bbox[2])/2))

        # identify position of 'top' of footer on this page
        # used to identify question crop bottom point when there is no divider
        # top of footer *99% of the time* consists of something along the lines of 'continued' or 'end'
        in_footer = []
        for lt_obj in reversed(lt_objs):   # find last 3 non-whitespace text items on the page 
            if len(in_footer) == 3:
                break
            if isinstance(lt_obj, LTTextLineHorizontal):
                if not whitespace_re.match(lt_obj.get_text()):
                    in_footer.append(lt_obj)
        for lt_obj in in_footer:
            if footer_re.match(lt_obj.get_text().lower()):
                footer = lt_obj.bbox[3]
                break

        # traverse sorted layout objects to identify starts and ends of rubric/questions
        for lt_obj in lt_objs:
            if find == 'text':   # looking for rubric/start of a question
                if isinstance(lt_obj, LTTextLineHorizontal):
                    text = lt_obj.get_text().lower()
                    if find_q == 0:   # i.e. looking for rubric
                        if rubr_re.match(text):

                            # think I need a separate method for attempting to get the rubric because the problem is
                            # that the end of it is not always found (c.f. CS257) and then this messes up finding
                            # the questions - could just look for rubric in first page but it's sort of nice to get
                            # it and encapsulate it where possible - but maybe I should just leave it?

                            # set new Crop
                            crop = _Crop('rubric',top=page_height, left=0, right=page_width)
                            find = 'divider'   # now want to find where this ends
                    else:   # looking for start of question
                        sect_re = re.compile(r'\s*section\s'+find_sect)
                        q_re = re.compile(r''+str(find_q)+'\.')
                        qs_re = re.compile(r''+str(find_q-num_qs)+'\.')   # for if there are sections (since numbering may be reset)
                        if sect_re.match(text):   # first check for new section
                            print 'SECTION: '+find_sect.upper()+' FOUND BEFORE Q: '+str(find_q)
                            find_sect = chr(ord(find_sect)+1)   # increment
                            num_qs = find_q-1   # number of questions to this point
                            has_sections = True
                        elif q_re.match(text) or (has_sections and qs_re.match(text)):
                            crop = _Crop('q'+str(find_q),top=lt_obj.bbox[3], left=lt_obj.bbox[0], right=lt_obj.bbox[2])
                            #print 'here:', lt_obj, crop.right
                            find = 'divider'
            
            elif find == 'divider':
                if isinstance(lt_obj, LTTextLineHorizontal):
                    text = lt_obj.get_text();
                    #print text
                    if not whitespace_re.match(text):   # ignore whitespace
                        # reset crop_right if this text stretches further than current crop point
                        this_right = lt_obj.bbox[2];
                       # print crop.right, lt_obj
                        if (this_right > crop.right):
                            crop.set_right(this_right)
                        # set crop_bottom to be at last bit of text before the position of the footer
                        # assumes that questions finish on text (which appears always to be the case e.g. even images mostly have captions)
                        this_bottom = lt_obj.bbox[1]
                        if (this_bottom > footer):
                            crop.set_bottom(this_bottom)

                    # at the moment this just finds 'crop cut points' between each part in a question
                    # this is so that on the front-end question images can be 'split' on each part to reveal
                    # an input box to e.g. write notes for a question part and also to allow overlay over parts
                    # the cropping could be done here to produce a crop for each question part, but it might be
                    # nice to instead itegrate this on the web front-end using whatever is available to do so, in
                    # which case all that will be required is the cut point for each part within each question
                    # i.e. in pt units which hopefully can be used on the web side

                    # compare issues this poses i.e. crop to next part vs. crop to suspected end of part
                    # see CS249 Q5 vs. CS130 SBQ1
                    # currently crop to suspected end of part (*think* that's better)
                    if find_q is not 0:
                        if re.match(r'.{0,10}\('+part+'\)', text):   # find part looking for
                            has_parts = True
                            if part_cut is None:
                                part_cut = last_text_pos
                            print 'Q' + str(find_q) + ' NEW PART CUT: '+str(part_cut)   # this needs storing somewhere - where?!
                            #crop2 = Crop('q'+str(find_q)+chr(ord(part)-1),top=crop.top, left=crop.left, right=crop.right)
                            #crop2.set_bottom(part_cut)
                            #crop2.do_crop(file_path, i, page_height)
                            part_cut = None
                            part = chr(ord(part)+1)   # increment part to look for

                        if re.match(r'.*\[([0-9]{1,2})\]\s*$', text):   # find last marks declaration before start of next part
                            part_cut = lt_obj.bbox[1]   # keeps overwriting
                        else:
                            last_text_pos = lt_obj.bbox[1]   # position of last bit of text before new part; keeps overwriting

                elif _is_divider(lt_obj, page_width, page_height):
                    # found divider so now can do crop with the parameters as set above

                    if has_parts and not find_q == 0:
                        if part_cut is None:
                            part_cut = last_text_pos
                        print 'Q' + str(find_q) + ' NEW PART CUT: '+str(part_cut)
                        #crop2 = Crop('q'+str(find_q)+chr(ord(part)-1),top=crop.top, left=crop.left, right=crop.right)
                        #crop2.set_bottom(part_cut)
                        #crop2.do_crop(file_path, i, page_height)
                        part_cut = None; has_parts = False;

                    crop.do_crop(paper_dir, file_path, i, page_height)
                    find = 'text'; find_q += 1; part = 'b';   # now can look for next question


        if find == 'divider':   # got to end of page and found no divider
            # assume end of page to be the divider, do crop with the parameters as set above

            if has_parts and not find_q == 0:
                if part_cut is None:
                    part_cut = last_text_pos
                print 'Q' + str(find_q) + ' NEW PART CUT: '+str(part_cut)
                #crop2 = Crop('q'+str(find_q)+chr(ord(part)-1),top=crop.top, left=crop.left, right=crop.right)
                #crop2.set_bottom(part_cut)
                #crop2.do_crop(file_path, i, page_height)
                part_cut = None; has_parts = False;

            crop.do_crop(paper_dir, file_path, i, page_height)
            find = 'text'; find_q += 1; part = 'b';

        #marks_extractor.main(sys.argv[1])

    if (find_q == 0):
        raise Exception("FATAL ERROR: no rubric found!")
    elif (find_q == 1):
        raise Exception("FATAL ERROR: no questions found!")

    return find_q-1, _Crop.crop_sizes

# initialisation stuff for the pdfminer package
def init_pdf(file):
    parser = PDFParser(file)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = list(PDFPage.create_pages(document))
    return device, interpreter, pages

def process_page(device, interpreter, page):
    interpreter.process_page(page)
    layout = device.get_result()   # gets page items and their positions

    # populate list of layout objects, extracting child text line objects of text box objects
    lt_objs=[]
    for lt_obj in layout._objs:
        if isinstance(lt_obj, LTTextBoxHorizontal):
            for text_obj in lt_obj._objs:
                lt_objs.append(text_obj)   # want text lines within text box
        else:
            lt_objs.append(lt_obj)   # all other layout objects (line, rect, etc.)

    return lt_objs

# match different types of horizontal lines that represent question dividers
def _is_divider(lt_obj, page_width, page_height):
    if (isinstance(lt_obj, LTLine)
            and lt_obj.bbox[1] == lt_obj.bbox[3]    # is horizontal
            and lt_obj.bbox[2]-lt_obj.bbox[0] > 0.65*page_width):   # sufficiently pans page width
        return True
    if (isinstance(lt_obj, LTRect)   # is a rectangle object
            and round(lt_obj.bbox[3])-round(lt_obj.bbox[1]) <= 1   # is sufficiently thin
            and lt_obj.bbox[2]-lt_obj.bbox[0] > 0.65*page_width):   # sufficiently pans page width
        return True
    # regex to match at least 70 underscores (sometimes used to represent lines!!)
    line_re = re.compile(r'_{70,}')
    if (isinstance(lt_obj, LTTextLineHorizontal)
            and line_re.match(lt_obj.get_text())
            and lt_obj.bbox[2]-lt_obj.bbox[0] > 0.65*page_width):   # sufficiently pans page width
        return True
    return False

class _Crop:

    crop_sizes = []   # stores width/height of each crop

    def __init__(self, name, top=None, left=None, bottom=None, right=None):
        self.name = name
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def set_bottom(self, val):
        self.bottom = val

    def set_right(self, val):
        self.right = val

    def do_crop(self, paper_dir, file_path, page_num, page_height):
        save_as = paper_dir+self.name
        # pass in as arguments: path_to_pdf, page_height, page_num, q_num, x0, y0, x1, y1
        
        command = "java -cp ':pdfbox.jar' ParserByArea %s %s %f %d %s %f %f %f %f" \
        %(file_path,paper_dir,page_height,page_num,self.name,self.left,self.bottom,self.right,self.top)
        os.system(command)

        print "********", self.left, self.bottom, self.right, self.top

        # could write direct to an image and then crop with parameters? - depends if using image or PDF for web app
        if not self.name == 'rubric':
            pdf = PdfFileReader(file_path)
            page = pdf.getPage(page_num)

            # add 50pt padding to either side
            page.mediaBox.lowerLeft = (self.left-50, self.bottom-50)
            page.mediaBox.upperRight = (self.right+50, self.top+50)

            # now fill these padded areas with whitespace
            # (otherwise original content shows through!)

            # white vertical padding 50pt across
            padding = PdfFileReader('scripts/v_white50pt.pdf')
            padding_v = padding.getPage(0)

            # white horizontal padding 50pt up
            padding = PdfFileReader('scripts/h_white50pt.pdf')
            padding_h = padding.getPage(0)

            width = int(self.right-self.left)+100
            height = int(self.top-self.bottom)+100
            print '********w', width   # total width in *pts* including padding
            print '********h', height    # total height in *pts* including padding
            _Crop.crop_sizes.append((width,height))

            # merge padding at appropriate places
            page.mergeTranslatedPage(padding_v, self.left-50, 0)
            page.mergeTranslatedPage(padding_v, self.right, 0)
            page.mergeTranslatedPage(padding_h, 0, self.top)
            page.mergeTranslatedPage(padding_h, 0, self.bottom-50)

            output = PdfFileWriter()
            output.addPage(page)
            outputStream = file(save_as+'.pdf', 'wb')
            output.write(outputStream)   # crop to end of page
            outputStream.close()

            with Image(filename=(save_as+'.pdf'), resolution=100) as img:
                img.background_color = Color('white')
                img.alpha_channel = 'remove'
                img.save(filename=(save_as+'.png'))