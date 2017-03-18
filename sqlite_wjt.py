"""
 class to read from sqlite database
 last update: 3/17/2017
"""

import sqlite3
import os
import time
import pandas as pd
import matplotlib.pyplot as plt


class SQLiteWJT:
    def __init__(self, db):
        self.db = os.getcwd() + os.sep + db
        self.conn = sqlite3.connect(self.db)
        # text_factory = str results in bytestrings being returned rather than unicode for TEXT fields
        # = OptimizedUnicode returns bytestrings for ASCII, and unicode for non-ASCII
        self.conn.text_factory = sqlite3.OptimizedUnicode
        self.results = None

    def get_results(self):
        return self.results

    def close_connection(self):
        self.conn.close()

    def query_table(self, sql_command):
        try:
            cursor = self.conn.execute(sql_command)
            self.results = cursor.fetchall()
            return self.results
        except Exception as e:
            self.results = e
            return self.results

    def get_dataframe(self, sql_command):
        df = pd.read_sql(sql_command, self.conn)
        return df

    def excel_to_sqlite(self):
        # read into a pandas dataframe
        df = pd.read_excel('county_hrap.xlsx', sheetname='Sheet1')

        sql = "delete from county_hrap"
        self.conn.execute(sql)
        self.conn.commit()

        for index, row in df.iterrows():
            sql = "insert into county_hrap values ('" + str(row['county'].strip()) + "'," + \
                  str(row['hrapx']) + "," + str(row['hrapy']) + ")"
            self.conn.execute(sql)
            if index % 100 == 0:
                print(index)
                self.conn.commit()
                time.sleep(1)
        self.conn.commit()
        self.conn.close()


if __name__ == "__main__":
    sqlitewjt = SQLiteWJT('precipddf.db')
    sql = "select 1/prob as rp, d_1hr, d_3hr, d_6hr, d_12hr, d_24hr" \
          " from ddf where county = 'Bastrop' " \
          "and hrapx=585 and hrapy=173"
    df = sqlitewjt.get_dataframe(sql)
    sqlitewjt.close_connection()
    dft = df.T

    # print(dft[:1])
    # print(dft[1:])
    # print(dft.index)

    lst_hrs = [1, 3, 6, 12, 24]
    lst_rp = [2, 5, 10, 25, 50, 100, 250, 500]
    lst_legend = [str(x) + '-yr' for x in lst_rp]
    lst_legend_reversed = list(reversed(lst_legend))
    print(lst_legend_reversed)

    # add the lines in reverse order: 500, 250, 100, etc.
    for col in range(dft.shape[1]-1, -1, -1):
        if dft[:1][col].values[0] in lst_rp:
            plt.plot(lst_hrs, dft[1:][col].values)
            print(dft[:1][col].values)
            print(dft[1:][col].values)
    plt.xticks(lst_hrs)
    plt.xlim(xmin=1)
    plt.xlim(xmax=24)
    plt.ylim(ymax=16)
    plt.grid(b=True, which='both')
    plt.xlabel('Duration (hrs)', fontsize='medium')
    plt.ylabel('Depth (in)', fontsize='medium')
    # plt.xscale('log')
    newhrs = [1, 3, 6, 12, 24]
    newdepth = [2.1, 3.2, 5.6, 7.9, 13.5]
    plt.plot(newhrs, newdepth, 'r--D', linewidth=3.0, markersize=9)
    plt.legend(lst_legend_reversed + ['storm'], loc='upper left', fontsize='small')

    plt.show()
