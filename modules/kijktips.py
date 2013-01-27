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

def createSuggestionsList(params):
  module = params['module']
  url = 'http://www.uitzendinggemist.nl/kijktips'
  request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
  if request["status"] == 200:
    page = request["content"].encode('utf-8')
    episodes = common.parseDOM(page, 'div', attrs = { 'class': 'kijktip' })
    for episode in episodes:
      title = common.parseDOM(episode, 'h3')
      videourl = "http://www.uitzendinggemist.nl%s" % common.parseDOM(title, 'a', ret = 'href')[0]
      title = common.parseDOM(title, 'a')[0]
      subtitle = common.parseDOM(episode, 'h2')
      subtitle = common.parseDOM(subtitle, 'a')[0]
      plot = common.parseDOM(episode, 'p')[0]
      title = "%s - %s" % (title, subtitle)
      videourl = urllib.quote_plus(videourl)
      videourl = sys.argv[0]+"?module="+module+"&action=find_video"+"&url="+videourl
      thumb = utils.parseDataImages(common.parseDOM(episode, 'img', attrs = { 'class': 'thumbnail' }, ret = 'data-images')[0])
      utils.addLink(title, videourl, thumb, info={'plot': plot})
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
  else:
    createSuggestionsList(params)
