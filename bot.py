#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram, stackexchange
import MySQLdb
from settings import *

bot = telegram.Bot(token=token)
db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPassword, db=mysqlDBName, charset='utf8')
cursor = db.cursor()


def obtain_question(q):
    result = False
    so = stackexchange.Site(stackexchange.StackOverflow)
    so_qs = so.search(intitle=q, sort='votes')[:1]
    for so_q in so_qs:
        print('%8d %s %s' % (so_q.id, so_q.title, so_q.url))
        answers = so.answers(question_id=so_q.id, sort='votes')[:1]
        if answers:
            result = answers[0].body

    return result


def run_bot():
    print 'Get last update id... '
    sql = """SELECT updateId FROM messages ORDER BY updateId DESC LIMIT 1"""
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            last_update_id = row[0]
        else:
            last_update_id = None
        print 'OK! Its ' + str(last_update_id)
    except MySQLdb.Error, e:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        last_update_id = None

    print 'Get telegram updates... '
    updates = bot.getUpdates(offset=last_update_id+1)
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

        answer = obtain_question(question)
        if answer:
            message = answer
        else:
            message = u'Ниче не нашёл :('

        bot.sendMessage(chat_id=upd.message.chat.id, text=message)

    db.close()
    print 'OK!'


run_bot()
