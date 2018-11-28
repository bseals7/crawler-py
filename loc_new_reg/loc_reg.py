#-*- coding=utf-8 -*-
import requests
import time
import datetime
import re
import os
import pymysql
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
logfile =  'newreg.log'
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

def log(msg):
    print(msg)
    logger.info(msg)


db=pymysql.connect('127.0.0.1','mysql_user','mysql_passwd','mysql_db',charset='utf8mb4')
cur=db.cursor()
db.ping()
try:
    sql="""
    create table if not exists loc_reg_relation(
    uid bigint
    ,username varchar(64)
    ,regtime varchar(64)
    ,puid bigint
    ,pusername varchar(64)
    );
    """
    cur.execute(sql)
    db.commit()
except Exception as e:
    print(e)
    sys.exit(0)

home='https://www.hostloc.com'
forum_home=home+'/forum.php?mod=forumdisplay&fid=45&orderby=dateline&filter=author&orderby=dateline&page={}'
login_url=home+'/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'

login_data={
        'fastloginfield':'username'
        ,'username':''
        ,'cookietime':'2592000'
        ,'password':''
        ,'quickforward':'yes'
        ,'handlekey':'ls'
    }

headers={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    ,'Accept-Encoding':'gzip, deflate, sdch'
    ,'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
    ,'Host':'www.hostloc.com'
    ,'Referer':'https://www.hostloc.com/forum.php'
    ,'Upgrade-Insecure-Requests':'1'
    ,'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

class HostLoc():
    def __init__(self):
        self.session=requests.Session()
        self.session.headers=headers


    def login(self):
        self.session.post(login_url,data=login_data,verify=False)

    def isLogin(self):
        url='https://www.hostloc.com/home.php?mod=spacecp'
        html=self.session.get(url).text
        UserName=re.findall(self.username,html)
        if len(UserName)==0:
            return False
        else:
            return True

    def GetContent(self,url):
        r=self.session.get(url)
        if len(re.findall('document.cookie=".*?";',r.text))>0:
            rcookies=re.findall('document.cookie="(.*?)";',r.text)[0]
            cookies={}
            for kv in rcookies.split(';'):
                k,v=kv.strip().split('=',1)
                cookies[k]=v
            self.session.cookies.set(**cookies)
        if len(re.findall('location.href="(.*?)";',r.text))>0:
            redirect_url=re.findall('location.href="(.*?)";',r.text)[0]
            if not redirect_url.startswith('https://'):
                redirect_url=home+redirect_url
            r=self.session.get(redirect_url)
        return r


    def get_hidden_value(self,url,keyname):
        r=self.session.get(url)
        cont=r.text
        value=re.findall('<input type="hidden" name="{}" value="(.*?)" />'.format(keyname),cont)[0]
        return value

    def GetNewUser(self):
        r=self.GetContent(home)
        space,username=re.findall(u'</span>欢迎新会员: <em><a href="(space-username-.*?\.html)" target="_blank" class="xi2">(.*?)</a></em></p',r.text)[0]
        space_url=home+'/'+space
        if not self.exists(username):
            uid,puid,pusername,regtime=self.GetUserInfo(space_url)
            log('get new register user:{},register time:{};invited by {}'.format(uid,regtime,pusername))
            sql='insert into loc_reg_relation(`uid`,`username`,`regtime`,`puid`,`pusername`) values(%s,%s,%s,%s,%s)'
            cur.execute(sql,(uid,username,regtime,puid,pusername))
            db.commit()

    def exists(self,username):
        sql="select count(1) from loc_reg_relation where `username`=%s;"
        cur.execute(sql,(username,))
        num=int(cur.fetchone()[0])
        return num>0

    def GetUserInfo(self,space_url):
        r=self.GetContent(space_url)
        uid=re.findall('<a id="domainurl" href="https://www.hostloc.com/\?(\d+)"',r.text)[0]
        try:
            f_c=re.findall('<div id="friend_content" class="dxb_bc">[\w\W]*?</div>',r.text)[0]
            puid,pusername=re.findall('<a href="space-uid-(\d+)\.html" target="_blank">(.*?)</a>',f_c)[0]
        except:
            puid,pusername=0,'已删除好友'
        profile_url='https://www.hostloc.com/home.php?mod=space&uid={}&do=profile'.format(uid)
        r3=self.GetContent(profile_url)
        regtime=re.findall(u'<em>注册时间</em>([\d\- :]*?)</li>',r3.text)[0]
        return uid,puid,pusername,regtime

    def UpdateHistory(self):
        sql="select uid from loc_reg_relation;"
        cur.execute(sql)
        dats=cur.fetchall()
        for u in dats:
            uid=u[0]
            print('update user info {}'.format(uid))
            space_url='https://www.hostloc.com/space-uid-{}.html'.format(uid)
            uid,puid,pusername,regtime=self.GetUserInfo(space_url)
            sql='update loc_reg_relation set puid=%s,pusername=%s where uid=%s'
            cur.execute(sql,(puid,pusername,uid))
            db.commit()



if __name__=="__main__":
    loc=HostLoc()
    while 1:
        log(u'getting new register user at {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S')))
        loc.GetNewUser()
        time.sleep(10)
