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

import xbmcplugin
import xbmcgui
import urllib
import re
import sys
import utils


def createBroadcasterList(params):
  module = params['module']
  baseurl = 'http://www.uitzendinggemist.nl'
  page = ""
  url = baseurl+'/omroepen/landelijk'
  page = utils.open_url(url)
  page = page.replace("\n","").replace("\t","")
  broadcasters = re.findall(r"<li.*?class=\"broadcaster knav\".*?<a.*?href=\"(.*?)\".*?class=\"broadcaster\".*?title=\"(.*?)\">.*?src=\"(.*?)\".*?</a>", page)
  for broadcaster in broadcasters:
    title = utils.htmlentitydecode(broadcaster[1].strip())
    url = broadcaster[0].strip()
    url = sys.argv[0]+"?module="+module+"&action=find_programs"+"&url=" + url
    thumb = "http:"+broadcaster[2].strip()
    utils.addDir(title, url, thumb) 
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def find_programs(params):
  baseurl = 'http://www.uitzendinggemist.nl/'
  url = urllib.unquote(params['url'])
  module = params['module']
  page = ""
  pagecount = 1
  while pagecount<15:
    url = baseurl + url + "?display_mode=list&order=name_asc&page=" + str(pagecount)
    page = utils.open_url(url)
    programs = re.findall(r"<h2><a.*?href=\"(.*?)\".*?class=\"series knav_link\".*?title=\"(.*?)\">.*?</a>.*?</h2>", page)
    if len(programs)==0:
      break
    for program in programs:
      title = utils.htmlentitydecode(program[1])
      programurl = program[0]
      programurl = sys.argv[0]+"?module="+module+"&action=find_episodes"+"&url=" + programurl
      thumb = ""
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
    page = utils.open_url(rssurl)    
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
        title = utils.htmlentitydecode(utils.getText(item.getElementsByTagName('title')[0].childNodes))
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
    createBroadcasterList(params)
