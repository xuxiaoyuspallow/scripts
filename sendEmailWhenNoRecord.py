"""
当mongodb数据库超过一段时间没有数据插入时，
将会给一些人发送邮件
"""
import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.utils import formataddr

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus

from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-s %(message)s',
                    # datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='sendEmail.log',
                    filemode='a')
##################################################################
TOUSER = []  #发送给的邮箱
DATABASES = []  #监控的数据库
TIME = 20*60    #当数据库没有新数据的最长时间，秒

my_sender=''    # 发送邮件的邮箱
my_pass = ''         #邮箱密码
SMTP_SERVRE = ''    # smtp服务器，ssl

MONGOHOSTS = []
MONGOCONFIG = {
    'port': 27017,
    'user': '',
    'pass': ''
}
###################################################################


def send_mail(text):
    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = formataddr(["developer", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['Subject'] = "something about xx happened"  # 邮件的主题，也可以说是标题

    server = smtplib.SMTP_SSL(SMTP_SERVRE, 465)  # 发件人邮箱中的SMTP服务器，端口是465
    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(my_sender, TOUSER, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接

def query_database(host):
    result = []
    uri = "mongodb://%s:%s@%s/%s" % (
        quote_plus(MONGOCONFIG['user']), quote_plus(MONGOCONFIG['pass']), host,'welv1')
    conn = MongoClient(uri)
    db = conn.welv1
    for database in DATABASES:
        table = db[database]
        s = table.find({'postTimestamp':{'$lte':time.time() * 1000,'$gte':(time.time() - TIME)*1000}},sort=[('postTimestamp',-1)])
        try:
            logging.debug(s.next())
        except StopIteration:
            result.append(database)
    return result

def main():
    while True:
        for host in MONGOHOSTS:
            text = '以下数据库已经有{}秒没更新了:'.format(TIME)
            result = query_database(host)
            if result:
                for i in result:
                    logging.info('以下数据库没数据,host:{0}，name:{1}'.format(host,i))
                    text += i
                    text += '、'
                send_mail(text)
        time.sleep(TIME)


if __name__ == '__main__':
    main()