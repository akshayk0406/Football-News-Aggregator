"""
Constructing data-sets for offline recommendation
"""

from config import g_reco_article_limit
from query_util import *
from util import *
from db import get_db_connection,insert
from util import *
import sys
import datetime

dt_format               = "%Y-%m-%d %H:%M:%S"
conn            	= get_db_connection()
cursor          	= conn.cursor()
result		    	= get_recent_data(cursor)
cursor.close()
conn.close()

user_data 			= {}
for user_activity in result:
        ipaddress		= user_activity['ipaddress']
	news_id			= user_activity['news_id']
	
	if ipaddress not in user_data:
		user_data[ipaddress]	= []

	user_data[ipaddress].append(news_id)

"""
Implementing collabrative engine
"""
recommendations		= {}
neighbors			= 10
recommend_news		= {}
for target_user,target_news_id in user_data.iteritems():
        total_news              = len(target_news_id) 
	norm_factor		= total_news ** 0.5
        nearest_user            = []
	for search_user,source_news_id in user_data.iteritems():
		if search_user == target_user:
			continue
		similarity	= compute_similarity(target_news_id,source_news_id)
		nearest_user.append((similarity,search_user))

	nearest_user.sort()
	nearest_user.reverse()
	nearest_user 		= nearest_user[:neighbors]
	required_articles	= []

	for similarity,user in nearest_user:
		for news_article in user_data[user]:
			if news_article not in target_news_id and news_article not in required_articles:
				required_articles.append(news_article)

	recommendations[target_user] = required_articles[:g_reco_article_limit]

conn            = get_db_connection()
cursor          = conn.cursor()

for user,articles in recommendations.iteritems():
    components  = ",".join([str(news) for news in articles])
    ctime       = datetime.datetime.strftime(datetime.datetime.utcnow(),dt_format)
    sql_query   = "insert into football_news.recommendation(ipaddress,components,created_date) values ('"+str(user)+"','"+str(components)+"','"+ctime+"')"
    insert(cursor,sql_query)
    conn.commit()
    
