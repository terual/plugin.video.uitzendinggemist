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

xbmc       = sys.modules["__main__"].xbmc
xbmcplugin = sys.modules["__main__"].xbmcplugin
xbmcgui    = sys.modules["__main__"].xbmcgui
common     = sys.modules["__main__"].common

def search(params):
  import cgi
  baseurl = 'http://www.uitzendinggemist.nl'
  module = params['module']
  # open dialog to get search string
  kb = xbmc.Keyboard('', 'Zoek een programma', False)
  kb.doModal()
  if (kb.isConfirmed()):
    search = kb.getText()
  else:
    search = ""
  # loop trough max 10 pages of search results 5 results per page
  page = ""
  pagecount = 1
  while pagecount<15:
    url = baseurl+'/zoek/programmas?q=' + urllib.quote(search) + '&series_page=' + str(pagecount) + '&_pjax=true'
    request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
    if not request["status"] == 200:
      break
    page = request["content"]
    if len(page)<10:
      break
    page = page.replace("\n","").replace("\t","")
    programs = re.findall(r"<div.*?class=\"img\".*?href=\"(.*?)\".*?title=\"(.*?)\".*?data-images=\"(.*?)\".*?class=\"episodes-count\">(.*?)</div>.*?</div>", page)
    for program in programs:
      title = common.replaceHTMLCodes(program[1].strip())
      url = program[0].strip()
      url = sys.argv[0]+"?module="+module+"&action=find_episodes"+"&url=" + url
      thumb = program[2].strip().replace("&quot;","").replace("[","").replace("]","").replace("140x79.jpg","280x160.jpg")
      try:
        episodecount = [int(s) for s in program[3].split() if s.isdigit()][0]
      except:
        episodecount = 0
      if episodecount>0:
        utils.addDir(title, url, thumb)
    pagecount = pagecount+1
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def find_episodes(params):
  import xml.dom.minidom
  baseurl = 'http://www.uitzendinggemist.nl'
  url = urllib.unquote(params['url'])
  module = params['module']
  page = ""
  pagecount = 1
  while pagecount<10:
    rssurl = baseurl + url + '.rss?page=' + str(pagecount)
    request = common.fetchPage({"link": rssurl, "cookie": "site_cookie_consent=yes"})
    if not request["status"] == 200:
      break
    page = request["content"]  
    try:
      dom = xml.dom.minidom.parseString(page)
    except:
      page = page.replace("&","&amp;")
      dom = xml.dom.minidom.parseString(page)
    if len(dom.getElementsByTagName('item'))==0:
      break
    else:
      for item in dom.getElementsByTagName('item'):
        videourl = utils.getText(item.getElementsByTagName('link')[0].childNodes)
        videourl = urllib.quote_plus(videourl)
        videourl = sys.argv[0]+"?module="+module+"&action=find_video"+"&url="+videourl
        try:
          thumb = item.getElementsByTagName('media:thumbnail')[0].attributes['url'].value
        except:
          thumb = ""
        title = common.replaceHTMLCodes(utils.getText(item.getElementsByTagName('title')[0].childNodes))
        utils.addLink(title, videourl, thumb)
    pagecount = pagecount+1
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(params):
  url = params['url']
  url = urllib.unquote(url)
  resolved_url = utils.find_video(url)
  if resolved_url!="":
    li=xbmcgui.ListItem(path = resolved_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    return True
  else:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('Uitzending Gemist', 'Geen afspeelbaar formaat gevonden.')
    return False

def run(params):
  if 'action' in params:
    if params['action']=='find_video':
      play(params)
    elif params['action']=='find_episodes':
      find_episodes(params)
  else:
    search(params)
