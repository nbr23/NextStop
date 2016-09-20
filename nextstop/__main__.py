#! /usr/bin/env python3

import argparse
import sys

from . import ratp


def extractInformation(transport,
    line,
    station, direction):
  if station is not None and station != "":
    times = ratp.getNextStopsAtStation(transport, line, station, direction)
    stops = ""
    for time, direction, stationname in times:
      station = stationname
      if direction:
        stops += ("\n—%s: %s direction %s;" % (station, time, direction))
      else:
        stops += ("\n—%s: %s;" % (station, time))
    if len(stops) > 0:
      print("Prochains passages du %s ligne %s à l'arrêt %s : %s" %
          (transport, line, stationname, stops))
    else:
      print("La station `%s' ne semble pas exister sur le %s ligne %s."
          % (station, transport, line))
  elif line is not None:
    stations = ratp.getAllStations(transport, line)
    if len(stations) > 0:
      s = ""
      for name in stations:
          s += "\n— " + name + " ;"
      print("Stations : %s" % (s))
      return 0
    else:
        print("Aucune station trouvée.")
  else:
      lines = ratp.getTransportLines(transport)
      if len(lines) > 0:
          s = ""
          for name in lines:
              s += "\n— " + name + " ;"
          print("Lignes : %s" % s)
          return 0
      else:
          print("Aucune ligne trouvée.")


def main():
  opts = argparse.ArgumentParser()

  opts.add_argument("-t", "--transport-type", "--type",
                    help="transportation type: bus, rer, tram, noctilien, metro")

  opts.add_argument("-l", "--line",
                    help="line number or name. e.g.: 72, A, T3")

  opts.add_argument("-s", "--station", "--stop",
                    help="station for which to print the next stops (optional)")

  opts.add_argument("-d", "--direction",
                    help="destination for which to print the next stops (optional)")

  opts.add_argument("-c", "--cause",
                    help="cause of the disturbance (one of: alerte, travaux, or manif)")

  opts.add_argument("-a", "--alert", action="store_true",
                    help="get alerts and transportation status (work on the line, manifestations)")

  args = opts.parse_args()

  if args.alert:
    if args.transport_type is None and args.cause is None:
      opts.print_help()
      return 1
    print(ratp.getDisturbance(args.cause, args.transport_type))
    return 0
  if args.transport_type is None:
    opts.print_help()
    return 1

  return extractInformation(args.transport_type, args.line, args.station, args.direction)

if __name__ == "__main__":
      sys.exit(main())
