
"""
General Utility File for text processing and cleaning
"""

from bs4 import BeautifulSoup
import re
import pytz
import datetime
import hashlib
import requests
from config import g_hash_key

"""
Removes non ascii characters from text
"""
def remove_nonascii(line):
    return ''.join([i if ord(i) < 128 else '' for i in line])

"""
Removes non numeric characters from text
"""

def remove_non_alpha_numeric(line):
    return re.sub('[^0-9a-z]+', ' ',line)

"""
Clean texts by :-
(i)   removing non-ascii characters
(ii)  removing non-alpha numeric characters
(iii) removing stops
(iv)  stemming
"""
def clean_text(token,stop,stemmer):
    token     = token.lower()
    token     = remove_nonascii(token)
    token     = remove_non_alpha_numeric(token)

    result    = []
    tokens    = token.split(" ")
    for tk in tokens:
        tk = tk.strip()
        tk = stemmer.stem(tk)
        if tk.isdigit() or len(tk) == 0 or tk in stop:
            continue
        result.append(tk)
    return result

"""
Generating article-Id 
"""
def generate_articleId(source,document_id):
	return md5_hash(source+ g_hash_key + document_id)
	
def md5_hash(input_str):
	m = hashlib.md5()
	m.update(input_str)
	return m.hexdigest()

"""
Extracting image url from html text. This function was required to extract image from "Guardian" articles
"""
def get_image_from_source(base_url):
	
	result = ""
	response = requests.get(base_url).text
	parsed_html = BeautifulSoup(response,'html.parser')
	image_tags	= parsed_html.find('img')
        
        if 'class' in image_tags.attrs and 'responsive-img' in image_tags.attrs['class']:
		result = image_tags['src']
        return result
"""
Generic method to extract image from html source
"""
def extract_image(news_record,source):

	result = ""
	if 'espn' == source:
		result = "http://assets.espn.go.com/i/espn/teamlogos/lrg/trans/espn_dotcom_black.gif"

	if 'guardian' == source:
		result = get_image_from_source(news_record['link'])

	if result == "" and 'links' in news_record:
		for link_obj in news_record['links']:
			if 'type' in link_obj and (link_obj['type'] == 'image/jpg' or link_obj['type'] == 'image/jpeg'):
				result = link_obj['href']

	if result == ""  and 'media_thumbnail' in news_record:
			for media_obj in news_record['media_thumbnail']:
				if 'url' in media_obj:
					result = media_obj['url']

	return result

"""
Generic method to change time in anytime zone to UTC
"""
def change_time_zone(ctime,zone):

	tzone = pytz.timezone(zone)
	format = "%Y-%m-%d %H:%M:%S"
	date = datetime.datetime.strptime(ctime,format)
	date_zone = tzone.localize(date,is_dst=True)
	return date_zone.astimezone(pytz.utc).strftime(format)	

"""
Utility function to get month name from month number
"""
def getMonth(month_name):
	month_name_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','June':'06',
						'July':'07','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
	if month_name in month_name_dict:
		return month_name_dict[month_name]
	return 0

"""
Removing HTML,CSS,javascript tags from html source
"""
def cleanMe(source,html,stop,stemmer):
    soup = BeautifulSoup(html,'html.parser')
    text =[''.join(s.findAll(text=True))for s in soup.findAll('p')]
    result = []
    for i in xrange(len(text)):
        token = clean_text(text[i],stop,stemmer)
        if '' != token:
            result.append(token)
    return sum(result,[])

"""
Converting datetime in string to YYYY-MM-DD HH:MM:SS
"""
def getDateTime(ts):

	is_est = False
	ts = ts.replace("GMT","+00:00")
	if ts.find("EST") >=0:
		ts = ts.replace("EST","+00:00")
		is_est = True

	result = ""
	tokens = ts.split(",")
	if len(tokens) >=1:
		tokens = tokens[1].strip().split("GMT")
		if len(tokens)>=0:			
			tokens = tokens[0].strip().split(" ")
			result = tokens[2] + "-" + getMonth(tokens[1]) + "-" + tokens[0] + " " + tokens[3]
	
	if is_est == True:
		result = change_time_zone(result,'US/Eastern')

	return result

"""
Sanitizing string before inserting into Database
"""
def clean(token):
	token = BeautifulSoup(token,'html.parser').text
	token = token.replace('"','')
	token = token.replace("'","")
	return token