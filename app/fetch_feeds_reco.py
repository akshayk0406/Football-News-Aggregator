"""
Constructing data-sets for offline recommendation
"""

from query_util import *
from util import *
from db import get_db_connection
from util import *
import sys

output_file			= sys.argv[1]
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
	norm_factor		= sqrt(len(news_id))
	for search_user,source_news_id in user_data.iteritems():
		if search_user == target_user:
			continue
		similarity	= compute_similarity(target_news_id,source_news_id)
		nearest_user.append((similarity,search_user))

	nearest_user.sort()
	nearest_user.reverse()
	nearest_user 		= nearest_user[:neighbors]
	required_articles	= []

	for user in nearest_user:
		for news_article in user_data[user]:
			if news_article not in target_news_id and news_article not in required_articles:
				required_articles.append(news_article)

	recommendations[target_user] = required_articles

with open(output_file,'w') as f:
	for user,articles in recommendations.iteritems():
		f.write(user+ " ")
		for news_id in articles:
			f.write(str(news_id) + " ")
		f.write("\n")

