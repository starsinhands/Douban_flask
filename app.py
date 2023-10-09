from urllib import request
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect,url_for,session
import sqlite3
import pandas as pd
import numpy as np
app = Flask(__name__)
app.secret_key='machine_learning'#

@app.route('/')
def index():
    return render_template('login.html')
    # if 'file_data' in session:#
    #     return render_template("index.html",uploaded=True)
    # else:#
    #     return render_template("index.html",uploaded=False)#

@app.route('/login', methods=['post'])
def login():
    username = request.form.get('username')  # 接收form表单传参
    password = request.form.get('password')
    if username=="admin" and password=="123456":
        return render_template('upload.html', msg='登陆成功')
    else:
        return render_template('login.html', msg='登录失败')

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        datalist = []
        con = sqlite3.connect("douban250.db")
        cur = con.cursor()
        sql = "select * from movie250"
        data = cur.execute(sql)
        for item in data:
            datalist.append(item)
        cur.close()
        con.close()
        return redirect(url_for('movie'))##

@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect("douban250.db")
    cur = con.cursor()
    sql = "select * from movie250"
    data = cur.execute(sql)
    for item in data :
        datalist.append(item)
    cur.close()
    con.close()
    # # 当前页码，从第一页开始
    # page = int(request.args.get("page", 1))
    # # 每页的数量
    # per_page = int(request.args.get('per_page', 25))
    # paginate = data.paginate(page, per_page, error_out=False)
    return render_template('movie.html',movies = datalist,data=data)

@app.route('/score')
def score():
    score = [] # 评分
    num = [] # 每一个电影评分对应的电影数量
    con = sqlite3.connect("douban250.db")
    cur = con.cursor()
    sql = "select score,count(score) from movie250 group by score"
    data = cur.execute(sql)
    for item in data :
        score.append(str(item[0]))
        num.append(item[1])
    cur.close()
    con.close()

    # data = pd.read_excel('豆瓣电影Top250.xls')
    # # 计算各个分数对应的频率
    # freq = data['评分'].value_counts(normalize=True).sort_index()
    # # 计算熵值
    # entropy = -np.sum(freq * np.log(freq))
    # # 计算各个分数的权重
    # weights = (1 - freq) / (len(freq) - 1)
    # # 计算归一化权重
    # normalized_weights = weights / np.sum(weights)
    return render_template('score.html',score = score ,num=num)

@app.route('/word')
def word():
    return render_template('word.html')
@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True)
