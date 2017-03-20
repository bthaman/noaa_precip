<b>Overview</b>

Application that downloads NOAA hourly historical rainfall data at HRAP points, spaced 4 km over the entire U.S., and produces recurrence interval maps over specified areas.

Data downloaded from: http://www.srh.noaa.gov/data/ridge2/Precip/qpehourlyshape/

The following page gives you a general idea of the data: https://water.weather.gov/precip/download.php

<b>Prerequisites</b>

1. Python 2.7.10 w/ ArcPy installed and licensed. Python needs the following libraries:
   a. pandas
   b. numpy
   c. wget
   d. matplotlib
   e. pypyodbc
   f. sqlite3 (this may be in the standard library)

2. SDE geodatabase. I'm using SQLEXPRESS installed locally. I've also used an enterprise SQL Server database on a Fort Worth server, but the performance was terrible.

3. noaa_precip.config is used for sql server settings (connection string, table names for queries/geoprocessing), sqlite table name, download info.

4. Uses a sqlite database (precipddf.db). Don't need sqlite installed to execute the app, but will to manage the db.

<b>Modules</b>

1. precip_main.py - Main program, displays window for input of date, rainfall duration, geographic area. 
                    Outputs include csv file for each duration, and optionally a pdf map for each duration.
                    A feature class with thiessen polygons, generated from the HRAP points, is updated for each duration, but
                    is overwritten with the next duration executed.
   a. precip_dialog.py
      i.  tkSimpleDialog.py
      ii. ttkcalendar.py
         process_hourly.py
            read_config_functions.py
            precip_geoprocessing.py
            sql_wjt.py
            sqlite_wjt.py
            interpolator.py
            wget.py
         
   ddf_plot_main.py - Main program, generates depth-duration-frequency curves for the top ten counties in terms of max recurrence
                      interval within the county.
      imported custom modules:
         ddf_plot_dialog.py
         ddf_plotting.py
            file_mgmt.py
            sqlite_wjt.py
