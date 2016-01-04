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

