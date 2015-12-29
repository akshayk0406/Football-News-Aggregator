import psycopg2
import datetime
import sys

format = "%Y-%m-%d %H:%M:%S"
conn_string = "host='localhost' dbname='news' user='akshaykulkarni' password=''"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

solution_file = sys.argv[1]
with open(solution_file,'r') as f:
    for line in f:

        tokens  = line.split(" ")
        tokens  = tokens[:-1]
        score   = float(tokens[0])
        cluster_str = ",".join([x for x in tokens[1:]])

        if len(tokens[1:]) <= 2:
            continue

        ctime = datetime.datetime.strftime(datetime.datetime.utcnow(),format)
        sql_query = "insert into football_news.clusters(cluster_id,score,created_date) values ('"+ cluster_str + "',"+ str(score) +",'"+ ctime +"')"
        cursor.execute(sql_query)
        conn.commit()

