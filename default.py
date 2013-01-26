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
import sys

def get_params():
        param={}
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

def addDir(name, module):
        u=sys.argv[0]+"?module="+module
        liz=xbmcgui.ListItem(name)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

params=get_params() # First, get the parameters

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
  # Add extra modules here, using addDir(name, module)
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
