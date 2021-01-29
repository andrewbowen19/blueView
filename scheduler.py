'''
Scheduler script to update our Heroku DB from Simpelcast

https://www.postgresqltutorial.com/postgresql-python/update/
'''

import os
import psycopg2
# Connection url -- env variable in production
# dns = 
cur = conn.cursor()

value1=10
value2="Hamburgers"

cur.execute('UPDATE', (value1, value2))

conn.commit()
cur.close()
conn.close()