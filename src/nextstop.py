#! /usr/bin/python3

import getopt
import sys
import ratp


def printUsage(name):
  print("Usage: %s -t transport_type -l line [-s station] " % name)
  print("\t-t transport_type: transportation type: bus, rer, tram, "
      + "noctilien, metro")
  print("\t-l line: line number or name. e.g.: 72, A, T3")
  print("\t-s station: optionnal: station for which to print the next stops")

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

  return ratp.extractInformation(type_transp, line, station)

if __name__ == "__main__":
      sys.exit(main())
