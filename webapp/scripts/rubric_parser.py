import re

def get_rubric(paper_id):

	time = calcs_allowed = choice_choose = choice_outof = choice_text = None

	paper_dir = 'media/papers/'+str(paper_id)+'/'
	f = open(paper_dir+'rubric.txt','rU')

	# regex to match line that hopefully contains time details e.g. 'Time allowed: 1.5 hours.'
	# captures a string containing the time details e.g. '1.5 hours'
	time_regex = re.compile(r'(?:^|\b)time\b.*:\s*'
						 r'([0-9].*[a-z][^.]*)')

	# regex to match line that hopefully contains calculator details e.g. 'Calculators are not allowed'
	calc_regex = re.compile(r'(?!.*\bno\b.*)'   # don't match if line contains word 'no' (otherwise might be fooled)
							r'calculators\s*([^.]*)')   # capture remainder of line after 'calculators' exluding closing dot

	choice_regex = re.compile(r'\b[Aa]nswer\s'
							  r'(.*\bquestion[^.]*)')
	
	for line in f:   # iterate over lines

		line = line.strip()

		time_match = time_regex.search(line.lower())
		if time_match and not time:
			time = parse_time(time_match.group(1))

		calc_match = calc_regex.search(line.lower())
		if calc_match and calcs_allowed is None:
			calcs_allowed = parse_calc(calc_match.group(1))

		choice_match = choice_regex.search(line)
		if choice_match and not choice_text:
			choice_choose, choice_outof = parse_choice(choice_match.group(1))
			choice_text = choice_match.group()

	f.close()

	return time, calcs_allowed, choice_choose, choice_outof, choice_text

def parse_time(line):   # function to interpret line containing time details, returning time allowed in terms of x hours and y minutes

	# match against a mighty regex to attempt to find the time allowed from the line, captured in groups hours and minutes
	
	hrWords = 'hours|hour|hrs|hr|hs|h'
	minWords = 'minutes|minute|mins|min|ms|m'

	hrmin_regex = re.compile(r'(?:([0-9]{1,3}(?:\.[0-9]{0,2})?)'   # match numbers, optionally a decimal; capture in group 1 for hours
							 r'\s{0,2}'   # match optional spaces in between
							 r'(?:'+hrWords+'))?'   # match a word representing hours; whole hours part to here is optional
							 r'\s{0,2}'   # match optional spaces in between
							 r'(?:([0-9]{1,3})'   # match numbers, capture in group 2 for minutes
							 r'\s{0,2}'   # match optional spaces in between
							 r'(?:'+minWords+')?)?')   # match a word representing minutes; whole minutes part to here is optional

	hrmin_match = hrmin_regex.match(line)

	if hrmin_match:
		hrs = hrmin_match.group(1)
		mins = hrmin_match.group(2)
		total_mins = convert_hrsmins(hrs, mins)
		return total_mins
	else:
		raise Exception('No time found!')

# convert captured hrs_mins strings to total time in integer minutes
def convert_hrsmins(hrs, mins):
	
	if mins and not hrs:   # if mins are captured but not hours
		return int(mins)   # total is just mins

	if mins and hrs:
		return int(hrs)*60 + int(mins)

	if hrs and not mins:
		dec_match = re.match(r'([0-9]{1,2})\.([0-9]{1,2})', hrs)   # check against regex in case decimal number (e.g. '1.5' hours)
		if dec_match:
			hrs = dec_match.group(1)   # convert into hours and minutes
			mins = int(round((float('0.'+dec_match.group(2)))*60))
			return int(hrs)*60 + mins
		else:
			return int(hrs)*60


def parse_calc(line):   # function to interpret line containing calculator details, returning whether or not calculators are allowed

	allowed = ['allowed','permitted','can','may']
	negative = ['not','neither','nor']
	prohibited = ['prohibited','forbidden']

	calcs_allowed = None

	calc_toks = line.split()   # split line into individual word tokens

	for i in range(len(calc_toks)):   # traverse tokens
		if calc_toks[i] in prohibited:
			calcs_allowed = False
			break
		elif calc_toks[i] in allowed:
			# don't check next token if at end of string
			if (calc_toks[i-1] not in negative) and \
			   ((i==len(calc_toks)-1) or (calc_toks[i+1] not in negative)):
				calcs_allowed = True
				break   # no need to check further
			else:   # a negative word preceeds or suceeds an allowed word
				calcs_allowed = False
				break

	return calcs_allowed


def parse_choice(line):
	choose = None; out_of = None;

	number = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10}

	numqs_regex = re.compile(r'\b(one|two|three|four|five|six|seven|eight|nine|ten)(?:\squestions)?'
							 r'(?:\sout\sof\s(two|three|four|five|six|seven|eight|nine|ten))?')

	numqs_match = numqs_regex.search(line.lower())

	if numqs_match:
		choose = numqs_match.group(1)
		out_of = numqs_match.group(2)

	return number.get(choose,None), number.get(out_of,None)