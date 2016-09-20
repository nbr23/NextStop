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

def getTransportLines(transport):
  page = getPage("/siv/schedule?service=next&reseau=%s&linecode=*&referer=line"
      % transport.lower())
  soup = bs4.BeautifulSoup(page, "html.parser")
  links = soup.findAll('div', attrs={'class':'bg1'})
  lines = []
  for link in links:
      if link.img and link.img['alt']:
          lines.append(re.sub('[\[\]]', '', link.img['alt'].strip()))
  return lines

# Returns a list of all the stations of the line in both directions
def getAllStationsUrls(transport, line):
  page = getPage("/siv/schedule?stationname=*&reseau=%s&linecode=%s"
      % (transport.lower(), line.lower()))
  soup = bs4.BeautifulSoup(page, "html.parser")
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
      soup = bs4.BeautifulSoup(page, "html.parser")
      links = soup.findAll('a')
      for link in links:
        if re.search(r'stationid=', str(link)):
          stations.append((cleanString(link.string), link['href']))
  return stations

def getStationTimes(soup, station, direction=None):
  divs = soup.findAll('div')
  currentdest = ""
  times = []
  for div in divs:
    try:
      cl = div['class'][0]
      if re.search(r'schmsg', cl):
        if div.b is not None:
          if direction:
            if direction.lower() in cleanString(currentdest).lower():
              times.append((cleanString(div.b.string),
                  cleanString(currentdest), station))
          else:
            times.append((cleanString(div.b.string),
              cleanString(currentdest), station))
      elif re.search('error', cl):
          times.append((div.get_text(), None, station))
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
def getAllStations(transport, line):
  page = getPage('/siv/schedule?stationname=*&reseau=%s&linecode=%s'
      % (transport.lower(), line))
  soup = bs4.BeautifulSoup(page, "html.parser")
  stations = {}
  directions = {}
  links = soup.findAll('a')
  for link in links:
    if re.search(r'directionsens=', str(link)):
      directions[cleanString(link.string)] = link['href']
    elif re.search(r'stationid=', str(link)):
      stations[cleanString(link.string)] = link['href']
  if len(directions) > 0:
    stations = []
    for name in directions:
      page = getPage("/siv/"+directions[name])
      soup = bs4.BeautifulSoup(page, "html.parser")
      links = soup.findAll('a')
      for link in links:
        if re.search(r'stationid=', str(link)):
          stations.append(cleanString(link.string))
  return stations

def getNextStopsAtStation(transport, line, station, direction=None):
  stations = getAllStationsUrls(transport, line)
  results = []
  for key, url in stations:
    if searchNameInData(station, key):
      page = getPage("/siv/"+url)
      soup = bs4.BeautifulSoup(page, "html.parser")
      results += getStationTimes(soup, key, direction)
  return results

def getDisturbance(cause, transport):
    if cause == '':
        disturbance = ""
        for cause in ("manif", "alerte", "travaux"):
            if disturbance != "":
                disturbance += "\n**"+cause+"\n"
            disturbance += getDisturbanceFromCause(cause, transport.lower())
        return disturbance
    else:
        return getDisturbanceFromCause(cause.lower(), transport.lower())

def getDisturbanceFromCause(cause, transport):
    page = getPage('/siv/perturbation?cause=%s&reseau=%s' % (cause, transport))
    soup = bs4.BeautifulSoup(page, "html.parser")
    content = soup.find_all('div', { "class" : "bg1" })
    disturbances = ""
    for item in content:
        if disturbances != "":
            disturbances += "\n"
        item = str(item).replace('<br/>', ' ').replace('  ', ' ')
        disturbances += (bs4.BeautifulSoup(item, "html.parser").get_text())
    return disturbances
