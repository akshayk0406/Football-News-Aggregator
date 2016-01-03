"""
File to write clustering to database
"""

import datetime
import sys
from db import get_db_connection

format              = "%Y-%m-%d %H:%M:%S"
conn                = get_db_connection()
cursor              = conn.cursor()
solution_file       = sys.argv[1]

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
        insert(cursor,sql_query)
        conn.commit()

cursor.close()
conn.close()
