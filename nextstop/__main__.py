#! /usr/bin/env python3

import argparse
import sys

from . import ratp


def extractInformation(transport,
    line,
    station, direction):
  if station is not None and station != "":
    times = ratp.getNextStopsAtStation(transport, line, station, direction)
    found = False
    for time, direction, stationname in times:
      if not found:
        found = True
        print("Prochains passages du %s ligne %s à l'arrêt %s :" %
              (transport, line, stationname))
      if direction:
        print("  —", time, "direction", direction, ";")
      else:
        print("  —", time, ";")
    if not found:
      print("La station `%s' ne semble pas exister sur le %s ligne %s."
          % (station, transport, line))

  elif line is not None:
    stations = ratp.getAllStations(transport, line)
    found = False
    for name in stations:
      if not found:
        found = True
        print("Stations :")
      print("  —", name, ";")
    if not found:
      print("Aucune station trouvée.")

  else:
    lines = ratp.getTransportLines(transport)
    found = False
    for name in lines:
      if not found:
        found = True
        print("Lignes :")
      print("  —", name, ";")
    if not found:
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
    if args.transport_type and args.line:
      d = ratp.getDisturbanceFromLine(args.transport_type, args.line)
      if "date" in d and d["date"] is not None:
        print("Au {date[date]}, {title}: {message}".format(**d))
      else:
        print("{title}: {message}".format(**d))
    elif args.transport_type is None and args.cause is None:
      opts.print_help()
      return 1
    else:
      for d in ratp.getDisturbance(args.cause, args.transport_type):
        print(d)
    return 0
  if args.transport_type is None:
    opts.print_help()
    return 1

  return extractInformation(args.transport_type, args.line, args.station, args.direction)

if __name__ == "__main__":
      sys.exit(main())
