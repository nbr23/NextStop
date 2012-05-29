#! /usr/bin/python3

import getopt
import sys
import re
import http.cookiejar, urllib.request
import bs4
from unidecode import unidecode


def printUsage(name):
  print("Usage: %s -t transport_type -l line [-s station] " % name)
  print("\t-t transport_type: transportation type: bus, rer, tram, "
      + "noctilien, metro")
  print("\t-l line: line number or name. e.g.: 72, A, T3")
  print("\t-s station: optionnal: station for which to print the next stops")

def getInfoPage(url, opener):
  # This or any other user agent... the default one is denied by the website
  req = urllib.request.Request('http://wap.ratp.fr/siv/' + url, b'',
      { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.4) '
      + 'Gecko/20100101 Firefox/10.0.4 Iceweasel/10.0.4' })
  f = opener.open(req)
  res = str(f.read())
  f.close ()
  return res

# Removes bizarre things from strings
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
def getAllStations(opener, transport, line):
  page = getInfoPage("schedule?stationname=*&reseau=%s&linecode=%s"
      % (transport, line),
      opener)
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
      print("Direction: %s", name)
      page = getInfoPage(directions[name], opener)
      soup = bs4.BeautifulSoup(page)
      links = soup.findAll('a')
      for link in links:
        if re.search(r'stationid=', str(link)):
          stations[cleanString(link.string)] = link['href']
  return stations

# Returns a list of all the stations of the line in both directions
def getAllStationsUrls(opener, transport, line):
  page = getInfoPage("schedule?stationname=*&reseau=%s&linecode=%s"
      % (transport, line),
      opener)
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
      page = getInfoPage(directions[name], opener)
      soup = bs4.BeautifulSoup(page)
      links = soup.findAll('a')
      for link in links:
        if re.search(r'stationid=', str(link)):
          stations.append((cleanString(link.string), link['href']))
  return stations

# Returns the time at a specific station
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



def getNextStopsAtStation(opener, transport, line, station):
  stations = getAllStationsUrls(opener, transport, line)
  results = []
  for key, url in stations:
    if searchNameInData(station, key):
      page = getInfoPage(url, opener)
      soup = bs4.BeautifulSoup(page)
      results += getStationTimes(soup, key)
  return results

def extractInformation(opener,
    transport,
    line,
    station):
  if station != "":
    times = getNextStopsAtStation(opener, transport, line, station)
    for time, direction, stationname in times:
      print("Next %s %s at %s going to %s at %s" %
          (transport, line, stationname, direction, time))
  else:
    stations = getAllStations(opener, transport, line)
    if len(stations) > 0:
      for name in stations:
        print("Station %s." % name)
      return 0
    else:
      print("No station found.")

def main():
  type_transp = ''
  line = ''
  station = ''

  try:
    opt, args = getopt.getopt(sys.argv[1:], "ht:l:s:", ["help"])
  except getopt.GetoptError:
    printUsage(sys.argv[0])
    return 1
  for op, val in opt:
    if op in ("-h", "--help"):
      printUsage(sys.argv[0])
      return 0
    elif op == "-t":
      type_transp = val
    elif op == "-l":
      line = val
    elif op == "-s":
      station = val

  if type_transp == "" or line == "":
    printUsage(sys.argv[0])
    return 1

  cj = http.cookiejar.CookieJar()
  opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

  return extractInformation(opener, type_transp, line, station)

if __name__ == "__main__":
      sys.exit(main())
