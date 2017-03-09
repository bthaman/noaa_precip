import os
from os.path import isfile, join
import re
import wget
import tarfile
from shutil import move


def download(str_year, str_month, str_day):
    layer_name = "1dobs"
    root = os.getcwd()
    daily_dir = "qpedaily"
    working = join(root, daily_dir)
    if not os.path.isdir(working):
        os.makedirs(working)
    working_shp = join(working, str_year + str_month + str_day)

    # if not overwriting, check to see if the data has already been downloaded: if so, get out of the main function
    data_exists = True

    # check to see if the folder that would contain the shapefiles is there
    if os.path.isdir(working_shp):
        if not (isfile(join(working_shp, layer_name + '.shp')) and isfile(join(working_shp, layer_name + '.dbf'))):
            data_exists = False
    else:
        data_exists = False
    if data_exists:
        # data is already there - return status
        return "Date already downloaded"

    os.chdir(working)

    if not os.path.isdir(working_shp):
        os.makedirs(working_shp)

    base_link = "http://www.water.weather.gov/precip/p_download_new/yyyy/MM/dd/"
    base_link = re.sub('yyyy', str_year, base_link)
    base_link = re.sub('MM', str_month, base_link)
    base_link = re.sub('dd', str_day, base_link)

    gz_file = "nws_precip_1day_observed_shape_yyyyMMdd.tar.gz"
    gz_file = re.sub('yyyyMMdd', str_year + str_month + str_day, gz_file)

    link = base_link + gz_file
    print link
    try:
        thefile = wget.download(link)
        move(thefile, working_shp)
        print(thefile)
    except Exception as e:
        print(e)
    try:
        os.chdir(working_shp)
        if thefile.endswith("tar.gz"):
            tar = tarfile.open(thefile, "r")
            tar.extractall()
            tar.close()
    except Exception as e:
        print(e)
    try:
        os.remove(gz_file)
    except Exception:
        pass
    try:
        # rename shapefiles
        os.chdir(working_shp)
        shp_root = "nws_precip_1day_observed_" + str_year + str_month + str_day
        os.rename(shp_root + '.dbf', layer_name + '.dbf')
        os.rename(shp_root + '.prj', layer_name + '.prj')
        os.rename(shp_root + '.shp', layer_name + '.shp')
        os.rename(shp_root + '.shx', layer_name + '.shx')
        os.chdir(working)
    except Exception as e:
        return e.message

    os.chdir(root)
    return "Data downloaded successfully"

if __name__ == "__main__":
    result = download('2016', '11', '25')
    print(result)
