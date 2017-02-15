import re, os

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator

from scripts.parser import init_pdf, process_page   # borrow functions from parser

# check input file is a past paper
# and get paper details i.e. module code/year
def get_details(file):

	module_code = None
	year = None

	code_re = re.compile(r'^([a-z]{2}[0-9]{3})')
	yr_re = re.compile(r'''(?:\s|^)20([0-9]{2})(?:(?:\s+\n?|$)|\/([0-9]{2})(?:\s+\n?|$))''')

	device, interpreter, pages = init_pdf(file)
	
	lt_objs = process_page(device, interpreter, pages[0])

	# populate list of layout objects, extracting child text line objects of text box objects
	# lt_objs=[]
	# for lt_obj in layout._objs:
	# 	if isinstance(lt_obj, LTTextBoxHorizontal):
	# 		for text_obj in lt_obj._objs:
	# 			lt_objs.append(text_obj)   # want text lines within text box
    
    # sort layout objects by bottom y position then avg x position
    # lt_objs.sort(key=lambda x: (page_height-x.bbox[3],(x.bbox[0]+x.bbox[2])/2))

	for i, lt_obj in enumerate(lt_objs):
		text = lt_obj.get_text().lower().strip()
		print text
		code_match = code_re.search(text)
		yr_match = yr_re.search(text)
		if module_code == None and code_match:
			module_code = code_match.group(1)
			continue
		elif year == None and yr_match:
			print 'year match!'
			year = yr_match.group(1) if yr_match.group(2) \
				else yr_match.group(1)
			break

	if module_code == None and year == None:
		raise Exception('module code and year not found!')
	elif module_code == None:
		raise Exception('module code not found!')
	elif year == None:
		raise Exception('year not found!')

	return module_code, year