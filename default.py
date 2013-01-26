#/*
# *      Copyright (C) 2012 Syl
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

import xbmcplugin
import xbmcaddon
import xbmcgui
import sys

# plugin constants
version = "1.2.0"
plugin = "UitzendingGemist-" + version

# xbmc hooks
settings = xbmcaddon.Addon(id='plugin.video.uitzendinggemist')
language = settings.getLocalizedString
dbg = settings.getSetting("debug") == "true"
dbglevel = 5

def addDir(name, module):
        u=sys.argv[0]+"?module="+module
        liz=xbmcgui.ListItem(name)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

if (__name__ == "__main__" ):
  if dbg:
    print plugin + " ARGV: " + repr(sys.argv)
  else:
    print plugin

  import CommonFunctions as common
  common.plugin = plugin
  common.dbg = dbg
  common.dbglevel = dbglevel

  params = common.getParameters(sys.argv[2])

  if 'module' in params: # Module chosen, load and execute module
    module = 'modules.'+params['module']
    __import__(module)
    current_module = sys.modules[module]
    current_module.run(params)
  else: # No module chosen, list modules
    addDir('Zoeken...', 'search')
    addDir('Afgelopen 7 dagen', 'new')
    addDir('Omroepen', 'broadcasters')
    addDir('Regionaal', 'regional')
    addDir('Genres', 'genres')
    addDir('Programma\'s A-Z', 'programs')
    addDir('Top 50', 'top50')
    # Add extra modules here, using addDir(name, module)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
