#!/usr/bin/python
import json as j
import xml.etree.ElementTree as e
import datetime

def json_to_gpx_trackpoints(a_json_file_name, a_gpx_file_name):
    with open(a_json_file_name) as json_format_file:
        d = j.load(json_format_file)

    r = e.Element("gpx")

    track = e.SubElement(r,"trk")
    e.SubElement(track,"Name").text = d["uuid"]

    trackseg = e.SubElement(track,"trkseg")

    for coordinate in d["coordinates"]:
      trackpoint =  e.SubElement(trackseg,'trkpt', attrib={'lat':str(coordinate["lat"]),'lon':str(coordinate["lng"])})
      e.SubElement(trackpoint,"ele").text = str(coordinate["alt"])
      e.SubElement(trackpoint,"time").text = "{}Z".format(datetime.datetime.utcfromtimestamp(coordinate["at"]/1000).replace(microsecond=0).isoformat() )

    a = e.ElementTree(r)
    a.write(a_gpx_file_name)

def json_to_gpx_waypoints(a_json_file_name, a_gpx_file_name):
    with open(a_json_file_name) as json_format_file:
        d = j.load(json_format_file)

    r = e.Element("gpx")

    for coordinate in d["coordinates"]:
      waypoint =  e.SubElement(r,'wpt', attrib={'lat':str(coordinate["lat"]),'lon':str(coordinate["lng"])})
      e.SubElement(waypoint,"ele").text = str(coordinate["alt"])
      e.SubElement(waypoint,"time").text = "{}Z".format(datetime.datetime.utcfromtimestamp(coordinate["at"]/1000).replace(microsecond=0).isoformat() )

    a = e.ElementTree(r)
    a.write(a_gpx_file_name) 
 