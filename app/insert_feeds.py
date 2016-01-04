"""
File to write clustering to database
"""

import datetime
import sys
from db import get_db_connection
from util import md5_hash
from query_util import *

format              = "%Y-%m-%d %H:%M:%S"
conn                = get_db_connection()
cursor              = conn.cursor()
solution_file       = sys.argv[1]

with open(solution_file,'r') as f:
    for line in f:

        tokens          = line.split(" ")
        tokens          = tokens[:-1]
        score           = float(tokens[0])
        cluster_str     = ",".join([x for x in tokens[1:]])
        clustering_id   = md5_hash(cluster_str)

        if is_clusterting_present(cursor,clustering_id):
            continue

        if len(tokens[1:]) <= 2:
            continue

        ctime = datetime.datetime.strftime(datetime.datetime.utcnow(),format)
        sql_query = "insert into football_news.clusters(cluster_id,score,components,created_date) values ('"+ clustering_id + "',"+ str(score) +",'"+ cluster_str+"','"+ ctime +"')"
        insert(cursor,sql_query)
        conn.commit()

cursor.close()
conn.close()
