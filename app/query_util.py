
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

def is_record_present(cursor,fid):

	sql_query 		= "select fid from football_news.news where fid = '" + fid + "'"
	records 		= select(cursor,sql_query)
	total_records 	= 0

	for record in records:
		total_records = total_records + 1

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
