import re

def main():
	print get_marks(122, 1)

def get_marks(paper_id, q_num):

	# needs to identify and match different ways of expressing marks
	global marks2style
	marks2style = False

	paper_dir = 'media/papers/'+str(paper_id)+'/'
		
	f = open(paper_dir+'q'+str(q_num)+'.txt','rU')
	q_text = f.readlines()   # string containing question text

	part = 'a'   # part of question to look for
	found_parts = False   # whether found first part or not

	part_text = []   # list to contain text lines of each part
	
	total_marks = 0
	part_marks = []   # list containing marks for each part (in order)
	
	for line in q_text:   # traverse text lines of question

		if re.match(r'.{0,10}\('+part+'\)', line):   # if find start of next part e.g. '(b)'
			if len(part_text) != 0:   # if have text lines of previous part to work on
				marks = find_marks(part_text)
				part_marks.append(marks)
				total_marks += marks
				part_text = []   # finished with this part, clear list
			found_parts = True   # found start of the parts in this question
			part = chr(ord(part)+1)   # increment part to look for

		if found_parts:
			part_text.append(line)   # add line to text for this part

	# assume final part continues to end of question
	if found_parts:
		marks = find_marks(part_text)
		part_marks.append(marks)
		total_marks += marks
	else:   # no parts in this question
		total_marks = find_marks(q_text)

	#if total_marks == 0:
		#raise Exception('no marks found for this question!')

	return total_marks, part_marks

def find_marks(text):   # find the number of marks for a question/part

	global marks2style
	
	marks=0
	
	for line in text:   # traverse text lines of part
	 	marks1_regex = re.compile(r'.*\[([0-9]{1,2})(?:\s?mark(?:s)?)?\]\s*$')
	 	marks1_match = marks1_regex.match(line)

	 	marks2_regex = re.compile(r'.*[\s\(]([0-9]{1,2})\s?mark(?:s)?\).*$')
	 	marks2_match = marks2_regex.match(line)

		if not marks2style and marks1_match:   # if find number of marks e.g. [5]
			marks = marks+int(marks1_match.group(1))   # add to marks; add up all marks from 'subparts' of a part
		elif marks2_match:
			marks = marks+int(marks2_match.group(1))
			marks2style = True

	return marks

if __name__=="__main__":   # entry point
   main()