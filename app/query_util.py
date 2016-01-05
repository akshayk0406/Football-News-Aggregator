import datetime
from db import select,insert
from util import *

def get_latest_news(cursor):
	day_limit	= 1
	hours_limit = 12
	start_time  = (datetime.datetime.utcnow() - datetime.timedelta(hours=hours_limit)).strftime("%Y-%m-%d %H:%M:%S")
	sql_query	= "select id,fid,source,href,title,image,created_date from football_news.news where created_date >= '" + start_time + "' order by created_date desc"

	records		= select(cursor,sql_query)
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

	return result

def get_recent_data(cursor):
	day_limit		= 1
	start_time  	= (datetime.datetime.utcnow() - datetime.timedelta(days=day_limit)).strftime("%Y-%m-%d %H:%M:%S")
	sql_query		= "select news_id,ipaddress from football_news.log where created_date >= '" + start_time + "' order by created_date desc,ipaddress asc,news_id asc"

	records 		= select(cursor,sql_query)
	result 			= []
	for record in records:
		result_obj	= {}
		result_obj['news_id'] 	= record[0]
		result_obj['ipaddress']	= record[1]
		result.append(result_obj)
	return result

def is_record_present(cursor,fid):

	sql_query 		= "select fid from football_news.news where fid = '" + fid + "'"
	records 		= select(cursor,sql_query)
	total_records 	= 0

	for record in records:
		total_records = total_records + 1

	return total_records > 0

def is_clusterting_present(cursor,cluster_id):

	sql_query		= "select cluster_id from football_news.clusters where cluster_id = '" + cluster_id + "'"
	records 		= select(cursor,sql_query)
	total_records	= 0

	for record in records:
		total_records	= total_records + 1

	return total_records > 0

def record_news(cursor,news_object):

	if is_record_present(cursor,news_object['id']):
		return

	news_object['title'] 	= clean(news_object['title'])
	sql_query 				= "insert into football_news.news(fid,source,href,title,image,created_date) values ('" + news_object['id'] + "',"
	sql_query				= sql_query + "'"+news_object['source'] + "',"
	sql_query				= sql_query + "'"+news_object['href'] +"','"+news_object['title']+"','"+news_object['image']+"',"
	sql_query				= sql_query + "'"+news_object['created_date']+"');"
	insert(cursor,sql_query)

def get_landing_page_data(cursor):

	answer 			= []
	sql_query 		= "select components from football_news.clusters order by created_date desc,score desc limit " + str(ARTICLE_LIMIT)
    cluster_records = select(cursor,sql_query)

    for record in cluster_records:
    	tokens 		= record[0].split(",")[:g_cluster_news_limit]
    	news_object = []

    	for token in tokens:
    		news_object.append(construct_news_from_id(cursor,token))

        modified_news_object = get_modifed_news_object(news_object)
        answer.append(modified_news_object)

    return answer

def construct_news_from_id(cursor,token):

	news_object 	= []
	sql_query		= "select id,fid,source,title,href,image from football_news.news where id in (" + str(token) + ")"
	records 		= select(cursor,sql_query)

	for record in records:
		news_object.append(get_news_object(record))

    return news_object

def get_recommended_items(cursor,ipaddress):
	sql_query   = "select components from football_news.recommendation where ipaddress ='"+str(ipaddress) + "'"
	return select(cursor,sql_query)

def push_log(cursor,news_id,ipaddress,ctime):

	sql_query   = "insert into football_news.log(news_id,ipaddress,created_date) values ("+str(news_id) +",'"+ipaddress+"','"+ ctime +"')"
    insert(cursor,sql_query)
