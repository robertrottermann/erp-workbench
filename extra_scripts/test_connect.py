import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    host="172.22.0.3",
    database="december_03",
    user="odoo",
    password="odoo")

a=1