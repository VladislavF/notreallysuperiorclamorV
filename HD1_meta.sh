#!/bin/bash
lasttitle=""
lastartist=""
while [ 1 ]
do
  artist=$(curl -sL https://vladfm.fomitchev.net/icecast | grep -oP '(?<=Currently playing:</td><td class="streamstats">).*?(?=<)' | awk -v b=2 -v e=2 'BEGIN{FS=OFS=" - "} {for (i=b;i<=e;i++) printf "%s%s", $i, (i<e ? OFS : ORS)}')
  
  title=$(curl -sL https://vladfm.fomitchev.net/icecast | grep -oP '(?<=Currently playing:</td><td class="streamstats">).*?(?=<)' | awk -v b=3 -v e=3 'BEGIN{FS=OFS=" - "} {for (i=b;i<=NF;i++) printf "%s%s", $i, (i<NF ? OFS : ORS)}')
  if [ "$artist" != "$lastartist" ] && [ "$title" != "$lasttitle" ]; then
    sleep 5
    echo "title${title}" | nc -q 1 localhost 52002
    echo "${title}"
    echo "artist${artist}" | nc -q 1 localhost 52002
    echo "${arist}"
  fi
  lasttitle=$title
  lastartist=$lastartist
  sleep 5
done
