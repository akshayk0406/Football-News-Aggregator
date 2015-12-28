import psycopg2
import pytz
import datetime
import hashlib
import feedparser
import requests
from bs4 import BeautifulSoup

HASH_KEY			= "D#5@BDW!swr7%"
football_sources	= { 'sky':'http://www.skysports.com/rss/0,20514,11095,00.xml',
						'bbc':'http://feeds.bbci.co.uk/sport/0/football/rss.xml',
						'dailymail':'http://www.dailymail.co.uk/sport/football/index.rss',
						'espn':'http://www.espn.co.uk/rss/sport/story/feeds/0.xml?sport=3;type=2',
						'guardian':'http://feeds.theguardian.com/theguardian/football/rss'}

def generate_articleId(source,document_id):
	m = hashlib.md5()
	m.update(source+ HASH_KEY + document_id)
	return m.hexdigest()

def get_image_from_source(base_url):
	
	result = ""
	response = requests.get(base_url).text
	parsed_html = BeautifulSoup(response,'html.parser')
	image_tags	= parsed_html.find('img')

	if 'class' in image_tags and 'responsive-img' in image_tags['class']:
		result = image_tags['src']
	return result

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

def change_time_zone(ctime,zone):

	tzone = pytz.timezone(zone)
	format = "%Y-%m-%d %H:%M:%S"
	date = datetime.datetime.strptime(ctime,format)
	date_zone = tzone.localize(date,is_dst=True)
	return date_zone.astimezone(pytz.utc).strftime(format)	

def getMonth(month_name):
	month_name_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','June':'06',
						'July':'07','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
	if month_name in month_name_dict:
		return month_name_dict[month_name]
	return 0

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

def clean(token):
	token = BeautifulSoup(token,'html.parser').text
	token = token.replace('"','')
	token = token.replace("'","")
	return token

def is_record_present(cursor,fid):

	sql_query = "select fid from football_news.news where fid = '" + fid + "'"
	cursor.execute(sql_query)

	records = cursor.fetchall()

	total_records = 0
	for record in records:
		total_records = total_records + 1

	return total_records > 0

def record_news(cursor,news_object):

	if is_record_present(cursor,news_object['id']):
		return

	news_object['title'] 	= clean(news_object['title'])
	sql_query 	= "insert into football_news.news(fid,source,href,title,image,created_date) values ('" + news_object['id'] + "',"
	sql_query	= sql_query + "'"+news_object['source'] + "',"
	sql_query	= sql_query + "'"+news_object['href'] +"','"+news_object['title']+"','"+news_object['image']+"',"
	sql_query	= sql_query + "'"+news_object['created_date']+"');"

	cursor.execute(sql_query)

conn_string = "host='localhost' dbname='news' user='akshaykulkarni' password=''"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

news = []
for k,v in football_sources.items():
	feed = feedparser.parse( v )
	if 'entries' in feed:
		for record in feed['entries']:

			if 'id' not in record:
				record['id'] = record['link']

			news_object					=	{}
			news_object['id'] 			= generate_articleId(k,record['id'])
			news_object['href']			= record['link']
			news_object['title']		= record['title']
			news_object['created_date']	= getDateTime(record['published'])
			news_object['source']		= k
			news_object['image']		= extract_image(record,k)
			news.append(news_object)

for news_item in news:
	record_news(cursor,news_item)
conn.commit()