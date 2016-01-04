"""
Gets Response from feeds and records the feed meta-data in database
"""

import feedparser
from db import get_db_connection
from query_util import *
from util import *
from config import g_unwanted_key_words

football_sources	= { 'sky':'http://www.skysports.com/rss/0,20514,11095,00.xml',
						'bbc':'http://feeds.bbci.co.uk/sport/0/football/rss.xml',
						'dailymail':'http://www.dailymail.co.uk/sport/football/index.rss',
						'espn':'http://www.espn.co.uk/rss/sport/story/feeds/0.xml?sport=3;type=2',
						'guardian':'http://feeds.theguardian.com/theguardian/football/rss'}

conn   				= get_db_connection()
cursor 				= conn.cursor()
news 				= []

for k,v in football_sources.items():
	feed = feedparser.parse( v )
	if 'entries' in feed:
		for record in feed['entries']:
                        
                        should_process  = True
			for unwanted_key_words in g_unwanted_key_words:
				if record['title'].lower().find(unwanted_key_words) >= 0:
                                        should_process = False
                    
                        if not should_process:
                            continue

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

cursor.close()
conn.close()
