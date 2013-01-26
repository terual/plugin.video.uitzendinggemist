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
language   = sys.modules["__main__"].language

def createPeriodsList(params):
  module = params['module']
  periods = ['vandaag', 'gisteren', 'week', 'maand', 'alles']
  periodName = [language(30301), language(30302), language(30303), language(30304), language(30305)]
  for i in range(len(periods)): #XXX
    title = periodName[i]
    url = sys.argv[0]+"?module="+module+"&action=find_episodes"+"&period=" + periods[i]
    thumb = ""
    utils.addDir(title, url, thumb) 
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def find_episodes(params):
  import xml.dom.minidom
  baseurl = 'http://www.uitzendinggemist.nl/top50/'
  period = params['period']
  module = params['module']
  
  url = baseurl + period
  request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
  if request["status"] == 200:
    page = request["content"].encode('utf-8')
    page = common.parseDOM(page, 'tbody')
    episodes = common.parseDOM(page, 'tr')
    for i, episode in enumerate(episodes):
      title = common.parseDOM(episode, 'h2')
      subtitle = common.parseDOM(episode, 'h3')
      title = "%i. %s, %s" % (i+1, common.parseDOM(subtitle, 'a', ret='title')[0], common.parseDOM(title, 'a', ret='title')[0])
      videourl = "http://www.uitzendinggemist.nl%s" % common.parseDOM(episode, 'a', attrs = { 'class': 'episode active episode-image' }, ret = 'href')[0]
      videourl = urllib.quote_plus(videourl)
      videourl = sys.argv[0]+"?module="+module+"&action=find_video"+"&url="+videourl
      thumb = utils.parseDataImages(common.parseDOM(episode, 'img', attrs = { 'class': 'thumbnail' }, ret = 'data-images')[0])
      utils.addLink(title, videourl, thumb)

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
    createPeriodsList(params)
