from query_util import *
from util import *
from db import get_db_connection
from util import *
import sys
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import *

output_file     = sys.argv[1]
conn            = get_db_connection()
cursor          = conn.cursor()
result		    = get_latest_news(cursor)
cursor.close()
conn.close()

stop            = stopwords.words('english')
stemmer         = PorterStemmer()
bow             = []
document_id     = []

for news_object in result:
    base_url = news_object['href']
    response = requests.get(base_url).text
    bow.append(Counter(cleanMe(news_object['source'],response,stop,stemmer)))
    document_id.append(int(news_object['id']))

feature_id      = 0
feature_id_map  = {}
for document in bow:
    for key,value in document.iteritems():
        if key not in feature_id_map:
            feature_id_map[key] = feature_id
            feature_id          = feature_id + 1

with open(output_file,'w') as f:
    for i in xrange(len(bow)):
        for key,value in bow[i].iteritems():
            f.write(str(document_id[i]) + " " + str(feature_id_map[key]) + " " + str(value)+"\n")
