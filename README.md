<b>Overview</b>

Application that downloads NOAA hourly historical rainfall data at HRAP points, spaced 4 km over the entire U.S., and produces recurrence interval maps over specified areas.

Data downloaded from: http://www.srh.noaa.gov/data/ridge2/Precip/qpehourlyshape/

The following page gives you a general idea of the data: https://water.weather.gov/precip/download.php

<b>Prerequisites</b>

1. Python 2.7.10 w/ ArcPy installed and licensed. Python needs the following libraries that are not in the standard library:
   * pandas
   * numpy
   * wget
   * matplotlib
   * pypyodbc

2. SDE geodatabase. I'm using SQLEXPRESS installed locally. I've also used an enterprise SQL Server database on a Fort Worth server, but the performance was terrible.

3. noaa_precip.config must be populated with current sql server settings (connection string, table names for queries/geoprocessing), sqlite table name, and download info.

4. Uses a sqlite database (precipddf.db). Don't need sqlite installed to execute the app, but will to manage the db, if necessary.

<b>Analysis Modules</b>

1.  <b>precip_main.py</b> - Main program, displays window for input of date, rainfall duration, geographic area. Outputs include csv file for each duration, and optionally a pdf map for each duration. A feature class with thiessen polygons, generated from the HRAP points, is updated for each duration, but is overwritten with the next duration executed. 
2.  precip_dialog.py - imported into precip_main
3.  tkSimpleDialog.py - imported into precip_dialog
4.  ttkcalendar.py - imported into precip_dialog
5.  process_hourly.py - imported into precip_main
6.  read_config_functions.py - imported into precip_hourly
7.  precip_geoprocessing.py - imported into precip_hourly
8.  sql_wjt.py - imported into precip_hourly
9.  sqlite_wjt.py - imported into precip_hourly
10. interpolator.py - imported into precip_hourly
11. wget.py - imported into precip_hourly
         
<b>DDF Plotting Modules</b>
   
1. <b>ddf_plot_main.py</b> - Main program, generates depth-duration-frequency curves for the top ten counties in terms of max recurrence interval within the county.
2. ddf_plot_dialog.py
3. ddf_plotting.py
4. file_mgmt.py
5. sqlite_wjt.py
