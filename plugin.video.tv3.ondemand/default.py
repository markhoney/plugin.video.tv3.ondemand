#/*
# *   Copyright (C) 2010 Mark Honeychurch
# *   based on the TVNZ Addon by JMarshall
# *
# *
# * This Program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2, or (at your option)
# * any later version.
# *
# * This Program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; see the file COPYING. If not, write to
# * the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# * http://www.gnu.org/copyleft/gpl.html
# *
# */

#http://ondemand.tv3.co.nz/Host/SQL/tabid/21/ctl/Login/portalid/0/Default.aspx

import urllib, urllib2, htmllib, string, unicodedata, re, time, urlparse, cgi, xbmcgui, xbmcplugin, xbmcaddon
from htmlentitydefs import name2codepoint
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup, SoupStrainer

urls = dict()
urls["TV3"] = 'http://www.tv3.co.nz'
urls["BASE1"] = 'http://ondemand'
urls["BASE2"] = 'co.nz'
urls["RTMP1"] = 'rtmpe://nzcontent.mediaworks.co.nz'
urls["RTMP2"] = '_definst_/mp4:'
urls["VIDEO1"] = 'tabid'
urls["VIDEO2"] = 'articleID'
urls["VIDEO3"] = 'MCat'
urls["VIDEO4"] = 'Default.aspx'
urls["FEEDBURNER_RE"] = '//feedproxy\.google\.com/'
urls["CAT"] = '/default404.aspx?tabid='
urls["CAT_RE"] = '/default404\.aspx\?tabid='
urls["IMG_RE"] = '\.ondemand\.tv3\.co\.nz/Portals/0-Articles/'
MIN_BITRATE = 400000
__addon__ = xbmcaddon.Addon(id='plugin.video.tv3.ondemand')


def message(message):
 dialog = xbmcgui.Dialog()
 if message:
  if message <> "":
   dialog.ok("Warning", message)
  else:
   dialog.ok("Warning", "Empty message text")
 else:
  dialog.ok("Warning", "No message text")

def gethtmlpage(url):
 sys.stderr.write("Requesting page: %s" % (url))
 req = urllib2.Request(url)
 response = urllib2.urlopen(req)
 doc = response.read()
 response.close()
 return doc

def unescape(s):
 return re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

def checkdict(info, items):
 for item in items:
  if info.get(item, "##unlikelyphrase##") == "##unlikelyphrase##":
   sys.stderr.write("Dictionary missing item: %s" % (item))
   return 0
 return 1

def addlistitem(info, folder = 0):
 if checkdict(info, ("Title", "Icon", "Thumb", "FileName")):
  liz = xbmcgui.ListItem(info["Title"], iconImage = info["Icon"], thumbnailImage = info["Thumb"])
  liz.setInfo(type = "Video", infoLabels = info)
  if not folder:
   liz.setProperty("IsPlayable", "true")
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = info["FileName"], listitem = liz, isFolder = folder)

def defaultinfo(folder = 0):
 info = dict()
 if folder:
  info["Icon"] = "DefaultFolder.png"
 else:
  info["Icon"] = "DefaultVideo.png"
  #info["VideoCodec"] = "flv"
  #info["VideoCodec"] = "avc1"
  #info["VideoCodec"] = "h264"
  #info["VideoResolution"] = "480" #actually 360 (640x360)
  #info["VideoAspect"] = "1.78"
  #info["AudioCodec"] = "aac"
  #info["AudioChannels"] = "2"
  #info["AudioLanguage"] = "eng"
 info["Thumb"] = ""
 return info

def xbmcdate(inputdate):
 return time.strftime(xbmc.getRegion( "datelong" ).replace( "DDDD,", "" ).replace( "MMMM", "%B" ).replace( "D", "%d" ).replace( "YYYY", "%Y" ).strip(), time.strptime(inputdate,"%d/%m/%y"))

def seasonepisode(se):
 if se:
  info = dict()
  info["PlotOutline"] = se.string.strip()
  season = re.search("(Cycle|Season) ([0-9]+)", se.string)
  seasonfound = 0
  if season:
   info["Season"] = int(season.group(2))
   seasonfound = 1
  episode = re.search("Ep(|isode) ([0-9]+)", se.string)
  if episode:
   info["Episode"] = int(episode.group(2))
   if not seasonfound:
    info["Season"] = 1
  return info

def dateduration(ad):
 if ad:
  info = dict()
  aired = re.search("([0-9]{2}/[0-9]{2}/[0-9]{2})", ad.contents[1])
  if aired:
   #info["Aired"] = time.strftime("%Y-%m-%d", time.strptime(aired.group(1),"%d/%m/%y"))
   info["Aired"] = xbmcdate(aired.group(1))
   info["Date"] = info["Aired"]
   #info["Year"] = int(time.strftime("%Y", info["Aired"]))
  duration = re.search("\(([0-9]+:[0-9]{2})\)", ad.contents[1])
  if duration:
   #info["Duration"] = duration.group(2)
   info["Duration"] = time.strftime("%M", time.strptime(duration.group(1), "%M:%S"))
  return info

def imageinfo(image):
 if image:
  info = dict()
  info["Thumb"] = image['src']
  #alttitle = image['title']
  return info

def itemtitle(Title, PlotOutline):
 if PlotOutline:
  Title = "%s - %s" % (Title, PlotOutline)
 return Title

def constructStackURL(playlist):
 uri = ""
 for url in playlist:
  url.replace(',',',,')
  if len(uri)>0:
   uri = uri + " , " + url
  else:
   uri = "stack://" + url
 return(uri)

def base_url(provider):
 return "%s.%s.%s" % (urls["BASE1"], provider, urls["BASE2"])

def rtmp(provider):
 if provider == "c4tv":
  return "%s/%s/%s" % (urls["RTMP1"], "c4", urls["RTMP2"])
 else:
  return "%s/%s/%s" % (urls["RTMP1"], provider, urls["RTMP2"])










def INDEX_FOLDERS():
 folders = dict()
 folders["0"] = "Categories"
 folders["1"] = "Channels"
 folders["2"] = "Genres"
 folders["3"] = "Shows"
 for index in folders:
  info = defaultinfo(1)
  info["Title"] = folders[index]
  info["Count"] = int(index)
  info["FileName"] = "%s?folder=%s" % (sys.argv[0], folders[index])
  addlistitem(info, 1)

def INDEX_FOLDER(folder):
 infopages = dict()
 infopages["0"]  = ("63", "Categories", "tv3", "Latest")
 infopages["1"]  = ("61", "Categories", "tv3", "Most Watched")
 infopages["2"]  = ("64", "Categories", "tv3", "Expiring Soon")
 infopages["3"]  = ("70", "Categories", "atoz", "A - Z")
 infopages["4"]  = ("71", "Channels", "tv3", "TV3")
 infopages["5"]  = ("72", "Channels", "c4tv", "C4")
 infopages["6"]  = ("65", "Genres", "tv3", "Comedy")
 infopages["7"]  = ("66", "Genres", "tv3", "Drama")
 infopages["8"]  = ("67", "Genres", "tv3", "News/Current Affairs")
 infopages["9"]  = ("68", "Genres", "tv3", "Reality")
 infopages["10"] = ("82", "Genres", "tv3", "Sports")
 infopages["11"] = ("80", "Categories", "tv3", "All")
 #infopages["12"] = ("74", "RSS", "tv3", "RSS Feeds")
 #infopages["13"] = ("81", "Categories", "tv3", "C4 Highlights")
 #infopages["13"] = ("73", "Categories", "tv3", "All (Small)")
 for index in infopages:
  if infopages[index][1] == folder:
   info = defaultinfo(1)
   info["Title"] = infopages[index][3]
   info["Count"] = int(index)
   info["FileName"] = "%s?cat=%s&catid=%s" % (sys.argv[0], infopages[index][2], infopages[index][0])
   addlistitem(info, 1)
 if folder == "Shows":
  INDEX_SHOWS("tv3")

def INDEX(provider):
 doc = gethtmlpage("%s/tabid/56/default.aspx" % (base_url(provider))) #Get our HTML page with a list of video categories
 if doc:
  a_tag = SoupStrainer('a')
  html_atag = BeautifulSoup(doc, parseOnlyThese = a_tag)
  links = html_atag.findAll(attrs={"rel": "nofollow", "href": re.compile(urls["CAT_RE"])}) #, "title": True
  if len(links) > 0:
   count = 0
   for link in links:
    info = defaultinfo(1)
    info["Title"] = link.string
    caturl = link['href']
    catid = re.search('%s([0-9]+)' % (urls["CAT_RE"]), caturl).group(1)
    if info["Title"] == "Title (A - Z)":
     cat = "atoz"
    elif info["Title"] == "TV3 Shows":
     cat = "tv3"
    elif info["Title"] == "C4TV Shows":
     cat = "c4tv"
    else:
     cat = "tv"
    if catid:
     info["Count"] = count
     count += 1
     info["FileName"] = "%s?cat=%s&catid=%s" % (sys.argv[0], cat, catid)
     addlistitem(info, 1)
  else:
   sys.stderr.write("Couldn't find any categories")
 else:
  sys.stderr.write("Couldn't get index webpage")

def INDEX_SHOWS(provider):
 doc = gethtmlpage("%s/Shows/tabid/64/Default.aspx" % ("http://www.tv3.co.nz")) #Get our HTML page with a list of video categories
 if doc:
  #div_tag = SoupStrainer('div')
  #html_divtag = BeautifulSoup(doc, parseOnlyThese = div_tag)
  html_divtag = BeautifulSoup(doc)
  linksdiv = html_divtag.find('div', attrs = {"id": "pw_8171"})
  if linksdiv:
   links = linksdiv.findAll('a')
   if len(links) > 0:
    count = 0
    for link in links:
     info = defaultinfo(1)
     info["Title"] = link.string.strip()
     catid = link['href']
     if info["Title"] == "60 Minutes": #The URL on the next line has more videos
      info["FileName"] = "%s?cat=%s&title=%s&catid=%s" % (sys.argv[0], "shows", urllib.quote(info["Title"]), urllib.quote(catid)) #"http://ondemand.tv3.co.nz/Default.aspx?TabId=80&cat=22"
     else:
      info["FileName"] = "%s?cat=%s&title=%s&catid=%s" % (sys.argv[0], "shows", urllib.quote(info["Title"]), urllib.quote(catid))
     info["Count"] = count
     count += 1
     addlistitem(info, 1)
   else:
    sys.stderr.write("Couldn't find any videos in list")
  else:
   sys.stderr.write("Couldn't find video list")
 else:
  sys.stderr.write("Couldn't get index webpage")












def SHOW_EPISODES(catid, provider):
 doc = gethtmlpage("%s%s%s" % (base_url("tv3"), urls["CAT"], catid))
 if doc:
  a_tag=SoupStrainer('div')
  html_atag = BeautifulSoup(doc, parseOnlyThese = a_tag)
  programs = html_atag.findAll(attrs={"class": "latestArticle "})
  if len(programs) > 0:
   count = 0
   baseurl = base_url(provider)
   for soup in programs:
    info = defaultinfo()
    info["Studio"] = provider
    link = soup.find("a", attrs={"href": re.compile(baseurl)})
    if link:
     href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, urls["VIDEO1"], urls["VIDEO2"], urls["VIDEO3"]), link['href'])
     if href:
      if link.string:
       title = link.string.strip()
       if title <> "":
        info["TVShowTitle"] = title
        image = soup.find("img", attrs={"src": re.compile(urls["IMG_RE"]), "title": True})
        if image:
         info.update(imageinfo(image))
        info.update(seasonepisode(soup.find("span", attrs={"class": "title"})))
        info.update(dateduration(soup.find("span", attrs={"class": "dateAdded"})))
        info["Title"] = itemtitle(info["TVShowTitle"], info["PlotOutline"])
        info["Count"] = count
        count += 1
        plot = soup.find("div", attrs={"class": "left"}).string
        if plot:
         if plot.strip() <> "":
          info["Plot"] = unescape(plot.strip())
        info["FileName"] = "%s?id=%s&info=%s" % (sys.argv[0], "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), urllib.quote(str(info)))
        addlistitem(info, 0)
  else:
   sys.stderr.write("Couldn't find any videos")
 else:
  sys.stderr.write("Couldn't get videos webpage")


def SHOW_ATOZ(catid, provider):
 doc = gethtmlpage("%s%s%s" % (base_url("tv3"), urls["CAT"], catid))
 if doc:
  a_tag=SoupStrainer('div')
  html_atag = BeautifulSoup(doc, parseOnlyThese = a_tag)
  programs = html_atag.findAll(attrs={"class": "wideArticles"})
  if len(programs) > 0:
   baseurl = base_url(provider)
   count = 0
   for soup in programs:
    info = defaultinfo()
    info["Studio"] = provider
    link = soup.h5.find("a", attrs={"href": re.compile(baseurl)})
    if link:
     href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, urls["VIDEO1"], urls["VIDEO2"], urls["VIDEO3"]), link['href'])
     if href:
      if link.string:
       title = link.string.strip()
       if title <> "":
        info["TVShowTitle"] = title
        info.update(imageinfo(soup.find("img", attrs={"src": re.compile(urls["IMG_RE"]), "title": True})))
        info.update(seasonepisode(soup.contents[4]))
        info["Title"] = itemtitle(info["TVShowTitle"], info["PlotOutline"])
        info["Plot"] = unescape(soup.find("span", attrs={"class": "lite"}).string.strip())
        info["Count"] = count
        count += 1
        info["FileName"] = "%s?id=%s&info=%s" % (sys.argv[0], "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), urllib.quote(str(info)))
        addlistitem(info, 0)
  else:
   sys.stderr.write("Couldn't find any videos")
 else:
  sys.stderr.write("Couldn't get videos webpage")

def SHOW_SHOW(catid, title, provider):
 baseurl = ""
 if catid[:4] <> "http":
  baseurl = urls["TV3"]
 geturl = "%s%s" % (baseurl, catid)
 doc = gethtmlpage(geturl)
 if doc:
  div_tag=SoupStrainer('div')
  html_divtag = BeautifulSoup(doc, parseOnlyThese = div_tag)
  tables = html_divtag.find(attrs={"xmlns:msxsl": "urn:schemas-microsoft-com:xslt"})
  if tables:
   programs = tables.findAll('table')
   if len(programs) > 0:
    count = 0
    for soup in programs:
     info = defaultinfo()
     info["Studio"] = provider
     bold = soup.find('b')
     if bold:
      link = bold.find("a", attrs={"href": re.compile(urls["FEEDBURNER_RE"])})
      if link:
       urltype = "other"
      else:
       link = bold.find("a", attrs={"href": re.compile(base_url("tv3"))})
       if link:
        urltype = "tv3"
      if link:
       if link.string:
        plot = link.string.strip()
        if plot <> "":
         info["PlotOutline"] = plot
         info["TVShowTitle"] = title
         info.update(imageinfo(soup.find("img", attrs={"src": re.compile(urls["IMG_RE"])})))
         info.update(seasonepisode(link))
         info["Title"] = itemtitle(info["TVShowTitle"], info["PlotOutline"])
         info["Count"] = count
         count += 1
         if urltype == "tv3":
          href = re.search("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (base_url("tv3"), urls["VIDEO1"], urls["VIDEO2"], urls["VIDEO3"]), link['href'])
          if href:
           info["FileName"] = "%s?id=%s&info=%s" % (sys.argv[0], "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), urllib.quote(str(info)))
         elif urltype == "other":
          info["FileName"] = "%s?id=%s&info=%s" % (sys.argv[0], urllib.quote(link["href"]), urllib.quote(str(info)))
         addlistitem(info, 0)
   else:
    sys.stderr.write("Couldn't find any videos in list")
  else:
   sys.stderr.write("Couldn't find video list")
 else:
  sys.stderr.write("Couldn't get index webpage")









def RESOLVE(id, info):
 #http://ondemand.tv3.co.nz/Season-7-Ep-10/tabid/59/articleID/1075/MCat/118/Default.aspx
 #http://ondemand.tv3.co.nz/tabid/59/articleID/1075/118
 #var video ="/*transfer*07092010*HW026232";
 #var fo = new FlashObject("http://static.mediaworks.co.nz/video/3.1/videoPlayer3.1.swf?rnd="+random_num+"", "flashPlayerSwf", "640", "390", "10", "#000000");
 ids = id.split(",")
 if len(ids) == 4:
  doc = gethtmlpage("%s/%s/%s/%s/%s/%s/%s/%s/%s" % (base_url(info["Studio"]), ids[0], urls["VIDEO1"], ids[1], urls["VIDEO2"], ids[2], urls["VIDEO3"], ids[3], urls["VIDEO4"]))
 else:
  doc = gethtmlpage("id")
 if doc:
  #videoid = re.search('var video ="/\*transfer\*([0-9]+)\*([0-9A-Z]+)";', doc)
  videoid = re.search('var video ="/\*(.*?)\*([0-9]+)\*(.*?)";', doc)
  if videoid:
   videoplayer = re.search('var fo = new FlashObject\("(http://static.mediaworks.co.nz/(.*?).swf)', doc)
   if videoplayer:
    playlist=list()
    #if __addon__.getSetting('advert') == 'true':
     #playlist.append(ad)
    quality = "330K"
    if __addon__.getSetting('hq') == 'true':
     quality = "700K"
    rtmpurl = '%s/%s/%s/%s_%s' % (rtmp(info["Studio"]), videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality)
    sys.stderr.write("RTMP URL: %s" % (rtmpurl))
    swfverify = ' swfUrl=%s swfVfy=true' % (videoplayer.group(1))
    sys.stderr.write("Flash Player: %s" % (videoplayer.group(1)))
    playlist.append(rtmpurl + swfverify)
    if len(playlist) > 1:
     uri = constructStackURL(playlist)
    elif len(playlist) == 1:
     uri = playlist[0]
    liz = xbmcgui.ListItem(id, iconImage = info["Icon"], thumbnailImage = info["Thumb"])
    liz.setInfo( type = "Video", infoLabels = info)
    liz.setProperty("IsPlayable", "true")
    liz.setPath(uri)
    xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = liz)
   else:
    sys.stderr.write("Couldn't get video player URL")
  else:
   sys.stderr.write("Couldn't get video RTMP URL")
 else:
  sys.stderr.write("Couldn't get video webpage")










params = cgi.parse_qs(urlparse.urlparse(sys.argv[2])[4])
if params:
 if params.get("folder", "") <> "":
  INDEX_FOLDER(params["folder"][0])
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
  #xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL)
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
 elif params.get("cat", "") <> "":
  if params["cat"][0] == "tv":
   SHOW_EPISODES(params["catid"][0], "tv3")
  elif params["cat"][0] == "atoz":
   SHOW_ATOZ(params["catid"][0], "tv3")
  elif params["cat"][0] == "tv3":
   SHOW_EPISODES(params["catid"][0], "tv3")
  elif params["cat"][0] == "c4tv":
   SHOW_EPISODES(params["catid"][0], "c4tv")
  elif params["cat"][0] == "shows":
   SHOW_SHOW(urllib.unquote(params["catid"][0]), urllib.unquote(params["title"][0]), "tv3")
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
  #xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_DATE)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_EPISODE)
  xbmcplugin.setContent(handle = int(sys.argv[1]), content = "episodes")
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
 elif params.get("id", "") <> "":
  RESOLVE(params["id"][0], eval(urllib.unquote(params["info"][0])))
else:
 if __addon__.getSetting('folders') == 'true':
  INDEX_FOLDERS()
 else:
  INDEX("tv3")
 xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
 #xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
 xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL)
 xbmcplugin.endOfDirectory(int(sys.argv[1]))


