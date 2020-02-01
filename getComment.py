import requests
import emoji
from bs4 import BeautifulSoup
import urllib.parse
from sqlalchemy import and_
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def login(username, password):
    url = 'https://accounts.douban.com/j/mobile/login/basic'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony',
        'Origin': 'https://accounts.douban.com',
        'content-Type': 'application/x-www-form-urlencoded',
        'x-requested-with': 'XMLHttpRequest',
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'connection': 'keep-alive'
        , 'Host': 'accounts.douban.com'
    }
    data = {
        'ck': '',
        'name': '',
        'password': '',
        'remember': 'false',
        'ticket': ''
    }
    data['name'] = username
    data['password'] = password
    data = urllib.parse.urlencode(data)
    print(data)
    req = requests.post(url, headers=header, data=data, verify=False)
    cookies = requests.utils.dict_from_cookiejar(req.cookies)
    print(cookies)
    return cookies


def ini_mysql(password, base_name):
    Base = declarative_base()
    engine = create_engine('mysql+mysqlconnector://root:' + str(password) + '@localhost:3306/' + str(base_name))

    class Movie_Comment(Base):
        __tablename__ = 'movie_comment'
        index = Column(Integer)
        name = Column(Integer,primary_key=True)
        comment = Column(String(255))
        star = Column(Integer)

    return Movie_Comment, engine


def insert_mysql(Movie_Comment, engine, index, name, comment, star):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    new_comment = Movie_Comment(index=index, name=name, comment=comment, star=star)
    session.add(new_comment)
    session.commit()
    session.close()


def getcomment(cookies, movie_code):
    start = 0
    index = 1
    base_name = input("请输入数据库名：")
    base_password = input("请输入数据库密码：")


    Movie_Comment, engine=ini_mysql(base_password, base_name)
    while True:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }
        try:
            url = 'https://movie.douban.com/subject/' + str(movie_code) + '/comments?start=' + str(
                start) + '&limit=20&sort=new_score&status=P&comments_only=1'
            start += 20
            req = requests.get(url, cookies=cookies, headers=header)
            res = req.json()
            res = res['html']
            soup = BeautifulSoup(res, 'lxml')
            node = soup.select('.comment-item')
            for va in node:
                name = emoji.demojize(va.a.get('title'))
                star = va.select_one('.comment-info').select('span')[1].get('class')[0][-2]
                comment = emoji.demojize(va.select_one('.short').text)
                #print(name, star, comment,index)
                #print(index)
                index += 1
                insert_mysql(Movie_Comment, engine, index, name, comment, star)

        except Exception as  e:
            print(e)
            print('爬取了'+str(index)+'条记录')
            break


if __name__ == '__main__':
    douban_account=input("请输入豆瓣账号：")
    douban_password=input("请输入豆瓣密码：")
    movie_code=input("请输入电影代码：")
    cookies = login(douban_account,douban_password)
    getcomment(cookies,movie_code)

