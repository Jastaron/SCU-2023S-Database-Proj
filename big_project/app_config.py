from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

# 初始化flask
app = Flask(__name__, static_url_path='', static_folder='templates', template_folder='templates')
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = '1145141919810'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

mysql = MySQL(app)
