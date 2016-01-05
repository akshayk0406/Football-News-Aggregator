import os
from flask import Flask, render_template, send_from_directory, request,make_response
import json
import psycopg2
from app.db import get_db_connection,select,insert
from app.config import g_post_hash_key,g_cluster_news_limit,g_dtformat
from app.util import md5_hash,get_news_object
from app.query_util import get_landing_page_data,push_log,construct_news_from_id,get_recommended_items
import datetime

# initialization
app = Flask(__name__)

app.config.update(
    DEBUG = False,
)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.route("/",methods=["GET"])
def index():

    json_object             = {'status':'OK','result':[]}
    conn                    = get_db_connection()
    cursor                  = conn.cursor()
    json_object['result']   = get_landing_page_data(cursor)

    cursor.close()
    conn.close()

    return make_response(json.dumps(json_object))

@app.route("/log",methods=["POST"])
def log_views():
    news_id     = request.form['id'] if 'id' in request.form else 0
    client_hash = request.form['hash'] if 'hash' in request.form else ''
    server_hash = md5_hash(str(news_id)+g_post_hash_key)

    if client_hash != server_hash:
        return make_response(json.dumps({'status':'FAIL','message':'Hash MisMatch'}))

    conn        = get_db_connection()
    cursor      = conn.cursor()
    push_log(cursor,news_id,request.remote_addr,datetime.datetime.strftime(datetime.datetime.utcnow(),g_dtformat))
    conn.commit()
    cursor.close()
    conn.close()

    return make_response(json.dumps({'status':'OK'}))

@app.route("/reco",methods=["GET"])
def get_reco():
    
    response    = {'status':'FAIL','message':'NO_RECOMMENDATION','result':[]}
    ipaddress   = request.remote_addr
    if '' == ipaddress:
        return make_response(json.dumps(response))

    conn        = get_db_connection()
    cursor      = conn.cursor()
    
    records     = get_recommended_items(cursor,ipaddress) 
    reco_news   = ""

    for record in records:
        reco_news    = record[0]

    if 0 == len(reco_news.split(",")):
        cursor.close()
        conn.close()
        return make_response(json.dumps(response))

    response            = {'status':'OK','result':[]}
    
    reco_news_tokens    = reco_news.split(",")
    for reco_news in reco_news_tokens:
        news_object             = construct_news_from_id(cursor,reco_news)
        news_object['other']    = []
        response['result'].append(news_object)

    if 0 == len(response['result']):
        response['result']  = get_landing_page_data(cursor)
        response['result'].reverse()

    cursor.close()
    conn.close()

    return make_response(json.dumps(response))

if __name__ == "__main__":
    app.run()

