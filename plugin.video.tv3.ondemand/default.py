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


import urllib,urllib2,string,unicodedata,re,time,urlparse,cgi,xbmcgui,xbmcplugin,xbmcaddon
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup, SoupStrainer

urls = dict()
urls["BASE_URL1"] = 'http://ondemand'
urls["BASE_URL2"] = 'co.nz'
urls["RTMP_URL1"] = 'rtmpe://nzcontent.mediaworks.co.nz'
urls["RTMP_URL2"] = '_definst_/mp4:'
urls["VIDEO_URL1"] = 'tabid'
urls["VIDEO_URL2"] = 'articleID'
urls["VIDEO_URL3"] = 'MCat'
urls["VIDEO_URL4"] = 'Default.aspx'
urls["CAT_URL"] = '/default404.aspx?tabid='
urls["CAT_URL_RE"] = '/default404\.aspx\?tabid='
urls["IMG_URL_RE"] = '\.ondemand\.tv3\.co\.nz/Portals/0-Articles/'
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

def addlistitem(info, folder = 0):
 liz = xbmcgui.ListItem(info["Title"], iconImage = info["Icon"], thumbnailImage = info["Thumb"])
 liz.setInfo(type = "Video", infoLabels = info)
 if not folder:
  liz.setProperty("IsPlayable", "true")
 xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = info["FileName"], listitem = liz, isFolder = folder)

def addlistfolder(info):
 liz = xbmcgui.ListItem(info["Title"], iconImage = "DefaultFolder.png", thumbnailImage = info["Thumb"])
 liz.setInfo(type = "Video", infoLabels = info)
 xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = info["FileName"], listitem = liz, isFolder = True)

def addlistitemold(info):
 liz = xbmcgui.ListItem(info["Title"], iconImage="DefaultVideo.png", thumbnailImage = info["Thumb"])
 liz.setInfo(type = "Video", infoLabels = info)
 liz.setProperty("IsPlayable", "true")
 xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = info["FileName"], listitem = liz, isFolder = False)
 
def defaultinfo(folder = 0):
 info = dict()
 if folder:
  info["Icon"] = "DefaultFolder.png"
  info["Thumb"] = ""
 else:
  info["Icon"] = "DefaultVideo.png"
  #info["VideoCodec"] = "flv"
  #info["VideoCodec"] = "avc1"
  info["VideoCodec"] = "h264"
  info["VideoResolution"] = "480" #actually 360 (640x360)
  info["VideoAspect"] = "1.78"
  info["AudioCodec"] = "aac"
  info["AudioChannels"] = "2"
  info["AudioLanguage"] = "eng"
 return info


def xbmcdate(inputdate):
 return time.strftime(xbmc.getRegion( "datelong" ).replace( "DDDD,", "" ).replace( "MMMM", "%B" ).replace( "D", "%d" ).replace( "YYYY", "%Y" ).strip(), time.strptime(inputdate,"%d/%m/%y"))

def seasonepisode(se):
 if se:
  info = dict()
  info["PlotOutline"] = se.string.strip()
  season = re.search("Season ([0-9]+)", se.string)
  seasonfound = 0
  if season:
   info["Season"] = int(season.group(1))
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
 return "%s.%s.%s" % (urls["BASE_URL1"], provider, urls["BASE_URL2"])

def rtmp_url(provider):
 if provider == "c4tv":
  return "%s/%s/%s" % (urls["RTMP_URL1"], "c4", urls["RTMP_URL2"])
 else:
  return "%s/%s/%s" % (urls["RTMP_URL1"], provider, urls["RTMP_URL2"])










#   info = defaultinfo(1)
#   info["Title"] = "TV Show Index"
#   info["FileName"] = "%s?cat=%s&catid=%s" % (sys.argv[0], "shows", "64")
#   info["Count"] = count
#   addlistitem(info, 1)



def INDEX(provider):
 doc = gethtmlpage("%s/tabid/56/default.aspx" % (base_url(provider))) #Get our HTML page with a list of video categories
 if doc:
  a_tag = SoupStrainer('a')
  html_atag = BeautifulSoup(doc, parseOnlyThese = a_tag)
  links = html_atag.findAll(attrs={"rel": "nofollow", "href": re.compile(urls["CAT_URL_RE"])}) #, "title": True
  if len(links) > 0:
   count = 0
   for link in links:
    info = defaultinfo(1)
    info["Title"] = link.string
    caturl = link['href']
    catid = re.search('%s([0-9]+)' % (urls["CAT_URL_RE"]), caturl).group(1)
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
   links = linksdiv.findall('a')
   if len(links) > 0:
    count = 0
    for link in links:
     info = defaultinfo(1)
     info["Title"] = link.string.strip()
     catid = link['href']
     info["FileName"] = "%s?cat=%s&catid=%s" % (sys.argv[0], "show", catid) 
     info["Count"] = count
     count += 1
     addlistitem(info, 1)
   else:
    sys.stderr.write("Couldn't find any videos in list")
  else:
   sys.stderr.write("Couldn't find video list")
 else:
  sys.stderr.write("Couldn't get index webpage")

def SHOW_SHOW(catid, provider):
 message("Test")

def SHOW_EPISODES(catid, provider):
 doc = gethtmlpage("%s%s%s" % (base_url("tv3"), urls["CAT_URL"], catid))
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
     href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, urls["VIDEO_URL1"], urls["VIDEO_URL2"], urls["VIDEO_URL3"]), link['href'])
     if href:
      if link.string:
       title = link.string.strip()
       if title <> "":
        info["TVShowTitle"] = title
        info.update(imageinfo(soup.find("img", attrs={"src": re.compile(urls["IMG_URL_RE"]), "title": True})))
        info.update(seasonepisode(soup.find("span", attrs={"class": "title"})))
        info.update(dateduration(soup.find("span", attrs={"class": "dateAdded"})))
        info["FileName"] = "%s?id=%s&info=%s" % (sys.argv[0], "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), urllib.quote(str(info)))
        info["Title"] = itemtitle(info["TVShowTitle"], info["PlotOutline"])
        info["Count"] = count
        count += 1
        plot = soup.find("div", attrs={"class": "left"}).string
        if plot:
         if plot.strip() <> "":
          info["Plot"] = plot.strip()
        addlistitem(info, 0)
  else:
   sys.stderr.write("Couldn't find any videos")
 else:
  sys.stderr.write("Couldn't get videos webpage")


def SHOW_ATOZ(catid, provider):
 doc = gethtmlpage("%s%s%s" % (base_url("tv3"), urls["CAT_URL"], catid))
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
     href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, urls["VIDEO_URL1"], urls["VIDEO_URL2"], urls["VIDEO_URL3"]), link['href'])
     if href:
      if link.string:
       title = link.string.strip()
       if title <> "":
        info["TVShowTitle"] = title
        info.update(imageinfo(soup.find("img", attrs={"src": re.compile(urls["IMG_URL_RE"]), "title": True})))
        info.update(seasonepisode(soup.contents[4]))
        info["FileName"] = "%s?id=%s&info=%s" % (sys.argv[0], "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), urllib.quote(str(info)))
        info["Title"] = itemtitle(info["TVShowTitle"], info["PlotOutline"])
        info["Plot"] = soup.find("span", attrs={"class": "lite"}).string.strip()
        info["Count"] = count
        count += 1
        addlistitem(info, 0)
  else:
   sys.stderr.write("Couldn't find any videos")
 else:
  sys.stderr.write("Couldn't get videos webpage")

def RESOLVE(id, info):
 #http://ondemand.tv3.co.nz/Season-7-Ep-10/tabid/59/articleID/1075/MCat/118/Default.aspx
 #http://ondemand.tv3.co.nz/tabid/59/articleID/1075/118
 #var video ="/*transfer*07092010*HW026232";
 #var fo = new FlashObject("http://static.mediaworks.co.nz/video/3.1/videoPlayer3.1.swf?rnd="+random_num+"", "flashPlayerSwf", "640", "390", "10", "#000000");
 ids = id.split(",")
 doc = gethtmlpage("%s/%s/%s/%s/%s/%s/%s/%s/%s" % (base_url(info["Studio"]), ids[0], urls["VIDEO_URL1"], ids[1], urls["VIDEO_URL2"], ids[2], urls["VIDEO_URL3"], ids[3], urls["VIDEO_URL4"]))
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
    rtmpurl = '%s/%s/%s/%s_%s' % (rtmp_url(info["Studio"]), videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality)
    sys.stderr.write("RTMP URL: %s" % (rtmpurl))
    swfverify = ' swfUrl=%s swfVfy=true' % (videoplayer.group(1))
    sys.stderr.write("Flash Player: %s" % (videoplayer.group(1)))
    playlist.append(rtmpurl + swfverify)
    if len(playlist) > 1:
     uri = constructStackURL(playlist)
    elif len(playlist) == 1:
     uri = playlist[0]
    liz = xbmcgui.ListItem(id, iconImage = "DefaultVideo.png", thumbnailImage = "")
    liz.setInfo( type = "Video", infoLabels = {'episode': 1})
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
 if params.get("cat", "") <> "":
  if params["cat"][0] == "tv":
   SHOW_EPISODES(params["catid"][0], "tv3")
  elif params["cat"][0] == "atoz":
   SHOW_ATOZ(params["catid"][0], "tv3")
  elif params["cat"][0] == "tv3":
   SHOW_EPISODES(params["catid"][0], "tv3")
  elif params["cat"][0] == "c4tv":
   SHOW_EPISODES(params["catid"][0], "c4tv")
  elif params["cat"][0] == "shows":
   INDEX_SHOWS("tv3")
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_DATE)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
  xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_EPISODE)
  xbmcplugin.setContent(handle = int(sys.argv[1]), content = "episodes")
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
 elif params.get("id", "") <> "":
  RESOLVE(params["id"][0], eval(urllib.unquote(params["info"][0])))
else:
 INDEX("tv3")
 xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
 xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
 xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL)
 xbmcplugin.endOfDirectory(int(sys.argv[1]))


