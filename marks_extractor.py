import re, os, sys

def main(paper):

	q_marks = []   # list of lists one for each question with the num marks for each of its parts

	for file in os.listdir('../questions'):   # traverse text files of questions

		if file.endswith('.txt'):
			f = open('../questions/'+file,'rU')
			q_text = f.readlines()   # string containing question text

			q_num = int(file.split('q')[1].split('.txt')[0])
			#print '----------------------------------\nQUESTION:', q_num; print

			part = 'a'   # part of question to look for
			part_text = []   # list to contain text lines of each part
			part_marks = []
			found_parts = False   # whether found first part or not

			for line in q_text:   # traverse text lines of question

				if re.match(r'.{0,10}\('+part+'\)', line):   # if find start of next part e.g. '(b)'
					if len(part_text) != 0:   # have text lines of previous part to work on
						part_marks.append(find_marks(part_text))
						part_text = []   # finished with this part, empty list
					found_parts = True   # found start of the parts in this question
					part = chr(ord(part)+1)   # increment part to look for

				if found_parts:   # something to add to text of part
					part_text.append(line)

			# assume final part continues to end of question
			if found_parts:
				part_marks.append(find_marks(part_text))
				q_marks.append(part_marks)
			else:
				q_marks.append(find_marks(q_text))
			

	total_marks=0

	f=open('../marks'+paper,'w')

	for i, part_marks in enumerate(q_marks):
		#print
		if type(part_marks) == int:
			f.write('Q%d - %d marks\n' %((i+1),part_marks))
			total_marks+=part_marks
		else:
			f.write('Q%d - %d marks\n' %((i+1),sum(part_marks)))
			for i, marks in enumerate(part_marks):
				f.write('  Part (%s) - %d marks\n' %((chr(ord('a')+i),marks)))
				total_marks+=marks

	#print
	f.write('TOTAL NUM QUESTIONS: '+str(len(q_marks))+'\n')
	f.write('TOTAL NUM MARKS: '+str(total_marks)+'\n')
	#print

def find_marks(text):   # find the number of marks for a question part
	#print 'PART:', part
	marks=0
	for line in text:   # traverse text lines of part
	 	marks_regex = re.compile(r'.*\[([0-9]{1,2})\]\s*$')
	 	marks_match = marks_regex.match(line)
		if marks_match:   # if find number of marks e.g. [5]
	 		# add to marks; add up all marks from 'subparts' of a part
			marks = marks+int(marks_match.group(1))
			#print line, marks
	#print 'MARKS:', marks; print
	return marks

if __name__=="__main__":   # entry point
   main()