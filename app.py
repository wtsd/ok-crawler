"""
	This script fetches comments from the list of links to community posts in
	a Russian social network, OK.ru.
	
	File with links should contain links to a mobile version of the post such as:

		https://m.ok.ru/group/1234567890/topic/1234567890

	Links file should be placed in the `input/` directory with .txt extension
	Name of the file should be put in a `fileSuffix` variable.

	Running:

	$ python app.py [email] [password] [fileSuffix]

		email -- username for an active OK.ru account
		password -- password for an active OK.ru account
		fileSuffix -- filename of urls list in the input/ folder

	Output:

		Comments are being saved to a CSV-formatted file in the `data/` directory.
		Each file has the `records-` prefix and `-date.txt` postfix.
		Encoding is UTF-8.

		Example:

			data/records-ria-stage-1-2020-09-03-193549.csv

	Next steps:

		Import each CSV-file to Excel with UTF-8 encoding. Data > Import from File


"""

import requests
import sys
import csv
import codecs
import time

from datetime import datetime
from bs4 import BeautifulSoup

start_time = time.time()

# Methods
# Read line by line `fname` and put each line into content_array
def get_urls(fname):
    content_array = []
    with open(fname) as f:
        for line in f:
            content_array.append(line.strip())
    return content_array

# Form an array
# Post, Text, Time, Name, ProfileURL, MSGID
def get_comments(html, allComments):
	pageComments = html.select('.discus_dialogs_i.it')
	for comment in pageComments:
		if len(comment.select('.discus_txt.ofh.wbr')) > 0 and len(comment.select('.emphased.usr')) > 0 and len(comment.select('.tstmp')) > 0 and len(comment.select('a[name*="msg"]')) > 0:
			allComments.append([
					postUrl,
					comment.select('.discus_txt.ofh.wbr')[0].text,
					comment.select('.tstmp')[0].text,

					comment.select('.emphased.usr')[0].text,
					'https://ok.ru/'+comment.select('.emphased.usr')[0]['href'],
					
					comment.select('a[name*="msg"]')[0]['name'],
				])
	return allComments

# Save each comment from allComments array to a filename as a CSV
def save_file(allComments, filename):
	csvwriter = None
	file = codecs.open(filename, 'w', encoding='utf-8')
	csvwriter = csv.writer(file)
	
	for row in allComments:
		csvwriter.writerow(row)

def do_authorize(email, password, isMobile = 1):
	if isMobile:
		okLoginUrl = 'https://ok.ru/dk?cmd=AnonymLogin&st.cmd=anonymLogin'
		loginPayload = {
			'st.redirect':		'',
			'st.asr':			'field_asr',
			'st.posted':		'set',
			'st.fJS':			'st.field_fJS',
			'st.st.screenSize':	'2195 x 1235',
			'st.st.browserSize':'973',
			'st.flashVer': 		'0.0.0',
			'st.iscode':		'false',
			'st.email':			email,
			'st.password':		password
			}
	else:
			okLoginUrl = 'https://m.ok.ru/dk?bk=GuestMain&amp;st.cmd=main';
			loginPayload = {
				'fr.posted':		'set',
				'fr.needCaptcha':	'',
				'button_login':		'Log in',
				'fr.login':			email,
				'fr.password':		password
			}

	sess = requests.Session()
	sess.headers.update({
	    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
	}) 

	response = sess.request('POST', okLoginUrl, data=loginPayload)
	html = response.content.decode()
	parsed = BeautifulSoup(html, "html.parser")

	fullNameObj = parsed.select('.tico.ellip')

	# Check if authorization succeeded
	if len(fullNameObj) == 0:
		print('ERROR! Not authorized')
		sys.exit()

	# Continue parsing
	fullName = fullNameObj[0].get_text()
	print("Authorized as " + fullName.strip())

	return sess

############################################
#
# MAIN
#
############################################

# Variables
fileSuffix = ''

################ TEMP ######################
#fileSuffix = 'ria-stage-1' # DONE
#fileSuffix = 'ria-stage-2' # DONE
#fileSuffix = 'ria-stage-3' # DONE

#fileSuffix = 'ren-stage-1' #DONE
fileSuffix = 'ren-stage-2'
#fileSuffix = 'ren-stage-3'
################ /TEMP ######################

# Test file
#fileSuffix = 'urls'

# Fetch arguments: login and password
if len(sys.argv) < 4:
	print('ERROR! Usage: '+ sys.argv[0] + ' email password')
	email = input('Email: ')
	password = input('Password: ')
	fileSuffix = input('File Suffix (input/SUFFIX.txt): ')
	#sys.exit()
else:
	email = sys.argv[1]
	password = sys.argv[2]
	fileSuffix = sys.argv[3]

# Titles:
allComments = [
	['Post', 'Text', 'Time', 'Name', 'ProfileURL', 'MSGID' ]
	]
isMobile = 1
now = datetime.today().strftime('%Y-%m-%d-%H%M%S')
outpuFilename = 'data/records-' + fileSuffix + '-' + now + '.csv'
inputFilename = 'input/' + fileSuffix + '.txt'
prevCount = 0

# Authentication
sess = do_authorize(email, password, isMobile)

# Load URLs from a file
print('Input file:  ' + inputFilename)
print('Output file: ' + outpuFilename)
postUrls = get_urls(inputFilename)

print('Loaded urls: ', len(postUrls))
print('----------------------');

i = 0
for postUrl in postUrls:
	i = i + 1

	# Validate URL
	if postUrl.find('https://m.ok.ru/') == -1:
		continue
	
	# Request a page HTML
	responseMobile = sess.request('GET', postUrl)
	htmlMobile = responseMobile.content.decode()
	parsedProfile = BeautifulSoup(htmlMobile, "html.parser")
	#fullNameProfileObj = parsedProfile.select('#comments-pager-top')

	# Fetch comments
	allComments = get_comments(parsedProfile, allComments)

	# Check if there is a "Prev comments" button
	prevUrl = parsedProfile.select('.dsib.js-load-more.js-load-more-top')
	while len(prevUrl) > 0:
		prevLink = 'https://m.ok.ru' + prevUrl[0]['href']
		#print('Previous link: ' + prevLink)
		responsePrev = sess.request('GET', prevLink)
		htmlPrev = responsePrev.content.decode()
		parsedPrev = BeautifulSoup(htmlPrev, "html.parser")
		
		allComments = get_comments(parsedPrev, allComments)
		prevUrl = parsedPrev.select('.dsib.js-load-more.js-load-more-top')
		time.sleep(2)

	# Print progress to console
	timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	print(i, '/', len(postUrls), 'Post ' + postUrl + ' ; Comments: ', len(allComments), '(+', (len(allComments) - prevCount), ')')
	prevCount = len(allComments)
	save_file(allComments, outpuFilename)
	time.sleep(10)


# Some statistics
print('---------------------')
print('Output file:		', outpuFilename)
print('Total links:		', len(postUrls))
print('Total comments:	', len(allComments))
print("--- Execution time: %s seconds ---" % (time.time() - start_time))
#save_file(allComments, filename)

# EOF