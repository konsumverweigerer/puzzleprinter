#!/bin/sh

VERTICALPIC="s3://puzzle-live/puzzle/images/print/puzzle_01010101-0101-0101-0101010101010101.jpg"
HORIZONTALPIC="s3://puzzle-live/puzzle/images/print/puzzle_01010101-0101-0101-0101010101010100.jpg"
DEBUG=1

if [ "$DEBUG" = "1" ]; then
        ./printpuzzle.py -o1334334 -p17676766 -d/tmp/ -s200 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#333333" -q
        ./printpuzzle.py -o1334331 -p17676761 -d/tmp/ -s200 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#333333" -q
        ./printpuzzle.py -o5434334 -p57676766 -d/tmp/ -s500 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#FF8E1D" -q
        ./printpuzzle.py -o5434331 -p57676761 -d/tmp/ -s500 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#FF8E1D" -q
        ./printpuzzle.py -o9334334 -p07676766 -d/tmp/ -s1000 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#003E6F" -q
        ./printpuzzle.py -o9334331 -p07676761 -d/tmp/ -s1000 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#003E6F" -q
else
        ./printpuzzle.py -o1434334 -p17676766 -d/tmp/ -s200 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#333333"
        ./printpuzzle.py -o1434331 -p17676761 -d/tmp/ -s200 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#333333"
        ./printpuzzle.py -o9434334 -p07676766 -d/tmp/ -s1000 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#003E6F"
        ./printpuzzle.py -o9434331 -p07676761 -d/tmp/ -s1000 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#003E6F"
        ./printpuzzle.py -o2434334 -p27676766 -d/tmp/ -s200 --image="${HORIZONTALPIC}" -h --title="1 äußerst schönes Puzzle" --color="#FFFFFF"
        ./printpuzzle.py -o2434331 -p27676761 -d/tmp/ -s200 --image="${VERTICALPIC}" -v --title="1 äußerst schönes Puzzle" --color="#FFFFFF"
        ./printpuzzle.py -o3434334 -p37676766 -d/tmp/ -s200 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#7D0E19"
        ./printpuzzle.py -o3434331 -p37676761 -d/tmp/ -s200 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#7D0E19"
        ./printpuzzle.py -o4434334 -p47676766 -d/tmp/ -s200 --image="${HORIZONTALPIC}" -h --title="1 äußerst schönes Puzzle" --color="#DD5B78"
        ./printpuzzle.py -o4434331 -p47676761 -d/tmp/ -s200 --image="${VERTICALPIC}" -v --title="1 äußerst schönes Puzzle" --color="#DD5B78"
        ./printpuzzle.py -o5434334 -p57676766 -d/tmp/ -s500 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#FF8E1D"
        ./printpuzzle.py -o5434331 -p57676761 -d/tmp/ -s500 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#FF8E1D"
        ./printpuzzle.py -o7434334 -p87676766 -d/tmp/ -s500 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#91B329"
        ./printpuzzle.py -o6434331 -p77676761 -d/tmp/ -s500 --image="${VERTICALPIC}" -v --title="1 äußerst schönes Puzzle" --color="#FFFF00"
        ./printpuzzle.py -o8434334 -p97676766 -d/tmp/ -s500 --image="${HORIZONTALPIC}" -h --title="1 äußerst schönes Puzzle" --color="#1B8B34"
        ./printpuzzle.py -o8434331 -p97676761 -d/tmp/ -s500 --image="${VERTICALPIC}" -v --title="1 äußerst schönes Puzzle" --color="#1B8B34"
        ./printpuzzle.py -o0434334 -p61676766 -d/tmp/ -s1000 --image="${HORIZONTALPIC}" -h --title="1 äußerst schönes Puzzle" --color="#2DC0C8"
        ./printpuzzle.py -o0434331 -p61676761 -d/tmp/ -s1000 --image="${VERTICALPIC}" -v --title="1 äußerst schönes Puzzle" --color="#2DC0C8"
        ./printpuzzle.py -o3134334 -p62676766 -d/tmp/ -s1000 --image="${HORIZONTALPIC}" -h --title="Ein äußerst schönes Puzzle" --color="#333333"
        ./printpuzzle.py -o3134331 -p62676761 -d/tmp/ -s1000 --image="${VERTICALPIC}" -v --title="Ein äußerst schönes Puzzle" --color="#333333"
        ./printpuzzle.py -o3234334 -p63676766 -d/tmp/ -s1000 --image="${HORIZONTALPIC}" -h --title="1 äußerst schönes Puzzle" --color="#FFFFFF"
        ./printpuzzle.py -o3234331 -p63676761 -d/tmp/ -s1000 --image="${VERTICALPIC}" -v --title="1 äußerst schönes Puzzle" --color="#FFFFFF"
fi
