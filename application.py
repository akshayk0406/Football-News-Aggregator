import os
from flask import Flask, render_template, send_from_directory, request,make_response
import json
import psycopg2

# initialization
app = Flask(__name__)

app.config.update(
    DEBUG = False,
)

ARTICLE_LIMIT = 12
NEWS_LIMIT = 4
conn_string = "host='127.0.0.1' dbname='news' user='don' password='$g3WE28%H3'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.route("/")
def index():
    sql_query 		= "select cluster_id from football_news.clusters order by created_date,score desc limit " + str(ARTICLE_LIMIT)
    cursor.execute(sql_query)
    cluster_records = cursor.fetchall()

    json_object		= {'status':'OK','result':[]}
    for record in cluster_records:
    	news_object = []
    	tokens 		= record[0].split(",")[:NEWS_LIMIT]
    	for token in tokens:
	    	sql_query	= "select id,fid,source,title,href,image from football_news.news where id in (" + str(token) + ")"
	    	cursor.execute(sql_query)
	    	records 	= cursor.fetchall()

	    	for record in records:
	    		news_record = {}
                news_record['source']   = record[2]
	    		news_record['fid'] 	= record[1]
	    		news_record['title']= record[3]
	    		news_record['href']	= record[4]
	    		news_record['image']= record[5]
	    		
                if news_record['source'] == 'guardian' and '' != news_record['image']:
                    news_object.insert(0,news_record)
                else:
                    news_object.append(news_record)

        modified_news_object = {}
        if len(news_object) > 0:
        	modified_news_object['source'] = news_object[0]['source']
        	modified_news_object['title'] = news_object[0]['source']
        	modified_news_object['href'] = news_object[0]['source']
        	modified_news_object['image'] = news_object[0]['source']
        	modified_news_object['other'] = []

        	for i in range(1,len(news_object)):
        		modified_news_object['other'].append({'href':news_object[i]['href'],'title':news_object[i]['title']})

    	json_object['result'].append(modified_news_object)

    return make_response(json.dumps(json_object))
# launch
if __name__ == "__main__":
    app.run()

