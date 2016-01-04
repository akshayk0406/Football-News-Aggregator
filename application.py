import os
from flask import Flask, render_template, send_from_directory, request,make_response
import json
import psycopg2
from app.db import get_db_connection,select
from app.config import g_post_hash_key
from app.util import md5_hash
import datetime

# initialization
app = Flask(__name__)

app.config.update(
    DEBUG = False,
)

ARTICLE_LIMIT   = 12
NEWS_LIMIT      = 4


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.route("/",methods=["GET"])
def index():
    conn            = get_db_connection()
    cursor          = conn.cursor()
    sql_query 		= "select components from football_news.clusters order by created_date,score desc limit " + str(ARTICLE_LIMIT)
    cluster_records = select(cursor,sql_query)

    json_object		= {'status':'OK','result':[]}
    for record in cluster_records:
    	news_object     = []
    	tokens 		= record[0].split(",")[:NEWS_LIMIT]
    	for token in tokens:
	    	sql_query	= "select id,fid,source,title,href,image from football_news.news where id in (" + str(token) + ")"
	    	records 	= select(cursor,sql_query)

	    	for record in records:
	    		news_record = {}
	    		news_record['source']   = record[2]
	    		news_record['fid'] 	= record[1]
	    		news_record['title']    = record[3]
	    		news_record['href']	= record[4]
	    		news_record['image']    = record[5]
	    		
                if news_record['source'] == 'guardian' and '' != news_record['image']:
                    news_object.insert(0,news_record)
                else:
                    news_object.append(news_record)

        modified_news_object = {}
        if len(news_object) > 0:
        	modified_news_object['source'] = news_object[0]['source']
        	modified_news_object['title'] = news_object[0]['title']
        	modified_news_object['href'] = news_object[0]['href']
        	modified_news_object['image'] = news_object[0]['image']
        	modified_news_object['other'] = []

        	for i in range(1,len(news_object)):
        		modified_news_object['other'].append({'href':news_object[i]['href'],'title':news_object[i]['title']})

    	json_object['result'].append(modified_news_object)

    cursor.close()
    conn.close()

    return make_response(json.dumps(json_object))

@app.route("/log",methods=["POST"])
def log_views():
    news_id     = request.form['id'] if 'id' in form else 0
    client_hash = request.form['hash'] if 'hash' in form else ''
    server_hash = md5_hash(str(news_id)+g_post_hash_key)

    if client_hash != server_hash:
        return make_response(json.dumps({'status':'FAIL','message':'Hash MisMatch'}))

    conn            = get_db_connection()
    cursor          = conn.cursor()

    format      = "%Y-%m-%d %H:%M:%S"
    ipaddress   = request.remote_addr
    ctime       = datetime.datetime.strftime(datetime.datetime.utcnow(),format)
    sql_query   = "insert into football_news.log(news_id,ipaddress,created_date) values ("+str(news_id) +",'"+ipaddress+"','"+ ctime +"')"
    insert(cursor,sql_query)

    cursor.close()
    conn.close()

    return make_response(json.dumps({'status':'OK'})
