from os import listdir
from os.path import isfile, join
import re
import os


def list_files(loc):
    return [f for f in listdir(loc) if isfile(join(loc, f))]


def csv_precip_list(loc=os.getcwd()):
    lst_dates = []
    lst_duration = ['1', '3', '6', '12', '24']
    file_list = list_files(loc)
    for f in sorted(file_list):
        # check is the file name matches the format of a file with duration = 1
        m = re.match('^(\d{8})_1\.csv$', f)
        # if it matches, check to see if all the other durations are there; if so, add the date to lst_dates
        if m:
            # build list of a all files that would need to exist before the date is added to lst_dates
            files = [join(loc, m.group(1) + '_' + d + '.csv') for d in lst_duration]
            # check to see if all files that would need to be there are actually there using isfile()
            # 'files' is empty if any file is not there (i.e. isfile() is False)
            files = files if all(x for x in [isfile(ff) for ff in files]) else []
            if files:
                lst_dates.append(m.group(1)[4:6] + '/' + m.group(1)[6:8] + '/' + m.group(1)[:4])
    return lst_dates

if __name__ == "__main__":
    lstdts = csv_precip_list()
    print(lstdts)
