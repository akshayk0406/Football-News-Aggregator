import sys
import os

commands =  ["/var/www/Football-News-Aggregator/env/bin/python /var/www/Football-News-Aggregator/app/getFeed.py",
"/var/www/Football-News-Aggregator/env/bin/python /var/www/Football-News-Aggregator/app/pull_feeds.py /var/www/Football-News-Aggregator/data/articles.txt",
"/var/www/Football-News-Aggregator/worker/a.out /var/www/Football-News-Aggregator/data/articles.txt",
"/var/www/Football-News-Aggregator/env/bin/python /var/www/Football-News-Aggregator/app/insert_feeds.py /var/www/Football-News-Aggregator/data/clustering_solution.txt"]

for cmd in commands:
    print "Executing " + cmd
    os.system(cmd)
