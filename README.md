# NextStop

## Description
  This is a small python tool to check for the next bus/tram/rer/noctilien
  stops at a desired stop dedicated to the French transportation system.

## Usage
./src/nextstop.py -t transport_type -l line [-s station]

./src/nextstop.py -a -t transport_type -c cause

* -h: Display this help
* -t transport_type: transportation type: bus, rer, tram, noctilien, metro
* -l line: line number or name. e.g.: 72, A, T3
* -s station: optionnal: station for which to print the next stops
* -c cause: cause of the disturbance (alerte, travaux, or manif)
* -a: get alerts and transportation status (work on the line, manifestations)
