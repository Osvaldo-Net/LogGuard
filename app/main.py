from flask import Flask, render_template, request, redirect, session, url_for
from auth import check_login, must_change_password, change_password
from log_parser import parse_log
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if check_login(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            if must_change_password(request.form['username']):
                return redirect('/change-password')
            return redirect('/logs')
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/change-password', methods=['GET', 'POST'])
def change_pass():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        change_password(session['username'], request.form['new_password'])
        return redirect('/logs')
    return render_template('change_password.html')

@app.route('/logs', methods=['GET'])
def logs():
    if 'username' not in session:
        return redirect('/')
    log_path = request.args.get('file', '/var/log/ufw.log')
    if not os.path.exists(log_path):
        return render_template('logs.html', log_data=[], error='Archivo no encontrado', path=log_path)
    log_data = parse_log(log_path)
    return render_template('logs.html', log_data=log_data, path=log_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
