import sys, re

from pyparsing import Word, alphas

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

	f = open(sys.argv[1]+".txt")   # open text file of past paper PDF

	for line in f:   # iterate over lines

		line = line.strip().lower()   # force case insensitivity

		time_match = time_regex.match(line)   # matches only at beginning of string
		if (time_match):
			parseTime(time_match.group(1))   # pass extracted details (e.g. '2 hours') to function to interpret

		calc_match = calc_regex.match(line)
		if (calc_match):
			parseCalc(calc_match.group(1))   # pass extracted details (e.g. 'are permitted') to function to interpret

	f.close()

	pass

def parseTime(line):   # function to interpret line containing time details, returning time allowed in terms of x hours and y minutes

	# match against a mighty regex to attempt to find the time allowed from the line, captured in groups hours and minutes
	
	hrWords = 'hours|hour|hrs|hr|hs|h'
	minWords = 'minutes|minute|mins|min|ms|m'

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
		if (hrs != None):   # if hours are captured
			dec_match = re.match(r'([0-9]{1,2})\.([0-9]{1,2})',hrs)   # check against regex in case decimal number (e.g. '1.5' hours)
			if (dec_match):
				hrs = dec_match.group(1)   # convert into hours and minutes
				mins = str(int((float('0.'+dec_match.group(2)))*60))
		if (mins >= 60):
			print 'need to convert to hours!'
		print 'timeAllowed:', hrs, 'hours', mins, 'minutes'
	else:
		print 'sorry, couldn\'t find a suitable time from line:', line

	return

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
	print 'calcsAllowed:', calcsAllowed

	return

if __name__=="__main__":   # entry point
   main()