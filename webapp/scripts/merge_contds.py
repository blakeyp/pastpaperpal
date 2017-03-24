import os

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger, pdf

from wand.image import Image

def main():
	merge('../media/papers/192/')

def merge(paper_dir):

	for file_name in os.listdir(paper_dir):

		if file_name.endswith('n.txt'):
			q_num = file_name.split('q')[1].split('n.txt')[0]
			q_path = paper_dir+'q'+q_num

			print q_path

			with open(q_path+'n.txt', 'r') as r:
				with open(q_path+'.txt', 'a') as a:
					a.write(r.read())
					
			#os.remove(q_path+'n.txt')

			# merger = PdfFileMerger()

			# for f in [q_path+'.pdf', q_path+'n.pdf']:
			# 	merger.append(PdfFileReader(file(f, 'rb')))

			# a4_padding = PdfFileReader('a4_padding.pdf').getPage(0)

			# q_pdf = PdfFileReader(file(q_path+'.pdf', "rb")).getPage(0)

			# q_pdf.mergeTranslatedPage(a4_padding, 0, 100, expand=True)

			# output = PdfFileWriter()
			# output.addPage(q_pdf)
			# outputStream = file(q_path+'nnfffnn.pdf', "wb")
			# output.write(outputStream)
			# outputStream.close()

			# with Image(filename=q_path+'.png') as img:
			# 	with Image(filename=q_path+'n.png') as img2:
			# 		img.crop(height=img.height+img2.height)
			# 		img.composite(img2, 0, img.height)
			# 		img.save(filename=q_path+'gfhff.png')

if __name__ == '__main__':
	main()