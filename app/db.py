"""
Utility file to manage db connection
"""

from config import g_useProduction
import psycopg2

def get_db_connection():

	conn_string		= ''

	host_key 		= 'host'
	dbname_key 		= 'dbname'
	user_key		= 'user'
	password_key	= 'password'

	prod_host		= '127.0.0.1'
	prod_dbname		= 'news'
	prod_user		= 'don'
	prod_password 	= '$g3WE28%H3'

	local_host		= '127.0.0.1'
	local_dbname	= 'news'
	local_user		= 'akshaykulkarni'
	local_password	= ''


	if g_useProduction:
		conn_string = conn_string + host_key + "='" + prod_host + "' "
		conn_string	= conn_string + dbname_key + "='" + prod_dbname + "' "
		conn_string	= conn_string + user_key + "='" + prod_user + "' "
		conn_string	= conn_string + password_key + "='" + prod_password + "' "

	else:

		conn_string = conn_string + host_key + "='" + local_host + "' "
		conn_string	= conn_string + dbname_key + "='" + local_dbname + "' "
		conn_string	= conn_string + user_key + "='" + local_user + "' "
		conn_string	= conn_string + password_key + "='" + local_password + "' "

	conn = psycopg2.connect(conn_string)
	return conn

def select(cursor,sql_query):
	cursor.execute(sql_query)
	return cursor.fetchall()

def insert(cursor,sql_query):
	cursor.execute(sql_query)
	return
