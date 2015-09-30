#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
import stackexchange
import MySQLdb
from settings import *

bot = telegram.Bot(token=token)
db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPassword, db=mysqlDBName, charset='utf8')
cursor = db.cursor()


from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        
    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def obtain_question(q):
    result = {'status': False}
    so = stackexchange.Site(stackexchange.StackOverflow)
    so.be_inclusive()
    so_qs = so.search(intitle=q, sort='votes')[:1]
    for so_q in so_qs:
        print('%8d %s %s' % (so_q.id, so_q.title, so_q.url))
        answers = so.answers(question_id=so_q.id, sort='votes')[:1]
        if answers:
            result = {
                'status': True,
                'questionUrl': so_q.url,
                'answer': strip_tags(answers[0].body)
            }

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
    if last_update_id:
        updates = bot.getUpdates(offset=last_update_id+1)
    else:
        updates = bot.getUpdates()
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
        if answer['status']:
            message = answer['answer']
        else:
            message = u'Ниче не нашёл :('

        try:
            bot.sendMessage(chat_id=upd.message.chat.id, text=message)
        except telegram.TelegramError:
            if answer['status']:
                msg = 'Слишком длинный ответ, ничерта не влезает, вот линк на вопрос - ' + answer['questionUrl']
            else:
                msg = 'Произошла хер знает какая ошибка, мож лимит запросов, может криворукий разработчик'
            bot.sendMessage(chat_id=upd.message.chat.id, text=msg)

    db.close()
    print 'OK!'


run_bot()