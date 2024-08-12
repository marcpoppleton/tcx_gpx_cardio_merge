"""
File: gpx-merge.py
Author: Marc Poppleton
Date: 2024-08-09
Description: A Python script to merge cardio data from a TCX file into a GPX track file
"""

from typing import Dict, Any
from xml.etree import ElementTree

import sys, getopt
import gpxpy
import time
import lxml.etree
import dateutil.parser as dp

DELTA_THRESHOLD = 60

NAMESPACES = {
    'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
    'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
    'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
}

TCX_ROOT_NODE = 'TrainingCenterDatabase'
GPX_ROOT_NODE = 'gpx'

ACTIVITIES_NODE = 'ns:Activities'
LAP_NODE = 'ns:Lap'
TRACK_NODE = 'ns:Track'
TRACKPOINT_NODE = 'ns:Trackpoint'
TIME_NODE = 'ns:Time'
HEART_RATE_BPM_NODE = 'ns:HeartRateBpm'
VALUE_NODE = 'ns:Value'

def is_valid_tcx(filename: str) -> bool:
    tree = lxml.etree.parse(filename)
    root = lxml.etree.QName(tree.getroot()).localname
    if(root == TCX_ROOT_NODE):
        return True
    else:
        return False

def is_valid_gpx(filename: str) -> bool:
    tree = lxml.etree.parse(filename)
    root = lxml.etree.QName(tree.getroot()).localname
    if(root == GPX_ROOT_NODE):
        return True
    else:
        return False

def get_tcx_points(filename: str) -> Dict[int,int]:
    tree = lxml.etree.parse(filename)
    root = tree.getroot()

    activity = root.find(ACTIVITIES_NODE, NAMESPACES)[0]  # Assuming we know there is only one Activity in the TCX file
                                                          # (or we are only interested in the first one)
    points_data = {}

    for lap in activity.findall(LAP_NODE, NAMESPACES):
        for track in lap.findall(TRACK_NODE, NAMESPACES):
            for point in track.findall(TRACKPOINT_NODE, NAMESPACES):
                timestamp = None
                heart_rate = None
                time_str = point.find(TIME_NODE, NAMESPACES).text
                if time_str is not None:
                    timestamp = int(time.mktime(dp.parse(time_str).timetuple()))
                hr_elem = point.find(HEART_RATE_BPM_NODE, NAMESPACES)
                if hr_elem is not None:
                    heart_rate = int(hr_elem.find(VALUE_NODE, NAMESPACES).text)
                if(timestamp is not None and heart_rate is not None):
                    points_data[timestamp] = heart_rate
  
    return points_data


def get_gpx_points(filename) -> gpxpy.gpx.GPX:
    with open(filename) as f:
        gpx = gpxpy.parse(f)
        return gpx

def closest(lst:list, K:Any) -> Any:
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

def compare_points(tcx_points : Dict[int,int], gpx_points : gpxpy.gpx.GPX) -> bool:
    tcx_timestamps = list(tcx_points.keys())

    start_diff = abs(int(time.mktime(gpx_points.tracks[0].segments[0].points[0].time.timetuple())) - tcx_timestamps[0])
    end_diff = abs(int(time.mktime(gpx_points.tracks[-1].segments[-1].points[-1].time.timetuple())) - tcx_timestamps[-1])

    if(start_diff < DELTA_THRESHOLD and (end_diff < DELTA_THRESHOLD)):
        return True
    else:
        return False

def add_cardio_data(gpx : gpxpy.gpx.GPX, cardio_values : Dict[int,int]) -> gpxpy.gpx.GPX:
    for track in gpx.tracks:
        print(f"fixing cardio data for track {track.name}")
        for segment in track.segments:
            for point in segment.points:
                time_str = point.time
                timestamp = int(time.mktime(time_str.timetuple()))
                closest_timestamp = closest(list(cardio_values.keys()),timestamp)
                closest_heart_rate = cardio_values.get(closest_timestamp)
                gpx_extension_hr = ElementTree.fromstring(f"""<gpxtpx:TrackPointExtension xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"><gpxtpx:hr>{closest_heart_rate}</gpxtpx:hr></gpxtpx:TrackPointExtension>""")
                point.extensions.append(gpx_extension_hr)
        print("done")
    return gpx    

def process_file(tcx_file:str, gpx_file:str) -> None:
    
    if(is_valid_tcx(tcx_file)):
        tcx_points = get_tcx_points(tcx_file)
    else:
        print(f"{tcx_file} is not a valid TCX file")
        sys.exit()
    
    if(is_valid_gpx(gpx_file)):
        gpx_points = get_gpx_points(gpx_file)
    else:
        print(f"{gpx_file} is not a valid GPX file")
        sys.exit()

    valid = compare_points(tcx_points,gpx_points)

    if(valid):
        new_gpx = add_cardio_data(gpx_points,tcx_points)
        with open(f"{gpx_file}.new.gpx", "w") as f:
            f.write(new_gpx.to_xml())

def main(argv):
    tcx_file = ''
    gpx_file = ''
    try:
        opts, args = getopt.getopt(argv,"ht:c:",["track=","cardio="])
    except getopt.GetoptError:
        print ('gpx-merge.py -t <GPX file containing track data> -c <TCX file containing cardio data>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('gpx-merge.py -t <GPX file containing track data> -c <TCX file containing cardio data>')
            sys.exit()
        elif opt in ("-t", "--track"):
            gpx_file = arg
        elif opt in ("-c", "--cardio"):
            tcx_file = arg
    process_file(tcx_file,gpx_file)


if __name__ == '__main__':
    main(sys.argv[1:])


