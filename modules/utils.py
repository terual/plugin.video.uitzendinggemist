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

import sys
common     = sys.modules["__main__"].common

streamquality = { 0: "std",
                  1: "bb",
                  2: "sb" }

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def parseDataImages(data, resized=False):
  import re
  import simplejson as json
  try:
    im = json.loads(common.replaceHTMLCodes(data))
  except:
    return ""
  if len(im) > 0:
    if resized==False:
      mobj = re.search("http://mediadb.omroep.nl/assets/(\d*?)/(\d*?)/(\d*?)/(.*?).jpg", im[0])
      if mobj:
        return "http://mediadb.omroep.nl/assets/%s/%s/%s.jpg" % (mobj.group(1),mobj.group(2),mobj.group(3))
    else:
      return im[0]
  return ""

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

def get_security_code():
  import base64
  import xml.dom.minidom
  common.log("", 5)
  url = "http://pi.omroep.nl/info/security/"
  request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
  if request["status"] == 200:
    page = request["content"].encode('utf-8')
    dom = xml.dom.minidom.parseString(page)
    key = getText(dom.getElementsByTagName('key')[0].childNodes)
    key = base64.b64decode(key)
    key = key.split("|")
    return key[1]
  return None

def find_video(url):
  common.log("", 5)
  import xml.dom.minidom
  import re
  import hashlib
  try:
    request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
    if not request["status"] == 200:
      common.log("Error getting episode page", 3)
      return None
    page = request["content"].encode('utf-8')
    episode_id = re.findall(r'.*?episodeID=(.*?)&.*?',page)[0]
    
    security_code = get_security_code()
    if not security_code:
      common.log("Error getting security code", 3)
      return None
    md5hash = "%s|%s" % (episode_id,security_code)
    md5hash = hashlib.md5(md5hash.upper()).hexdigest().upper()
    
    url = "http://pi.omroep.nl/info/stream/aflevering/%s/%s" % (episode_id,md5hash)
    request = common.fetchPage({"link": url, "cookie": "site_cookie_consent=yes"})
    if not request["status"] == 200:
      common.log("Error getting stream infomartion", 3)
      return None
    page = request["content"].encode('utf-8')
    dom = xml.dom.minidom.parseString(page)
    streamurl = {}
    for stream in dom.getElementsByTagName('stream'):
      if (stream.attributes['compressie_formaat'].value=="mov" and stream.attributes['compressie_kwaliteit'].value==streamquality[0]):
        streamurl[0]=getText(stream.getElementsByTagName('streamurl')[0].childNodes).strip()
      if (stream.attributes['compressie_formaat'].value=="mov" and stream.attributes['compressie_kwaliteit'].value==streamquality[1]):
        streamurl[1]=getText(stream.getElementsByTagName('streamurl')[0].childNodes).strip()
      if (stream.attributes['compressie_formaat'].value=="mov" and stream.attributes['compressie_kwaliteit'].value==streamquality[2]):
        streamurl[2]=getText(stream.getElementsByTagName('streamurl')[0].childNodes).strip()
    for key in [0,1,2]:
      if streamurl.has_key(key):
        common.log("Found stream quality %s" % streamquality[key])
        return streamurl[key]
        break
  except:
    return None
