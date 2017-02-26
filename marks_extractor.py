import re, os, sys

def main():

	global marks2style

	#paper = sys.argv[1]

	q_marks = []   # list of lists one for each question with the num marks for each of its parts

	for file in os.listdir('../media/papers/104'):   # traverse text files of questions
		
		marks2style = False

		if file.endswith('.txt'):
			if file.endswith('0.txt') or file.endswith('rubric.txt'):
				continue
			f = open('../media/papers/104/'+file,'rU')
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

	f=open('../media/papers/104/marks.txt','w')

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
	global marks2style
	marks=0
	for line in text:   # traverse text lines of part
	 	marks1_regex = re.compile(r'.*\[([0-9]{1,2})(?:\s?marks)?\]\s*$')
	 	marks1_match = marks1_regex.match(line)
	 	marks2_regex = re.compile(r'.*\(([0-9]{1,2})\s?marks\).*$')
	 	marks2_match = marks2_regex.match(line)
		if not marks2style and marks1_match:   # if find number of marks e.g. [5]
	 		# add to marks; add up all marks from 'subparts' of a part
			marks = marks+int(marks1_match.group(1))
		elif marks2_match:
			print 'yes'
			marks = marks+int(marks2_match.group(1))
			marks2style = True
			#print line, marks
	#print 'MARKS:', marks; print
	return marks

if __name__=="__main__":   # entry point
   main()