import os
from os.path import isfile, join
import re
import wget
import tarfile
from subprocess import check_output


def download(str_year, str_month, str_day, overwrite=False):
    hours = ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
             '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')

    root = os.getcwd()
    qpe_dir = "qpehourly"
    working = root + os.sep + qpe_dir
    working_shp = working + os.sep + str_year + os.sep + str_year + str_month + os.sep + str_year + str_month + str_day
    print(working_shp)

    # if not overwriting, check to see if the data has already been downloaded: if so, get out of the main function
    data_exists = True
    if not overwrite:
        # check to see if the folder that would contain the shapefiles is there; if so,
        # check for all 24 shapefiles
        if os.path.isdir(working_shp):
            for hour in hours:
                if not (isfile(join(working_shp, hour + '.shp')) and isfile(join(working_shp, hour + '.dbf'))):
                    data_exists = False
                    break
        else:
            data_exists = False
        if data_exists:
            # not overwriting, and data is already there - return status
            return "Date already downloaded"

    os.chdir(working)

    base_link = "http://www.srh.noaa.gov/data/ridge2/Precip/qpehourlyshape/yyyy/yyyyMM/yyyyMMdd/"
    base_link = re.sub('yyyy', str_year, base_link)
    base_link = re.sub('MM', str_month, base_link)
    base_link = re.sub('dd', str_day, base_link)
    print(base_link)

    gz_file = "nws_precip_yyyyMMddhh.tar.gz"
    gz_file = re.sub('yyyyMMdd', str_year + str_month + str_day, gz_file)

    for hour in hours:
        gz = re.sub('hh', hour, gz_file)
        link = base_link + gz
        # run wget, tarfile, and command line commands
        try:
            thefile = wget.download(link)
            print(thefile)
        except Exception as e:
            print(e)
        try:
            if thefile.endswith("tar.gz"):
                tar = tarfile.open(thefile, "r")
                tar.extractall()
                tar.close()
        except Exception as e:
            print(e)
        try:
            check_output("del " + gz, shell=True).decode()
        except Exception:
            pass
        try:
            # rename shapefiles
            os.chdir(working_shp)
            shp_root = "nws_precip_" + str_year + str_month + str_day + hour
            os.rename(shp_root + '.dbf', hour + '.dbf')
            os.rename(shp_root + '.prj', hour + '.prj')
            os.rename(shp_root + '.shp', hour + '.shp')
            os.rename(shp_root + '.shx', hour + '.shx')
            os.chdir(working)
        except Exception as e:
            return e.message

    os.chdir(root)
    # copy the "all points" shapefile to the working directory. paths with spaces must be surrounded by double quotes
    # check_output('copy "' + root + os.sep + data_dir + os.sep + 'pts_cnty.*" "' + working + '"', shell=True)
    return "Data downloaded successfully"

if __name__ == "__main__":
    result = download('2016', '11', '22')
    print(result)
