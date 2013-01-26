#/*
# *      Copyright (C) 2013 terual
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

def createABCList(params):
  module = params['module']
  for letter in [chr(x) for x in range(97, 97+26)]:
    title = letter.upper()
    url = sys.argv[0]+"?module="+module+"&action=find_programs"+"&letter=" + letter
    thumb = ""
    utils.addDir(title, url, thumb) 
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def find_programs(params):
  baseurl = 'http://www.uitzendinggemist.nl/programmas/'
  letter = urllib.unquote(params['letter'])
  module = params['module']
  page = ""
  pagecount = 1
  while pagecount<15:
    url = baseurl + letter + "?display_mode=images&_pjax=true&page=" + str(pagecount)
    request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
    if request["status"] == 200:
      page = request["content"]
      programs = re.findall(r"<a href=\"(.*?)\".*?class=\"series series-image\".*?title=\"(.*?)\">.*?data-images=\"(.*?)\".*?</a>", page)
      if len(programs)==0:
        break
      for program in programs:
        title = common.replaceHTMLCodes(program[1])
        programurl = program[0]
        programurl = sys.argv[0]+"?module="+module+"&action=find_episodes"+"&url=" + programurl
        thumb = utils.parseDataImages(program[2])
        utils.addDir(title, programurl, thumb)
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
    if request["status"] == 200:
      page = request["content"].encode('utf-8')
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
  if resolved_url!=None:
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
    elif params['action']=='find_programs':
      find_programs(params)
  else:
    createABCList(params)
