#/*
# *      Copyright (C) 2012 Syl
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import urllib
import re
import sys
import utils

xbmcplugin = sys.modules["__main__"].xbmcplugin
xbmcgui    = sys.modules["__main__"].xbmcgui
common     = sys.modules["__main__"].common
language   = sys.modules["__main__"].language

def createDayList(params):
  import datetime
  import locale
  module = params['module']
  locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
  now = datetime.datetime.now()
  title = now.strftime("%A, %d %B %Y (vandaag)")
  url = now.strftime("%Y-%m-%d")
  dow = now.strftime("%w")
  url = sys.argv[0]+"?module="+module+"&action=find_episodes&dow="+dow+"&date="+url
  thumb = ""
  utils.addDir(title, url, thumb)
  for count in [1,2,3,4,5,6]:
    minus = datetime.timedelta(days=count)
    past = now - minus
    title = past.strftime("%A, %d %B %Y")
    url = past.strftime("%Y-%m-%d")
    dow = past.strftime("%w")
    url = sys.argv[0]+"?module="+module+"&action=find_episodes&dow="+dow+"&date="+url
    thumb = ""
    utils.addDir(title, url, thumb) 
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def find_episodes(params):
  baseurl = 'http://www.uitzendinggemist.nl/'
  date = urllib.unquote(params['date'])
  module = params['module']
  days = ["zo","ma","di","wo","do","vr","za"]
  dow = days[int(params['dow'])]
  page = ""
  url = baseurl + "/gids/" + date
  request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
  if request["status"] == 200:
    page = request["content"].encode('utf-8')
    episodes = re.findall(r"<li.*?class=\"episode active\".*?data-path=\"(.*?)\".*?>", page)
    episodelist = []
    unique=[]
    for episode in episodes:
      episodeinfourl = baseurl + episode
      request = common.fetchPage({"link": episodeinfourl, "cookie": "site_cookie_consent=yes"})
      if request["status"] == 200:
        episodeinfo = request["content"].encode('utf-8')
        episodeinfo=episodeinfo.replace("\n","")
        info1 = re.findall(r"<h2.*?href=\"(.*?)\".*?class=\"episode active \".*?title=\"(.*?)\".*?h2>", episodeinfo)
        info2 = re.findall(r"<tr>.*?<th>datum</th>.*?<td>(.*?)</td>.*?</tr>", episodeinfo)
        try:
          date = info2[0]
          title = common.replaceHTMLCodes(info1[0][1])
          date = date.replace(title,"").replace("(","").replace(")","") 
          videourl = info1[0][0]
          videourl = sys.argv[0]+"?module="+module+"&action=find_video"+"&url=" + baseurl+videourl
          thumb = ""
          if not info1[0][0] in unique:
            if dow in date:
              episodelist.append([date,title,videourl,thumb])
              unique.append(info1[0][0])
        except:
          pass
    episodelist.sort(reverse=True)
    for episode in episodelist:
      utils.addLink("%s, %s" % (episode[0],episode[1]), episode[2], episode[3])
  xbmcplugin.endOfDirectory(int(sys.argv[1]))


def play(params):
  url = params['url']
  url = urllib.unquote(url)
  resolved_url = utils.find_video(url)
  if resolved_url!=None:
    li=xbmcgui.ListItem(path = resolved_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    return True
  else:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok(language(30201), language(30202))
    return False

def run(params):
  if 'action' in params:
    if params['action']=='find_video':
      play(params)
    elif params['action']=='find_episodes':
      find_episodes(params)
  else:
    createDayList(params)
