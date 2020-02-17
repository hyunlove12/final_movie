import pymysql


def conn():
    conn = pymysql.connect(host='localhost', user='webdb', password='webdb', db='webdb', charset='utf8')
    return conn