#!/usr/bin/env python
#-*-coding:utf-8-*-

import sys, os
import urllib2,urllib
import re
import threading
import os
import sys
import datetime

abspath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abspath)
os.chdir(abspath)

class Kugou5SingSongDownloader:
    ''' 说明：下载 5Sing 某个歌手某个类型的全部音乐
        规则一：http://5sing.kugou.com/<主播用户ID>/<歌曲类型>/1.html
        规则二：http://5sing.kugou.com/m/detail/<歌曲类型>-<歌曲ID>-1.html
    '''

    _songtype = None    # 歌曲类型：yc（原唱）, fc（翻唱）, bz（伴奏）
    _userid = None      # 主播用户ID
    totalpages = None   # 主播 _songtype 类型歌曲的总页数

    def __init__(self, songtype=None, userid=None):
        self._songtype = songtype
        self._userid = userid

        pagepattern = re.compile(r'<a class="noFlush_load_link" href="\/%s\/%s\/(\d+).html">尾页<\/a>' % (self._userid, self._songtype))
        page = urllib2.urlopen('http://5sing.kugou.com/%s/%s/1.html' % (self._userid, self._songtype)).read()
        items = pagepattern.findall(page)
        self.totalpages = int(items[0] if items else 1)

    def dlitem(self, musicname, url):
        print ('.')
        fname = '%s.mp3' % musicname
        urllib.urlretrieve(url, os.path.join(abspath, fname))

    def dlpage(self, pageindex):
        pattern = re.compile(r'<span id="song-%s-(\d+)" class="tips_gray">' % (self._songtype))
        page = urllib2.urlopen('http://5sing.kugou.com/%s/%s/%s.html' % (self._userid, self._songtype, pageindex)).read()
        items = pattern.findall(page)

        tasks = []
        for songid in items:
            patterntarget = re.compile(r'<audio src="(.*)" preload="none"')
            patterntargettitle = re.compile(r'<h3 class="m_title">(.*)</h3>')
            pagetarget = urllib2.urlopen('http://5sing.kugou.com/m/detail/%s-%s-1.html' % (self._songtype, songid)).read()
            itemstarget = patterntarget.findall(pagetarget)
            itemstargettitle = patterntargettitle.findall(pagetarget)
            t = threading.Thread(target=self.dlitem, args=(itemstargettitle[0], itemstarget[0]))
            tasks.append(t)
        for task in tasks:
            task.start()
        for task in tasks:
            task.join(300)
        return 0

def main():
    argslen = len(sys.argv)

    if argslen < 3:
        print "Usage: Kugou5SingSongDownloader.py <UserID> <UserSongtype>"
        print "       UserID - 5Sing 歌手的用户ID，在其主页能看到"
        print "       UserSongtype - 歌曲类型：yc（原唱）, fc（翻唱）, bz（伴奏）"
        print ""
        return

    dl = Kugou5SingSongDownloader(songtype=sys.argv[2], userid=sys.argv[1])
    for page in range(0, dl.totalpages):
        dl.dlpage(page + 1)
    print "done"

if __name__ == "__main__":
    main()
