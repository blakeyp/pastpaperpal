from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer

from pyPdf import PdfFileWriter, PdfFileReader

# Open a PDF file.
fp = open('../pastpapers/cs1180.pdf', 'r')

# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)

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
page_width = pages[0].mediabox[2]   # width of each page
page_height = pages[0].mediabox[3]

#print page_width


def crop(page_num, start, end):
    inputF = PdfFileReader(fp)
    output = PdfFileWriter()
    page = inputF.getPage(page_num-1)

    page.cropBox.lowerLeft = (0, end)
    page.cropBox.upperRight = (page_width, start)
    output.addPage(page)

    return output

crop_count = 0


# def parsePage(lt_objs, page_num):   # breaks if questions aren't enclosed in balanced lines

#     global crop_count, crop_start, crop_end
#     begin_crop = True
    

#     for lt in lt_objs:   # traverse layout page objects

#         # check for line object, horizontal line, and line that pans sufficient width of page
#         if (isinstance(lt, pdfminer.layout.LTLine)) and (lt.bbox[1] == lt.bbox[3]) and (lt.bbox[2]-lt.bbox[0] > 0.75*page_width):
            
#             y_coord = lt.bbox[1]   # 'y' position of this line
#             print 'found horizontal line at y-coord:', y_coord, 'on page:', page_num

#             if begin_crop:   # first line found is crop start line
#                 crop_start=y_coord   # set as crop start
#                 crop_end=None
#                 begin_crop=False
#             else:   # had a crop start line, so presumably this is crop end line

#                 if (crop_start-y_coord < 5):
#                     continue   # double line detected, skip to next line
                
#                 crop_end=y_coord
#                 crop_count+=1
#                 print 'cropping'
#                 outputStream = file("crop"+str(crop_count)+".pdf", "wb")
#                 crop(page_num,crop_start,crop_end).write(outputStream)   # write cropped area to pdf file
#                 outputStream.close()

#                 begin_crop=True   # ready for next crop start

#     print crop_end

#     if crop_end == None:
#         crop_end=0
#         crop_count+=1
#         print 'cropping'
#         outputStream = file("crop"+str(crop_count)+".pdf", "wb")
#         crop(page_num,crop_start,crop_end).write(outputStream)   # write cropped area to pdf file
#         outputStream.close()




def splitPage(lt_objs, page_num):

    global crop_count
    crop_start = page_height

    for lt in lt_objs:   # traverse layout page objects

        # check for line object, horizontal line, and line that pans sufficient width of page
        if (isinstance(lt, pdfminer.layout.LTLine)) and (lt.bbox[1] == lt.bbox[3]) and (lt.bbox[2]-lt.bbox[0] > 0.75*page_width):
            
            y_coord = lt.bbox[1]   # 'y' position of this line
            print 'found horizontal line at y-coord:', y_coord

            if (crop_start-y_coord > 5): # i.e. not a double line
                crop_end=y_coord
                crop_count+=1
                print 'cropping'
                outputStream = file("crop"+str(crop_count)+".pdf", "wb")
                crop(page_num+1,crop_start,crop_end).write(outputStream)   # write cropped area to pdf file
                outputStream.close()
                crop_start=crop_end
    
    crop_end=0
    crop_count+=1        
    print 'cropping'
    outputStream = file("crop"+str(crop_count)+".pdf", "wb")
    crop(page_num+1,crop_start,crop_end).write(outputStream)   # write cropped area to pdf file
    outputStream.close()

    # if double line found
        # mark start, get 'y' value
        # match with closing double line
        # mark as 'rubric'
        # move on

    # line is horizontal, pans page by certain amount end of line x - start of line x = some amount
    # double line must consist of two lines, apart by up to some 1st line y - 2nd line y amount

    # rubric
    # question 1
    # question 2
    # ...
    # question n


for i, page in enumerate(pages):
    interpreter.process_page(page)
    layout = device.get_result()
    splitPage(layout._objs, i)



# def parse_obj(lt_objs):

#     # loop over the object list
#     for obj in lt_objs:

#         # if it's a textbox, print text and location
#         if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
#             print "%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_'))

#         elif isinstance(obj, pdfminer.layout.LTLine):
#             print "%s, %6d, %6d" % ("LINE", obj.bbox[0], obj.bbox[1])

#         # if it's a container, recurse
#         elif isinstance(obj, pdfminer.layout.LTFigure):
#             parse_obj(obj._objs)

# # loop over all pages in the document
# for page in PDFPage.create_pages(document):

#     # read the page into a layout object
#     interpreter.process_page(page)
#     layout = device.get_result()

#     # extract text from this object
#     parse_obj(layout._objs)