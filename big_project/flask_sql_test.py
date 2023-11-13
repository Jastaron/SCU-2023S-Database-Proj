import MySQLdb
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '20030415'
app.config['MYSQL_DB'] = 'sc_cq_specimen_normalization'

mysql = MySQL(app)

@app.route("/")
def users():
    conn = mysql.connection
    cur = conn.cursor()
    try:
        sql_str = "SELECT * FROM pac_county;"
        cur.execute(sql_str)
    except:
        pass

if __name__ == '__main__':
    app.run()
