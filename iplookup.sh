#!/bin/bash

IP=$1

mmdblookup --file /opt/homebrew/var/GeoIP/GeoLite2-City.mmdb --ip "$IP" \
| awk '
/"city"/ { in_city=1 }
/"country"/ { in_country=1 }
/"location"/ { in_location=1 }

/"en"/ && in_city {
  getline
  gsub(/^[[:space:]]*"/, "", $0)
  gsub(/"[[:space:]]*<.*>$/, "", $0)
  print "City: " $0
  in_city=0
}

/"en"/ && in_country {
  getline
  gsub(/^[[:space:]]*"/, "", $0)
  gsub(/"[[:space:]]*<.*>$/, "", $0)
  print "Country: " $0
  in_country=0
}

/latitude/ && in_location {
  getline
  gsub(/[[:space:]]*<.*>/, "", $0)
  lat=$0
}

/longitude/ && in_location {
  getline
  gsub(/[[:space:]]*<.*>/, "", $0)
  print "Coords: " lat ", " $0
  in_location=0
}'

