# tcx_gpx_cardio_merge
A Python script to merge cardio data from a TCX file into a GPX track file

Sometimes sport watches may have GPS issues, especially in enviroments where signals can bounce around, causing location issues. A workaround is to use a smartphone to track the geolocation and then import the cardio data in the resulting track.  
Polar Flow for example allows users to export a TCX file of a workout containing the cardio data.  
This simple script inserts cardio data exctracted from a TCX file into a GPX geolocation tracking file.

## Usage 

```
gpx-merge.py -t <GPX file containing track data> -c <TCX file containing cardio data>
```
