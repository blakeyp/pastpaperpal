import re, os

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

from questions_extractor import extract_qs

# check input file is a past paper
# and get paper details i.e. module code/year
def get_details(file):

	module_code = None
	year = None

	code_re = re.compile(r'^([a-z]{2}[0-9]{3})')
	yr_re = re.compile(r'''(?:\s|^)20([0-9]{2})(?:(?:\s+\n?|$)|\/([0-9]{2})(?:\s+\n?|$))''')

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
	
	interpreter.process_page(pages[0])
	layout = device.get_result()

	# need to get text lines not boxes!

	for i, lt_obj in enumerate(layout._objs):
		try:
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
		except AttributeError:
			continue   # not a text object, continue

	if module_code == None and year == None:
		raise Exception('module code and year not found!')
	elif module_code == None:
		raise Exception('module code not found!')
	elif year == None:
		raise Exception('year not found!')

	return module_code, year

def extract_questions(file_name, paper_id):

    paper_dir = 'media/papers/'+str(paper_id)+'/'
    os.mkdir(paper_dir)

    file_path = 'media/'+file_name
    return extract_qs(file_path, paper_dir)