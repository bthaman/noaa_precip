import sqlite_wjt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pylab as plb
import dateutil.parser as parser
import os
from os.path import isfile, join
import sys
import file_mgmt as fm


class DDFplotting:
    def __init__(self, precip_date):
        self.precip_date = precip_date
        self.year = parser.parse(precip_date).year
        self.month = parser.parse(precip_date).month
        self.day = parser.parse(precip_date).day
        self.str_year = str(self.year)
        self.str_month = str(self.month)
        self.str_day = str(self.day)
        if len(self.str_month) == 1:
            self.str_month = '0' + self.str_month
        if len(self.str_day) == 1:
            self.str_day = '0' + self.str_day
        self.root = os.path.join(os.getcwd(), 'output')
        self.hrapx = None
        self.hrapy = None
        self.csv_files = None
        self.plt = None
        self.lst_hrs = [1, 3, 6, 12, 24]
        self.str_hrs = ['01', '03', '06', '12', '24']
        self.lst_rp = [2, 5, 10, 25, 50, 100, 250, 500]
        self.lst_legend = [str(x) + '-yr' for x in self.lst_rp]
        self.lst_legend_reversed = list(reversed(self.lst_legend))

    def plot_ddf(self, hrapx, hrapy):
        self.hrapx = hrapx
        self.hrapy = hrapy

        sqlitewjt = sqlite_wjt.SQLiteWJT('precipddf.db')
        sql = "select 1/prob as rp, d_1hr, d_3hr, d_6hr, d_12hr, d_24hr" \
              " from ddf where hrapx=" + str(hrapx) + " and hrapy=" + str(hrapy)
        df = sqlitewjt.get_dataframe(sql)
        sqlitewjt.close_connection()
        dft = df.T

        # add the lines in reverse order: 500, 250, 100, etc.
        for col in range(dft.shape[1] - 1, -1, -1):
            if dft[:1][col].values[0] in self.lst_rp:
                plt.plot(self.lst_hrs, dft[1:][col].values)
        plt.xticks(self.lst_hrs)
        plt.xlim(xmin=1)
        plt.xlim(xmax=24)
        plt.ylim(ymax=plt.ylim()[1]+7)
        plt.grid(b=True, which='both')
        plt.xlabel('Duration (hrs)', fontsize='medium')
        plt.ylabel('Depth (in)', fontsize='medium')
        # plt.xscale('log')
        self.plt = plt

    def plot_precip_date_ddf(self):
        # the df from read_precip has three rows representing the counties w/ the three highest return periods
        dftop = self.read_precip()
        print(dftop.T)
        # transposing puts the counties as columns, and:
        #  * first two rows is hrapx, hrapy
        #  * next five rows are the depths for 1hr, 3hr, 6hr, 12hr, 24hr
        df_hrap = dftop.T.ix[:2]
        df_depths = dftop.T.ix[2:7]
        for i, col in enumerate(df_depths.columns.values):
            # get county name
            county = col
            # get lists of hrap and depths
            lst_hrap = df_hrap.iloc[:, i].tolist()
            lst_depths = df_depths.iloc[:, i].tolist()
            # get hrap coordinates
            hrapx = lst_hrap[0]
            hrapy = lst_hrap[1]
            # get the basic ddf plot for the hrap coordinates
            self.plot_ddf(hrapx, hrapy)
            # add plot for hrap depths
            print(self.lst_hrs)
            print(lst_depths)
            self.plt.plot(self.lst_hrs, lst_depths, 'r--D', linewidth=3.0, markersize=9)
            self.plt.legend(self.lst_legend_reversed + [self.precip_date], loc='upper left', fontsize='small')
            self.plt.title(county + ' (' + str(int(hrapx)) + ', ' + str(int(hrapy)) + ')', fontsize='large')
            plb.savefig('output\\' + county + '_' + self.str_year + self.str_month +
                        self.str_day + '.png', bbox_inches='tight')
            self.plt.show()

    def csv_file_list(self):
        file_root = self.str_year + self.str_month + self.str_day + '_'
        files = [join(self.root, file_root + str(h) + '.csv') for h in self.lst_hrs]
        files = files if all(x for x in [isfile(f) for f in files]) else []
        return files

    def read_precip(self):
        self.csv_files = self.csv_file_list()
        if self.csv_files:
            dict_files = dict(zip(self.str_hrs, self.csv_files))
            lst_df = [pd.read_csv(dict_files[hr]).set_index('hrap_id') for hr in self.str_hrs]
            dict_df = dict(zip(self.str_hrs, lst_df))
            for hr in self.str_hrs:
                dict_df[hr].columns = ['hrapx', 'hrapy', 'county', 'max_' + hr, 'rp_' + hr]
                # print(dict_df[hr].head())
            # merge all df's
            dfmerge = dict_df['01'].merge(dict_df['03']).merge(dict_df['06']).merge(dict_df['12']).merge(dict_df['24'])
            print(dfmerge.head())
            # final df has all depth and return period columns
            depth_col_names = ['max_' + hr for hr in self.str_hrs]
            rp_col_names = ['rp_' + hr for hr in self.str_hrs]
            df = dfmerge[['county', 'hrapx', 'hrapy'] + depth_col_names + rp_col_names]
            df['max_rp'] = df[rp_col_names].max(axis=1)
            df_max = df.sort('max_rp', ascending=False).groupby('county', as_index=False).first()
            df_max = df_max.sort('max_rp', ascending=False).set_index('county')
            # return the top five rows
            df_top3 = df_max[:][:10]
            return df_top3
        else:
            print('no files')
            return None


if __name__ == "__main__":
    dt_list = fm.csv_precip_list(os.getcwd())
    print(dt_list)
    print(sys.argv[1])
    if sys.argv[1] in dt_list:
        ddfp = DDFplotting(sys.argv[1])
        ddfp.plot_precip_date_ddf()
    else:
        print("Data for this date does not exist.")

