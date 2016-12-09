from PyPDF2 import PdfFileWriter, PdfFileReader, pdf
from wand.image import Image, Color
import os

class Crop:

	def __init__(self, name, top=None, left=None, bottom=None, right=None):
		self.name = name
		self.top = top
		self.left = left
		self.bottom = bottom
		self.right = right
		find = 'divider'

	def set_bottom(self, val):
		self.bottom = val

	def set_right(self, val):
		self.right = val

	def do_crop(self, file_path, page_num, page_height):
		print "ok I'll do a crop now"
		save_as = '../questions/'+self.name
		# pass in as arguments: path_to_pdf, page_height, page_num, q_num, x0, y0, x1, y1
		command = "java -cp '.:pdfbox.jar' ParserByArea %s %f %d %s %f %f %f %f" %(file_path,page_height,page_num,self.name,self.left,self.bottom,self.right,self.top)
		os.system(command)

		# could write direct to an image and then crop with parameters? - depends if using image or PDF for web app
		if not self.name == 'rubric':
			pdf = PdfFileReader(file_path)
			page = pdf.getPage(page_num)
			page.mediaBox.lowerLeft = (self.left, self.bottom)
			page.mediaBox.upperRight = (self.right, self.top)
			output = PdfFileWriter()
			output.addPage(page)
			outputStream = file(save_as+'.pdf', 'wb')
			output.write(outputStream)   # crop to end of page
			outputStream.close()
			with Image(filename=(save_as+'.pdf'), resolution=300) as img:
				img.background_color = Color('white')
				img.alpha_channel = 'remove'
				img.save(filename=(save_as+'.png'))