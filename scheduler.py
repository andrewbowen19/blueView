'''
Scheduler script to update our Heroku DB from Simpelcast

https://www.postgresqltutorial.com/postgresql-python/update/
'''

import os
import psycopg2
from utils import getSimplecastResponse, podIDs
import json
import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from boto.s3.connection import S3Connection

# s3 = S3Connection(os.environ['DATABASE_URL'], os.environ['SIMPLECAST_ACCOUNT_ID'])


# Connection url -- env variable in production
dns = os.environ['DATABASE_URL']
account_id = '3c7a8b2b-3c19-4d8d-8b92-b17852c3269c' # os.environ['SIMPLECAST_ACCOUNT_ID']
test_id = '93cc0b3a-49ea-455f-affd-ac01fdafd761'

### Tables we need ###

# Network-level downloads/listeners by date
# 

# API calls to write to db

# res = json.loads(getSimplecastResponse(f'/analytics/podcasts?account={account_id}&limit=1000'))


# network_dat = json.loads(getSimplecastResponse(f'/analytics/downloads?account={account_id}'))
# Listeners
listener_data = []
podcasts = podIDs()
pod_ids = [x['value'] for x in podIDs()]

print('Got Simplecast call!')

def create_table():
    '''
    Creating a Postgres table
    https://www.postgresqltutorial.com/postgresql-python/create-tables/
    '''
    print('Creating new table in db...')


    '''Creates table in our Postgres db from Heroku'''
    commands = (
        """
        ALTER TABLE network
        ADD COLUMN IF NOT EXISTS interval DATE NOT NULL,
        ADD COLUMN IF NOT EXISTS downloads_total INT NOT NULL,
        ADD COLUMN IF NOT EXISTS downloads_percent FLOAT(24) NOT NULL;
        """,
        """
        ALTER TABLE podcasts_by_interval
        ADD COLUMN IF NOT EXISTS interval DATE NOT NULL,
        ADD COLUMN IF NOT EXISTS downloads_total INT NOT NULL,
        """
        )
    conn = None
    try:
        # https://stackoverflow.com/questions/61022590/psycopg2-cant-execute-an-empty-query
        print('Connecting to db...')
        # connect to the PostgreSQL server
        conn = psycopg2.connect(dns)#, sslmode='require')
        cur = conn.cursor()
        print('DB connection established!')
        # create table one by one
        for command in commands:
            # cur.execute(command)
            print('Table cols created!')  

        # Writing network-level data  # 
            n = 1
            for i in network_dat['by_interval']:
                
                interval = i['interval']
                downloads_total = i['downloads_total']
                downloads_percent = i['downloads_percent']
                d = (n, interval, downloads_total, downloads_percent)

                cur.execute(f'INSERT INTO network (id, interval, downloads_total, downloads_percent) VALUES (%s, %s, %s, %s)', d)
                n += 1




        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def update_podcast_table():
    '''
    Updating pods_by_interval table
    '''
    for p in pod_ids:
        print(p)
    res = json.loads(getSimplecastResponse(f'/analytics/podcasts?account={account_id}&limit=1000'))
    commands = (
        """
        ALTER TABLE podcasts_by_interval
        ADD COLUMN IF NOT EXISTS interval DATE NOT NULL,
        ADD COLUMN IF NOT EXISTS downloads_total INT NOT NULL,
        """
        )
    conn = None

    try:
        # https://stackoverflow.com/questions/61022590/psycopg2-cant-execute-an-empty-query
        print('Connecting to db...')
        # connect to the PostgreSQL server
        conn = psycopg2.connect(dns)#, sslmode='require')
        cur = conn.cursor()
        print('DB connection established!')
        # create table one by one
        for command in commands:
            # cur.execute(command)
            print('Table cols created!')  


            m = 1
            # for d in res['collection']:
            #     print(d)
                # cur.execute(...)
                

        cur.close()
        # commit the changes
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def update_db(table, columns, data):
    '''
    Function to flexibily update our heroku postgres db 
    table: name of data table within our heroku db 
    columns: list of strings with column names, len(columns) == len(data[i])
    data: list of tuples with values to insert
    '''
    # Connecting to db and setting up a cursor
    conn = None
    try:
        conn = psycopg2.connect(dns) # Use env variable for production
        cur = conn.cursor()


        for d in data:
            cols = str(tuple(columns)) 
            n_vals = str(tuple(['%s' for x in d]))
            cur.execute(f'INSERT INTO {table}{cols} VALUES {n_vals}', d)

        cur.close()
        conn.commit()

    # Raise any exceptions and close the connection
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def format_response(query, tag):
    '''
    Format Simplecast response into proper data format for update_db
    Should return data as a list of tuples, 
    length of the tuples should match the # of datatable columns for that stat

    query: str, Simplecast API call, passed as a param to getSimplecast Response
    tag: str, Key name for Simplecast response, typically 'by_interval' or 'collection' depending on type
    '''
    res = json.loads(getSimplecastResponse(query))
    data = res[tag]

    # print('Response data:', data)
    new_data = []
    n = 1
    # Looping through items in data response
    for d in data:
        dlist = list(d.values())
        # dlist[1] = 
        dlist.insert(0,n)
        new_data.append(tuple(dlist))
      
        n += 1

    print(new_data[0:10], '...')
    return new_data


def create_podcast_tables():
    '''
    Creates table for each podcast in our db
    podcast: str, podcast title
    '''
    
    for p in pod_ids:
        query = f'/analytics/downloads?podcast={p}'
        pod_data = format_response(query, 'by_interval')
        columns = ['interval', 'downloads_total', 'downloads_percent','id']
        print(f'Creating DT for {p}')
        conn = None
        try:
            conn = psycopg2.connect(dns) # Use env variable for production
            cur = conn.cursor()

            pod_table_name = 'p_' + p.replace('-','_')
            # downloads_total, downloads_percent, interval
            cur.execute(f'CREATE TABLE {pod_table_name} (interval DATE NOT NULL, downloads_total INT NOT NULL, downloads_percent INT NOT NULL, id INT NOT NULL)')
            
            # D=Adding data to our db
            for d in pod_data:        
                cols = str(tuple(columns)).replace("'", '')
                n_vals = str(tuple(['%s' for x in d]))
                print('Inserting data...', d)
                # Inserting data
                cur.execute(f'INSERT INTO {pod_table_name} {cols} VALUES {n_vals};', d)
                print(f'Data inserted for table {pod_table_name} !')
            cur.close()
            conn.commit()

        # Raise any exceptions and close the connection
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('Table created, onto the next!\n')

# ##############################################################################

def write_network_table(update=True):
    '''
    Writes network-level downloads table
    https://stackoverflow.com/questions/23103962/how-to-write-dataframe-to-postgres-table
    '''
    engine = create_engine(dns)


    # Normal update table with last day's data
    if update:
        start_date = (datetime.datetime.now()).date()
        dat = json.loads(getSimplecastResponse(f'/analytics/downloads?account={account_id}&start_date={start_date}'))
        df = pd.DataFrame(dat['by_interval'])
        print(df)
        df.to_sql('network_level', con=engine, if_exists='append')

    # Write all-time data to db
    elif not update:
        dat = json.loads(getSimplecastResponse(f'/analytics/downloads?account={account_id}'))
        df = pd.DataFrame(dat['by_interval'])
        df.to_sql('network_level', engine)
    print('Database Network table updated!')

def write_pod_tables():
    '''
    Writes podcast tables to our db
    '''

if __name__ == '__main__':

    # create_table()
    # format_response(f'/analytics/downloads?podcast={test_id}&limit=1000', 'by_interval')
    # create_podcast_tables()
    write_network_table()
