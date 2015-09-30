#!/usr/lib/env python

import MySQLdb
from settings import *


db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPassword, db=mysqlDBName, charset='utf8')
cursor = db.cursor()

sql = """DROP TABLE IF EXISTS  messages;
      CREATE TABLE messages (
         id BIGINT(20) NOT NULL AUTO_INCREMENT,
         updateId BIGINT(20) NOT NULL,
         chatId BIGINT(20) NOT NULL,
         userId BIGINT(20) NOT NULL,
         content TEXT DEFAULT NULL,
         createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
         PRIMARY KEY (id)
         KEY userId (userId),
         KEY updateId (updateId)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

print 'Creating table `messages`... '
try:
    cursor.execute(sql)
    print 'OK!'
except MySQLdb.Error, e:
    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
