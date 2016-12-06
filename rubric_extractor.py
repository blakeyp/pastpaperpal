import sys, re

def main():

	# regex to match line that hopefully contains time details e.g. 'Time allowed: 1.5 hours.'
	time_regex = re.compile(r'.*time.*:\s*'   # match hint to time info i.e. '...time...:'
							r'([0-9.]{1,3}'   # open capture; match numbers including decimals
							r'\s{0,2}'   # match any spaces in between
							r'[a-z]+'   # match at least one of any word, hopefully things like 'hours','h','hrs'
							r'[^.]*)')   # match remainder of line excluding dots; close capture

	# regex to match line that hopefully contains calculator details e.g. 'Calculators are not allowed'
	calc_regex = re.compile(r'(?!.*\bno\b.*)'   # don't match if line contains word 'no' (otherwise might be fooled)
							r'.*calculators('   # match anything followed by word 'calculators'; open capture
							r'[^.]*)')   # match remainder of line excluding dots; close capture

	rubric_regex = re.compile(r'.*answer.*question.*\.')

	f = open('../pastpapers/astext/'+sys.argv[1]+'0.txt','rU')   # open text file of past paper PDF

	for line in f:   # iterate over lines

		line = line.strip().lower()   # force case insensitivity

		time_match = time_regex.match(line)   # matches only at beginning of string
		if (time_match):
			parseTime(time_match.group(1))   # pass extracted details (e.g. '2 hours') to function to interpret

		calc_match = calc_regex.match(line)
		if (calc_match):
			parseCalc(calc_match.group(1))   # pass extracted details (e.g. 'are permitted') to function to interpret

		rubric_match = rubric_regex.match(line)
		if (rubric_match):
			parseRubric(rubric_match.group())

	f.close()


def parseTime(line):   # function to interpret line containing time details, returning time allowed in terms of x hours and y minutes

	# match against a mighty regex to attempt to find the time allowed from the line, captured in groups hours and minutes
	
	hrWords = 'hours|hour|hrs|hr|hs|h'
	minWords = 'minutes|minute|mins|min|ms|m'

	# maybe want compiling outside of function?
	hrmin_regex = re.compile(r'^(?:([0-9]{1,3}(?:\.[0-9]{0,2})?)'   # match numbers, optionally a decimal; capture in group 1 for hours
							 r'\s{0,2}'   # match optional spaces in between
							 r'(?:'+hrWords+'))?'   # match a word representing hours, whole hours part is optional
							 r'\s{0,2}'   # match optional spaces in between
							 r'(?:([0-9]{1,3})'   # match numbers, capture in group 2 for minutes
							 r'\s{0,2}'   # match optional spaces in between
							 r'(?:'+minWords+')?)?'   # match a word representing minutes, whole minutes part is optional
							 r'(?<=[0-9rsenmh])$')   # match only if string ends in one of the given characters (stops match empty string)

	hrmin_match = hrmin_regex.match(line)
	
	if (hrmin_match):
		hrs = hrmin_match.group(1)
		mins = hrmin_match.group(2)
		if (mins != None):   # if mins are captured
			if (int(mins) >= 60):   # convert to hours if mins more than 60
				hrs = str(float(mins)/60)
		if (hrs != None):   # if hours are captured
			dec_match = re.match(r'([0-9]{1,2})\.([0-9]{1,2})',hrs)   # check against regex in case decimal number (e.g. '1.5' hours)
			if (dec_match):
				hrs = dec_match.group(1)   # convert into hours and minutes
				mins = str(int(round((float('0.'+dec_match.group(2)))*60)))
		if (mins == '0'):
			mins = None
		print 'timeAllowed: <%s> hours <%s> minutes' %(hrs,mins)
	else:
		print 'sorry, couldn\'t find a suitable time from line:', line


def parseCalc(line):   # function to interpret line containing calculator details, returning whether or not calculators are allowed

	allowed = ['allowed','permitted','can','may']
	negative = ['not','neither','nor']
	prohibited = ['prohibited','forbidden']

	calcsAllowed = None

	calcTokens = line.split()   # split line into individual word tokens

	for i in range(len(calcTokens)):   # traverse tokens
		if calcTokens[i] in prohibited:
			calcsAllowed = False
			break
		elif calcTokens[i] in allowed:
			if (calcTokens[i-1] not in negative) and ((i==len(calcTokens)-1) or (calcTokens[i+1] not in negative)):
				# don't check next token if at end of string
				calcsAllowed = True
				break   # no need to check further
			else:   
				# a negative word preceeds or suceeds an allowed word
				calcsAllowed = False
				break
	print 'calcsAllowed: <%s>' %calcsAllowed


def parseRubric(line):
	#print line

	number = {'one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','ten':'10'}

	numqs_regex = re.compile(r'.*answer\s(?:any\s)?(one|two|three|four|five|six|seven|eight|nine|ten)(?:\squestion(?:s)?)'
							 r'?(?:\sout\sof\s(two|three|four|five|six|seven|eight|nine|ten))?(?:\squestions)?\.$')

	numqs_match = numqs_regex.match(line)

	if (numqs_match):
		choose = numqs_match.group(1)
		out_of = numqs_match.group(2)
		print 'choice: any <%s> out of <%s> questions' %(choose,out_of)


if __name__=="__main__":   # entry point
   main()

