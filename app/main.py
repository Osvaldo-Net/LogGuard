from flask import Flask, render_template, request, redirect, session
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

    log_dir = '/var/log'
    log_filename = request.args.get('file', 'ufw.log')
    limit = request.args.get('limit', '20')

    log_path = os.path.join(log_dir, log_filename)
    available_logs = [
        f for f in os.listdir(log_dir)
        if os.path.isfile(os.path.join(log_dir, f)) and f.endswith('.log')
    ]

    if not os.path.exists(log_path):
        return render_template(
            'logs.html',
            log_data=[],
            error='Archivo no encontrado',
            path=log_path,
            selected_limit=limit,
            available_logs=available_logs
        )

    log_data = parse_log(log_path)

    # Ordenar por fecha (más reciente primero)
    log_data = sorted(log_data, key=lambda x: x['timestamp'], reverse=True)

    # Aplicar límite de resultados
    if limit != 'all':
        try:
            count = int(limit)
            log_data = log_data[:count]
        except ValueError:
            log_data = log_data[:20]

    return render_template(
        'logs.html',
        log_data=log_data,
        path=log_path,
        selected_limit=limit,
        available_logs=available_logs
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
