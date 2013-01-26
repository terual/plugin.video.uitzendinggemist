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

def log(string):
  print "uitzendinggemist : " + str(string)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def addLink(title, url, thumb):
  import xbmcgui
  import xbmcplugin
  import sys
  liz = xbmcgui.ListItem(title, thumbnailImage=thumb)
  liz.setProperty("IsPlayable","true")
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=False)

def addDir(title, url,thumb):
  import xbmcgui
  import xbmcplugin
  import sys
  liz = xbmcgui.ListItem(title, thumbnailImage=thumb)
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=True)

def open_url(url):
  import urllib
  import urllib2
  import time
  count = 1
  retrys = 5
  while True:
    try:
      page = urllib2.urlopen(url)
      return page.read()
      break
    except:
      time.sleep(1)
      if count==retrys:
        return "<none />"
        break
      count = count + 1
  
def htmlentitydecode(s):
  import re
  from htmlentitydefs import name2codepoint
  return re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

def find_video(url):
  import xml.dom.minidom
  import re
  import base64
  import hashlib
  try:
    page = open_url(url)
    episode_id = re.findall(r'.*?episodeID=(.*?)&.*?',page)[0]
    url = "http://pi.omroep.nl/info/security/"
    page = open_url(url)
    dom = xml.dom.minidom.parseString(page)
    key = getText(dom.getElementsByTagName('key')[0].childNodes)
    key = base64.b64decode(key)
    key = key.split("|")
    md5hash = "%s|%s" % (episode_id,key[1])
    md5hash = hashlib.md5(md5hash.upper()).hexdigest().upper()
    url = "http://pi.omroep.nl/info/stream/aflevering/%s/%s" % (episode_id,md5hash)
    page = open_url(url)
    dom = xml.dom.minidom.parseString(page)
    streamurl = {}
    for stream in dom.getElementsByTagName('stream'):
      if (stream.attributes['compressie_formaat'].value=="mov" and stream.attributes['compressie_kwaliteit'].value=="bb"):
        streamurl[1]=getText(stream.getElementsByTagName('streamurl')[0].childNodes).strip()
      if (stream.attributes['compressie_formaat'].value=="mov" and stream.attributes['compressie_kwaliteit'].value=="std"):
        streamurl[0]=getText(stream.getElementsByTagName('streamurl')[0].childNodes).strip()
      if (stream.attributes['compressie_formaat'].value=="mov" and stream.attributes['compressie_kwaliteit'].value=="sb"):
        streamurl[2]=getText(stream.getElementsByTagName('streamurl')[0].childNodes).strip()
    for key in [0,1,2]:
      if streamurl.has_key(key):
        return streamurl[key]
        break
  except:
    return None
