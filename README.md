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

3. Uses a sqlite database. Don't need sqlite installed to execute the app, but will to manage the db.

<b>Modules</b>


