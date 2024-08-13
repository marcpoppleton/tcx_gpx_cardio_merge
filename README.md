# tcx_gpx_cardio_merge
A Python script to merge cardio data from a TCX file into a GPX track file

Sometimes sport watches may have GPS issues, especially in enviroments where signals can bounce around, causing location issues. A workaround is to use a smartphone to track the geolocation and then import the cardio data in the resulting track.  
Polar Flow for example allows users to export a TCX file of a workout containing the cardio data.  
This simple script inserts cardio data extracted from a TCX file into a GPX geolocation tracking file.

## Installation

1) Clone or download the repo
2) In a terminal type the following commands
```
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```


## Usage 

The script takes 2 parameters:
1) -t or --track : the name of the GPX file containing the geolocation data
2) -c or --cardio : the name of the TCX file containing the cardio data
```
$ python gpx-merge.py -t <GPX file containing track data> -c <TCX file containing cardio data>
```

## Result

The script outputs a new GPX file containing merged geolocation and cardio data. If the start and finish timestamps in both files are too far appart the script will display an error message and exit.
