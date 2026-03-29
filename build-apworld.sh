#!/bin/sh

GAMENAME=$(jq -r '.game' src/data/game.json)
AUTHOR=$(jq -r '.creator' src/data/game.json)

BASENAME=manual_${GAMENAME}_${AUTHOR}

rm ${BASENAME}
rm ${BASENAME}.apworld

ln -s src ${BASENAME}

7z a -tzip ${BASENAME}.apworld ${BASENAME}

rm ${BASENAME}

