#! /usr/bin/python3

import getopt
import sys
import ratp


def extractInformation(transport,
    line,
    station, direction):
  if station is not None and station != "":
    times = ratp.getNextStopsAtStation(transport, line, station, direction)
    stops = ""
    for time, direction, stationname in times:
      station = stationname
      stops += ("\n—%s: %s direction %s;" % (station, time, direction))
    if len(stops) > 0:
      print("Prochains passages du %s ligne %s à l'arrêt %s : %s" %
          (transport, line, stationname, stops))
    else:
      print("La station `%s' ne semble pas exister sur le %s ligne %s."
          % (station, transport, line))
  else:
    stations = ratp.getAllStations(transport, line)
    if len(stations) > 0:
      s = ""
      for name in stations:
        s += "\n— " + name + " ;"
      print("Stations : %s" % (s))
      return 0
    else:
      print("Aucune station trouvée.")



def printUsage(name):
  print("Usage:\t%s -t transport_type -l line [-s station [-d direction]] " % name)
  print("\t%s -a -t transport_type -c cause" % name)
  print("\t-h: Display this help")
  print("\t-t transport_type: transportation type: bus, rer, tram, "
      + "noctilien, metro")
  print("\t-l line: line number or name. e.g.: 72, A, T3")
  print("\t-s station: optionnal: station for which to print the next stops")
  print("\t-d destination: optionnal: destination for which to print the next stops")
  print("\t-c cause: cause of the disturbance (alerte, travaux, or manif)")
  print("\t-a: get alerts and transportation status (work on the line, manifestations)")

def main():
  type_transp = ''
  line = ''
  station = ''
  alert = False
  cause = ''
  destination = None

  try:
    opt, args = getopt.getopt(sys.argv[1:], "aht:l:s:d:c:", ["help"])
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
    elif op == "-a":
      alert = True
    elif op == "-c":
      cause = val
    elif op == "-d":
      destination = val

  if alert:
    if type_transp == "" and cause == "":
      printUsage(sys.argv[0])
      return 1
    print(ratp.getDisturbance(cause, type_transp))
    return 0
  if type_transp == "" or line == "":
    printUsage(sys.argv[0])
    return 1

  return extractInformation(type_transp, line, station, destination)

if __name__ == "__main__":
      sys.exit(main())
