#! /usr/bin/python3

import re
import http.cookiejar, urllib.request
import bs4
from unidecode import unidecode

def getPage (page):
  conn = http.client.HTTPConnection("wap.ratp.fr", timeout=10)
  #We need a "proper" UA otherwise ratp.fr gives us a boggus page
  conn.request("GET", page, "",
      {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:10.0.4) "
        + "Gecko/20100101 Firefox/10.0.4 Iceweasel/10.0.4"})
  res = conn.getresponse()
  data = res.read()
  conn.close()
  return data

# Returns a list of all the stations of the line in both directions
def getAllStationsUrls(transport, line):
  page = getPage("/siv/schedule?stationname=*&reseau=%s&linecode=%s"
      % (transport, line))
  soup = bs4.BeautifulSoup(page)
  stations = []
  directions = {}
  links = soup.findAll('a')
  for link in links:
    if re.search(r'directionsens=', str(link)):
      directions[cleanString(link.string)] = link['href']
    elif re.search(r'stationid=', str(link)):
      stations.append((cleanString(link.string), link['href']))
  if len(directions) > 0:
    stations = []
    for name in directions:
      page = getPage("/siv/"+directions[name])
      soup = bs4.BeautifulSoup(page)
      links = soup.findAll('a')
      for link in links:
        if re.search(r'stationid=', str(link)):
          stations.append((cleanString(link.string), link['href']))
  return stations

def getStationTimes(soup, station):
  divs = soup.findAll('div')
  currentdest = ""
  times = []
  for div in divs:
    try:
      cl = div['class'][0]
      if re.search(r'schmsg', cl):
        if div.b is not None:
          times.append((cleanString(div.b.string),
            cleanString(currentdest), station))
      if re.search(r'bg', cl):
        m = re.search(r'([-_a-zA-Z-9]+[^>]*[-_a-zA-Z-9]+)', str(div.string))
        if m is not None:
          currentdest = m.group()
    except KeyError:
      next
  return times

def cleanString(mystr):
  mystr = re.sub(r'\\\'', '\'', mystr)
  mystr = re.sub(r'[-]', ' ', mystr)
  mystr = re.sub(r'[ ][ ]+', ' ', mystr)
  return unidecode(mystr)

def searchNameInData(name, data):
  return re.search(r'%s' % cleanString(name),
      cleanString(data),
      re.IGNORECASE)

# Returns a hashtable of all the stations of the line in both directions
def getAllStations(msg, transport, line):
  page = getPage('/siv/schedule?stationname=*&reseau=%s&linecode=%s'
      % (transport, line))
  soup = bs4.BeautifulSoup(page)
  stations = {}
  directions = {}
  links = soup.findAll('a')
  for link in links:
    if re.search(r'directionsens=', str(link)):
      directions[cleanString(link.string)] = link['href']
    elif re.search(r'stationid=', str(link)):
      stations[cleanString(link.string)] = link['href']
  if len(directions) > 0:
    stations = {}
    for name in directions:
      msg.send_chn("%s: Direction: %s." % (msg.nick, name))
      page = getPage("/siv/"+directions[name])
      soup = bs4.BeautifulSoup(page)
      links = soup.findAll('a')
      for link in links:
        if re.search(r'stationid=', str(link)):
          stations[cleanString(link.string)] = link['href']
  return stations



def getNextStopsAtStation(transport, line, station):
  stations = getAllStationsUrls(transport, line)
  results = []
  for key, url in stations:
    if searchNameInData(station, key):
      page = getPage("/siv/"+url)
      soup = bs4.BeautifulSoup(page)
      results += getStationTimes(soup, key)
  return results



def extractInformation(transport,
    line,
    station):
  if station is not None and station != "":
    times = getNextStopsAtStation(transport, line, station)
    stops = ""
    for time, direction, stationname in times:
      station = stationname
      stops += time+" direction "+direction+"; "
    if len(stops) > 0:
      print("Prochains passages du %s ligne %s à l'arrêt %s: %s" %
          (transport, line, stationname, stops))
    else:
      print("La station `%s' ne semble pas exister sur le %s ligne %s."
          % (station, transport, line))
  else:
    stations = getAllStations(msg, transport, line)
    if len(stations) > 0:
      s = ""
      for name in stations:
        s += name + "; "
      print("Stations: %s." % (s))
      return 0
    else:
      print("Aucune station trouvée.")


