"""
 bill thaman: 11/11/2016
 last update: 3/17/2017
 processes hourly rainfall data once the data has been downloaded and unzipped to shapefiles
   - PrecipProcessor class has functions to:
       - clip shapefiles to texas and output to SDE
       - join sde feature class table of all hrap points with hourly tables. outputs pandas dataframe of hourly values
   - main method takes a rainfall duration value (3hr, 6hr, 12hr, 24hr):
       - optionally clip shapefiles and move to sde using PrecipProcessor object
       - updates hourly values and gets a pandas dataframe using PrecipProcessor object
       - add/populate 'sliding window' columns to df; number of new columns corresponds to input rainfall duration
       - uses sqlite to build a pandas dataframe of depth-duration-frequency values for all hrap points in texas
       - determine most intense rainfall period by ?using the average depths within each county?
       - calculate, for each county (could be other area e.g. basin), the exceedance probability and return period,
         based on the most intense period. update the dataframe for each rainfall point.
"""
import pandas as pd
import numpy as np
from precip_geoprocessing import *
import pypyodbc
import sqlite_wjt
import sql_wjt
import interpolator
import read_config_functions as rcf
import wgetpy
import dateutil.parser as parser
import sys


class PrecipProcessor:
    # class variable which should be set to True if user selected "all" durations
    process_all_durations = False

    def __init__(self, precip_date):
        self.precip_date = precip_date
        self.year = parser.parse(precip_date).year
        self.month = parser.parse(precip_date).month
        self.day = parser.parse(precip_date).day
        self.root = os.getcwd()
        self.dictSettings = rcf.configsectionmap('noaa_precip.config', 'noaa_precip')
        self.qpe_dir = 'qpehourly'
        self.sql_cnn_string = self.dictSettings['cnn_string']
        self.update_table = self.dictSettings['update_table']
        self.hrap_val_table = self.dictSettings['hrap_val_table']
        self.depth_table_prefix = self.dictSettings['depth_table_prefix']
        self.dataframe = None
        self.dataframe_ddf = None
        self.out_raster = None
        self.hours = ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                      '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')
        self.str_year = str(self.year)
        self.str_month = str(self.month)
        self.str_day = str(self.day)
        if len(self.str_month) == 1:
            self.str_month = '0' + self.str_month
        if len(self.str_day) == 1:
            self.str_day = '0' + self.str_day

    def process_points(self, duration_hrs, map_area='texas', export_maps=True, show_maps=True, create_raster=True):
        # attempt to download the shapefiles: if they are already downloaded, they will not be downloaded again
        str_year = self.str_year
        str_month = self.str_month
        str_day = self.str_day
        duration_hrs = int(duration_hrs)

        if len(str_month) == 1:
            str_month = '0' + str_month
        if len(str_day) == 1:
            str_day = '0' + str_day
        download_status = wgetpy.download(str_year, str_month, str_day, overwrite=False)
        print('Download status: ' + download_status)

        if not PrecipProcessor.process_all_durations or (PrecipProcessor.process_all_durations and duration_hrs == 1):
            # clip shapefiles will only be run once if processing all durations
            self.clip_shapefiles()
            # feature class to feature class will only be run once if processing all durations
            # self.fc_to_fc()
        self.update_all_pts()
        df = self.get_dataframe()

        # create dictionary mapping duration_hrs to all_pts and ddf field names
        dict_dur = {1: ['Dur_1hr', 'd_1hr'], 3: ['Dur_3hr', 'd_3hr'], 6: ['Dur_6h', 'd_6hr'],
                    12: ['Dur_12hr', 'd_12hr'], 24: ['Dur_24hr', 'd_24hr']}
        if duration_hrs in dict_dur:
            ddf_field = dict_dur[duration_hrs][1]
        else:
            # need to add error handling for a value error
            print("Value Error")

        print('make ddf dataframe...')
        sqlitewjt = sqlite_wjt.SQLiteWJT(self.dictSettings['precip_db'])
        sql = "select cast(hrapx as string) || '_' || cast(hrapy as string) as hrap_id, prob, " + ddf_field + \
              " from ddf"
        df_ddf = sqlitewjt.get_dataframe(sql)
        df_ddf = df_ddf.set_index('hrap_id')
        sqlitewjt.close_connection()

        # create new duration columns
        print('make new columns...')
        new_cols = []
        num_new_columns = 24 - duration_hrs + 1
        for i in range(num_new_columns):
            new_cols.append('win_' + str(i + 1))

        # add the new columns to the df and populate
        for i, c in enumerate(new_cols):
            # create and initialize the new column
            df[c] = 0
            # populate new column by adding up hourly values
            for j in range(duration_hrs):
                df[c] += df.ix[:, i + j + 3]

        # create a new column containing the max value from the 'win_' columns,
        # and a column to hold the interpolated probs
        df['max_win_pt'] = df[new_cols].max(axis=1)
        df['return_period'] = 0

        # aggregate on county to get the mean rainfall
        print('export stats to csv...')
        # create a pivot table dataframe: get statistics by county and moving window columns
        # 'aggfunc' can take a list of statistical functions
        df_stats = pd.pivot_table(df, index=['county'], values=new_cols, aggfunc=[np.mean])
        df_stats.to_csv('output\\df_stats_interim.csv')
        # add a new column containing the name of the column with the max value for each county
        # problematic--->df_stats['Max'] = df_stats.ix[:, 3:num_new_columns + 3].idxmax(axis=1)
        df_stats['Max'] = df_stats.ix[:, 0:num_new_columns].idxmax(axis=1)
        # get a series of tuples containing the statistic name and the name of the column containing the max value,
        # e.g. ('mean', 'win_2')
        series_maxcols = df_stats[:]['Max']

        # iterate over the df and find the probability for each point
        print('interpolating...')
        # either get max by point or max average in county
        by_pt_or_area = 'by_point'

        interp = interpolator.Interpolator()
        sqlwjt = sql_wjt.SqlWjt(self.sql_cnn_string)
        # 'max_win_pt' contains the highest window value for the individual point
        max_win_pt_index = df.columns.get_loc('max_win_pt')
        i = 0
        for row in df.iterrows():
            hrap_id = str(row[0])
            hrapx = str(row[1][0])
            hrapy = str(row[1][1])
            county = str(row[1][2])

            # 'series_maxcols' contains, for each county, a tuple ('mean', 'column name'),
            # get the column name for the county's tuple
            if county in series_maxcols.index:
                max_col_name = series_maxcols[county][1]
            else:
                # need to catch an error here
                print('error')
            # get the column index corresponding to the column containing the maximum means for the current county
            max_col_index = df.columns.get_loc(max_col_name)
            # get the depth value in the column
            if by_pt_or_area == 'by_point':
                max_win = row[1][max_win_pt_index]
            else:
                max_win = row[1][max_col_index]
            rp = 0.0
            prob = 1.0
            # be sure the point has ddf values, and has rain; if so, interpolate for probability
            if max_win > 0 and hrap_id in df_ddf.index:
                i += 1
                # filter ddf values into a new df
                dfiter = df_ddf.ix[str(row[0])]
                # check is less than minimum, or gt maximum; if not, interpolate
                if max_win < dfiter.ix[0, ddf_field]:
                    # some rainfall, but less than a 2-yr
                    rp = 1
                elif max_win > dfiter.ix[len(dfiter) - 1, ddf_field]:
                    prob = dfiter.ix[len(dfiter) - 1, 'prob']
                    # add 1 to return period to indicate that depth is beyond the maximum (e.g. 500 yr)
                    rp = 1. / prob + 1
                else:
                    for r in range(len(dfiter) - 1):
                        if dfiter.ix[r, ddf_field] <= max_win < dfiter.ix[r + 1, ddf_field]:
                            prob = interp.interpolate(max_win, dfiter.ix[r, ddf_field], dfiter.ix[r + 1, ddf_field],
                                                      dfiter.ix[r, 'prob'], dfiter.ix[r + 1, 'prob'])
                            rp = 1. / prob
                # update the primary dataframe
                df.ix[hrap_id, 'return_period'] = rp
                # insert results into a table with only 3 fields.
                # combined with a table join at the end, this is ~10X faster than updating all_pts directly
                sql = 'insert into ' + self.hrap_val_table + ' values (' + hrapx + ',' + hrapy + ',' + str(rp) + ')'
                sqlwjt.update_table(sql, commit=False)
                if i % 100 == 0:
                    sqlwjt.commit_update()

        # update sql server fc
        sql = 'update a set a.globvalue = b.val from ' + self.update_table + ' a inner join ' + \
              self.hrap_val_table + ' b ' \
              'on a.hrapx = b.hrapx and a.hrapy = b.hrapy'
        sqlwjt.update_table(sql, commit=True)
        sqlwjt.close_cnn()

        # create new df w/ subset of columns and write df to csv
        dfsubset = df[['hrapx', 'hrapy', 'county', 'max_win_pt', 'return_period']]
        dfsubset.to_csv('output\\' + str_year + str_month + str_day + '_' + str(duration_hrs) + '.csv')

        if create_raster:
            # create raster
            print('creating raster...')
            self.create_raster('allpts_raster')
            out_raster = 'raster_' + str_year + str_month + str_day + '_' + str(duration_hrs) + 'hr'
            self.create_raster(out_raster)

        # export pdf
        if export_maps:
            print('exporting pdf...')
            pdf = PdfCreator()
            pdf_name = str_year + str_month + str_day + '_' + str(duration_hrs) + 'hr'
            status = pdf.export_pdf(map_area, pdf_name=pdf_name,
                                    legend_title=str(self.precip_date) + ': ' + str(duration_hrs) + ' hr')
            print(status)
            pdf_file = os.path.join(os.getcwd(), pdf_name + '.pdf')
            if show_maps:
                os.startfile(pdf_file)

        # create a Pandas Excel writer using XlsxWriter as the engine.
        """        print('writing df to excel...')
                xlsfile = 'df_out.xlsx'
                writer = pd.ExcelWriter(xlsfile, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='ddf_out')
                # close the Pandas Excel writer and output the Excel file.
                writer.save()
        """

    def get_hrs(self):
        return self.hours

    def get_dataframe(self):
        return self.dataframe

    def clip_shapefiles(self):
        arcpy.env.workspace = self.dictSettings['arcpy_workspace']
        working = self.root + os.sep + self.qpe_dir
        working_shp = working + os.sep + self.str_year + os.sep + self.str_year + self.str_month + os.sep + \
            self.str_year + self.str_month + self.str_day
        os.chdir(working_shp)

        gpt = GPtools()
        clip_boundary = self.dictSettings['clip_boundary']

        for hour in self.hours:
            inFeatures = os.getcwd() + os.sep + hour + '.shp'
            # outFC = "Database Servers\\FN27399_SQLEXPRESS.gds\\HCFCD (VERSION:dbo.DEFAULT)\\HCFCD.DBO." + \
            #         "FC_" + self.str_year + self.str_month + self.str_day + hour

            outFC = "FC_" + self.str_year + self.str_month + self.str_day + hour
            if not arcpy.Exists(outFC):
                run_status = gpt.clip_to_boundary(in_features=inFeatures, clip_boundary=clip_boundary,
                                                  out_features=outFC)
                print(outFC + ': ' + str(run_status))
            else:
                print(outFC + ' exists')
                os.chdir(self.root)
                return None
        os.chdir(self.root)

    def fc_to_fc(self):
        arcpy.env.workspace = self.dictSettings['arcpy_workspace']
        working = self.root + os.sep + self.qpe_dir
        working_shp = working + os.sep + self.str_year + os.sep + self.str_year + self.str_month + os.sep + \
            self.str_year + self.str_month + self.str_day
        os.chdir(working_shp)

        gpt = GPtools()

        for hour in self.hours:
            inFeatures = os.getcwd() + os.sep + hour + '.shp'
            outFC = "FC_" + self.str_year + self.str_month + self.str_day + hour

            if not arcpy.Exists(outFC):
                run_status = gpt.featureclass_to_featureclass(in_features=inFeatures, out_path=arcpy.env.workspace,
                                                              out_features=outFC)
                print(outFC + ': ' + str(run_status))
            else:
                print(outFC + ' exists')
                return None
        os.chdir(self.root)

    def update_all_pts(self):
        conn = pypyodbc.connect(self.sql_cnn_string)
        cursor = conn.cursor()
        hrs = self.hours

        print("initializing hourly values...")
        sql = "update " + self.update_table + " set hr_00=0, hr_01=0, hr_02=0, hr_03=0, hr_04=0, hr_05=0, " \
              "hr_06=0, hr_07=0, " \
              "hr_08=0, hr_09=0, hr_10=0, hr_11=0, hr_12=0, hr_13=0, hr_14=0, hr_15=0, " \
              "hr_16=0, hr_17=0, hr_18=0, hr_19=0, hr_20=0, hr_21=0, hr_22=0, hr_23=0, " \
              "Dur_3hr=0, Dur_6h=0, Dur_12hr=0, Dur_24hr=0, globvalue=0"
        cursor.execute(sql)
        conn.commit()

        sql = 'delete from ' + self.hrap_val_table
        cursor.execute(sql)
        conn.commit()

        # update sql all points table with hourly values
        for i, hr in enumerate(hrs):
            print(i)
            depth_table = self.depth_table_prefix + self.str_year + self.str_month + self.str_day + hr
            update_fld = "Hr_" + hr
            sql = "update a " \
                  " set a." + update_fld + " = b.globvalue " \
                  "from " + self.update_table + " a " \
                  "inner join " + depth_table + " b " \
                  "on a.HRAPX = b.HRAPX and a.HRAPY = b.HRAPY"

            cursor.execute(sql)
        conn.commit()

        sql = "select cast(hrapx as nvarchar(10)) + '_' + cast(hrapy as nvarchar(10)) as hrap_id, " \
              "hrapx, hrapy, name10 as county, hr_00, hr_01, hr_02, hr_03, hr_04, hr_05, hr_06, hr_07, hr_08, " \
              "hr_09, hr_10, hr_11, hr_12, hr_13, hr_14, hr_15, hr_16, hr_17, hr_18, hr_19, " \
              "hr_20, hr_21, hr_22, hr_23 from " + self.update_table + " where name10 is not null and name10 <> ''"
        print('make df containing all points...')
        df = pd.read_sql(sql, conn)
        df2 = df.set_index('hrap_id')
        self.dataframe = df2
        conn.close()

    def create_raster(self, out_raster):
        pg = GPtools()
        in_features = self.dictSettings['in_features']
        # in_features = 'Database Connections\\sde_wjt@sde_wjt@fwsde.sde\\sde_wjt.SDE_WJT.hrap\\all_pts'
        val_field = 'globvalue'
        pg.point_to_raster(in_features, out_raster, val_field)

    @staticmethod
    def delete_fc(infc):
        arcpy.Delete_management(infc)


if __name__ == "__main__":
    pp = PrecipProcessor(sys.argv[1])
    pp.process_points(duration_hrs=sys.argv[2], map_area=sys.argv[3], export_maps=sys.argv[4],
                      show_maps=sys.argv[5], create_raster=sys.argv[6])
