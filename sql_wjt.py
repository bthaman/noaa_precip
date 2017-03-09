"""
 querying sql server
"""

import pypyodbc


class SqlWjt:
    def __init__(self, cnn_string='Driver={SQL Server};Server=FN27963\SQLEXPRESS;Database=HCFCD'):
        self.cnn_string = cnn_string
        self.connection = pypyodbc.connect(self.cnn_string)
        self.cursor = self.connection.cursor()
        self.results = None

    def close_cnn(self):
        self.connection.close()

    def commit_update(self):
        self.connection.commit()

    def update_table(self, sql_command, commit=True):
        self.cursor.execute(sql_command)
        if commit:
            self.connection.commit()

    def getresults(self):
        return self.results

    def query_table(self, sql_command):
        try:
            self.cursor.execute(sql_command)
            self.results = self.cursor.fetchall()
            return self.results
        except Exception as e:
            self.results = e
            return self.results


class Sproc:
    def __init__(self, cnn_string='Driver={SQL Server};Server=FN27963\SQLEXPRESS;Database=HCFCD'):
        self.cnn_string = cnn_string
        self.connection = pypyodbc.connect(self.cnn_string, autocommit=False)
        self.cursor = self.connection.cursor()
        self.results = None

    def close_cnn(self):
        self.connection.close()

    def update_sproc(self, sql_command, params):
        self.cursor.execute(sql_command, params)

    def commit_update(self):
        self.connection.commit()


if __name__ == '__main__':
    sqlwjt = SqlWjt(cnn_string='Driver={SQL Server};Server=FN27963\SQLEXPRESS;Database=HCFCD')
    select_or_update = 'select'

    if select_or_update == 'select':
        sql = 'select hrapx, hrapy from pts_cnty'
        sql = 'select hrapx, hrapy, globvalue from pts_cnty'
        try:
            results = sqlwjt.query_table(sql)
            for hrapx, hrapy, globvalue in results:
                print(hrapx, hrapy, float(globvalue)+0.1)
            print(len(results))
        except Exception as e:
            print(sqlwjt.getresults())
        sqlwjt.close_cnn()
    else:
        sql = 'update pts_cnty set globvalue = 0'
        sqlwjt.update_table(sql)
        sqlwjt.close_cnn()

"""
SQLCommand = "SELECT * FROM Test"

cursor.execute(SQLCommand)
results = cursor.fetchone()
while results:
    # print(results[2] + " is " + str(results[3]) + " years old.")
    results = cursor.fetchone()

# method 2: fetch all records at once
cursor.execute(SQLCommand)
# fetchall returns a list of tuples
results = cursor.fetchall()
for id, last, first, age, height in results:
    print(last + ', ' + first + ' is ' + str(age) + ' yrs old.')

# another way
for row in results:
    for item in row:
        print(item)

# read into a pandas dataframe
df = pd.read_sql(SQLCommand, connection)
print(df.head())

connection.close()
"""