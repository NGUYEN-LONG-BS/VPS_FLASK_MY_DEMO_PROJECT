from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import os
from os import path

from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config["SECRET_KEY"] = "anhnebs"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Lấy đường dẫn tuyệt đối của file app.py
basedir = path.abspath(path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{path.join(basedir, 'users.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=1)

def create_app():
    return app

db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route('/home')
@app.route('/')
def render_home_page():
    return render_template("home.html"
                           ,var_name="Kế thừa templates"
                           )
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session.permanent = True  # Làm cho session luôn có lifetime
        if username == 'admin' and password == '123456':
            session['username'] = username  # Lưu trữ tên người dùng vào session
            flash('You logged in successfully', 'info')
            return redirect(url_for("f_user", var_name=username))
    if 'username' in session:
        print("username đã có trong session")
        flash('You are already logged in', 'info')
        name = session['username']
        return redirect(url_for("f_user", var_name=name))
    else:
        flash('You are not logged in', 'info')
        print("username không có trong session")
    return render_template("login.html")
    
@app.route('/index')
def hello_world():
    return render_template("index.html"
                           ,var_name="biến đây"
                           ,cars=["Vin", "BMW", "Audi", "Toyota", "Honda", "Suzuki", "Mazda"]
                           )

@app.route('/user', methods=['POST', 'GET'])
def f_user():
    print("chuyển sang trang user.html")
    if 'username' in session:
        name = session['username']
        
        # Nếu có dữ liệu gửi lên từ form, thêm email vào cơ sở dữ liệu
        if request.method == 'POST':
            email = request.form['email']  # Lấy giá trị email từ form
            if email:
                # Tạo một đối tượng User mới và thêm vào cơ sở dữ liệu
                new_user = User(name=name, email=email)
                db.session.add(new_user)
                db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
                flash(f"Email {email} has been saved.", 'success')  # Thông báo thành công
        
        return render_template("user.html", var_name=name)
        
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You logged out', 'info')
    return redirect(url_for('login'))

def plot_line_chart(df):
    x_values = df.iloc[:, 0]
    y_values = df.iloc[:, 1].astype(float)
    
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker='o', linestyle='-', color='b')
    
    ax.set_xlabel("Trục X")
    ax.set_ylabel("Trục Y")
    ax.set_title("Biểu đồ Line Chart từ Excel")
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@app.route('/mychart', methods=['GET', 'POST'])
def mychart():
    plot_url = None
    df_html = None
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)
            if len(df.columns) >= 2:
                plot_url = plot_line_chart(df)
                df_html = df.to_html(classes='table table-striped', index=False)
    
    return render_template('mychart.html', plot_url=plot_url, df_html=df_html)

if __name__ == '__main__':
    with app.app_context():  # Tạo application context
        # if not path.exists("users.db"):
        if not path.exists(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")):
            # db.create_all(app = app)
            db.create_all()
            print("Database created")
    app.run(host='0.0.0.0', port=5000, debug=True)