#!/usr/bin/env python

import telegram
import MySQLdb
from settings import *

bot = telegram.Bot(token=token)
db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPassword, db=mysqlDBName, charset='utf8')
cursor = db.cursor()

print 'Get last update id... '
sql = """SELECT updateId FROM messages ORDER BY updateId DESC LIMIT 1"""
try:
    cursor.execute(sql)
    row = cursor.fetchone()
    if row:
        LAST_UPDATE_ID = row[0]
    else:
        LAST_UPDATE_ID = None
    print 'OK! Its ' + str(LAST_UPDATE_ID)
except MySQLdb.Error, e:
    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
    LAST_UPDATE_ID = None

print 'Get telegram updates... '
updates = bot.getUpdates(offset=LAST_UPDATE_ID+1)
print 'OK! fetched ' + str(len(updates)) + ' update(s)! Obtain response... '

for upd in updates:
    question = upd.message.text
    sql = u"""INSERT INTO messages (updateId, chatId, userId, content) VALUES ({0}, {1}, {2}, '{3}')
          """.format(upd.update_id, upd.message.chat.id, upd.message.from_user.id, question)
    try:
        cursor.execute(sql)
        db.commit()
    except MySQLdb.Error, e:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])

db.close()
print 'OK!'
