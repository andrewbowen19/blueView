'''
Scheduler script to update our Heroku DB from Simpelcast

https://www.postgresqltutorial.com/postgresql-python/update/
'''

import os
import psycopg2
# Connection url -- env variable in production
dns = 'postgres://tssziceensuyju:df46ddbe5911723f5b7c920bcda753f4cc9fa50215ae9b4b92129fe354a3e0da@ec2-3-232-92-90.compute-1.amazonaws.com:5432/d6ij7g4596l6t4'
conn = psycopg2.connect(dns)
cur = conn.cursor()

value1=10
value2="Hamburgers"

cur.execute('UPDATE', (value1, value2))

conn.commit()
cur.close()
conn.close()