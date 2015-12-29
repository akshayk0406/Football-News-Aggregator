import psycopg2
import datetime
import sys
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import *

conn_string = "host='127.0.0.1' dbname='news' user='don' password='$g3WE28%H3'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

day_limit	= 1
hours_limit = 12
start_time  = (datetime.datetime.utcnow() - datetime.timedelta(hours=hours_limit)).strftime("%Y-%m-%d %H:%M:%S")
sql_query	= "select id,fid,source,href,title,image,created_date from football_news.news where created_date >= '" + start_time + "' order by created_date desc"
cursor.execute(sql_query)
records 	= cursor.fetchall()

result		= []
for record in records:
	
	result_obj					= {}
	result_obj['id'] 			= record[0]
	result_obj['fid'] 			= record[1]
	result_obj['source'] 		= record[2]
	result_obj['href']			= record[3]
	result_obj['title'] 		= record[4]
	result_obj['image'] 		= record[5]
	result_obj['created_date'] 	= record[6]
	result.append(result_obj)


cursor.close()
conn.close()

output_file     = sys.argv[1]
def remove_nonascii(line):
    return ''.join([i if ord(i) < 128 else '' for i in line])

def remove_non_alpha_numeric(line):
    return re.sub('[^0-9a-z]+', ' ',line)

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

def cleanMe(source,html,stop,stemmer):
    soup = BeautifulSoup(html,'html.parser')
    text =[''.join(s.findAll(text=True))for s in soup.findAll('p')]
    text = text[3:-7]
    result = []
    for i in xrange(len(text)):
        token = clean_text(text[i],stop,stemmer)
        if '' != token:
            result.append(token)
    return sum(result,[])

stop = stopwords.words('english')
stemmer = PorterStemmer()
bow     = []
document_id = []

for news_object in result:
    base_url = news_object['href']
    response = requests.get(base_url).text
    bow.append(Counter(cleanMe(news_object['source'],response,stop,stemmer)))
    document_id.append(int(news_object['id']))

feature_id      = 0
feature_id_map  = {}
for document in bow:
    for key,value in document.iteritems():
        if key not in feature_id_map:
            feature_id_map[key] = feature_id
            feature_id          = feature_id + 1

with open(output_file,'w') as f:
    for i in xrange(len(bow)):
        for key,value in bow[i].iteritems():
            f.write(str(document_id[i]) + " " + str(feature_id_map[key]) + " " + str(value)+"\n")
