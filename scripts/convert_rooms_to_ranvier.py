#!/usr/bin/python

from os import listdir, getcwd
from os.path import isfile, join
from sys import exit, version
from collections import OrderedDict
from itertools import groupby
import yaml

directions = {
    'N':    'north',
    'E':    'east',
    'S':    'south',
    'W':    'west',
    'U':    'up',
    'D':    'down' 
}

def setup_yaml():
  """ https://stackoverflow.com/a/8661021 """
  represent_dict_order = lambda self, data:  self.represent_mapping('tag:yaml.org,2002:map', data.items())
  yaml.add_representer(OrderedDict, represent_dict_order)   

setup_yaml()

room_list = list()

room_path = "../bbc/R"
only_files = [f for f in listdir(room_path) if isfile(join(room_path, f))]
rooms = sorted(only_files, key=int) 

for room in rooms:
    #print "Room: " + room
    bytes_read = open(room_path + "/" + room, 'rb').read()
    
    # Process exits.
    string_idx = 0
    exit_string = ''
    room_string = ''

    while (1):
        character = bytes_read[string_idx]
        #print "next: " + character + "  q  " + str(ord(character))

        if ord(character) == 13:
            break

        exit_string = exit_string + character
        string_idx=string_idx+1

    #print "Exit String: " + exit_string

    string_idx = 64

    while (1):
        character = bytes_read[string_idx]
        print str(string_idx) + " - next: " + character + "  q  " + str(ord(character))

        if ord(character) == 13:
            break
        
        # Replace BBC colour control characters with spaces.
        if ord(character) >= 129:
            character = ' '

        if not (ord(character) == 32 and ord( bytes_read[string_idx-1]) == 32):
            room_string = room_string + character

        string_idx=string_idx +1

    print "Room " + room + " string: " + room_string

    room_dict = OrderedDict()
    room_dict['id'] = room
    room_dict['title'] = 'Undefined'
    room_dict['description'] = room_string

    parsed_room_list = ["".join(x) for _, x in groupby(exit_string, key=str.isdigit)]

    parsed_room_list = iter(parsed_room_list)
    
    room_exists_list = list()

    for x, y in zip(parsed_room_list, parsed_room_list):
        print x, y

        if x == 'Q':
            continue

        room_exists_dict = OrderedDict()
        room_exists_dict['roomId'] = 'cave:' + y
        room_exists_dict['direction'] = directions[x]
        room_exists_list.append(room_exists_dict)

    room_dict['exits'] = room_exists_list

    room_list.append(room_dict)

with open('rooms.yml', 'w') as outfile:
    yaml.dump(room_list, outfile, default_flow_style=False)
