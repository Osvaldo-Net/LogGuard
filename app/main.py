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

    root_log_dir = os.environ.get('LOG_DIR', '/logs')

    # Detectar carpetas y archivos en /logs
    entries = os.listdir(root_log_dir)

    available_dirs = [
        d for d in entries if os.path.isdir(os.path.join(root_log_dir, d))
    ]

    available_files = [
        f for f in entries if os.path.isfile(os.path.join(root_log_dir, f)) and f.endswith('.log')
    ]

    selected_dir = request.args.get('dir', '')
    selected_file = request.args.get('file', '')
    limit = request.args.get('limit', '20')
    search_term = request.args.get('search', '').strip()

    log_data = []
    available_logs = []

    if selected_dir:
        dir_path = os.path.join(root_log_dir, selected_dir)
        if os.path.isdir(dir_path):
            available_logs = [
                f for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f)) and f.endswith('.log')
            ]
            if selected_file in available_logs:
                log_path = os.path.join(dir_path, selected_file)
            else:
                log_path = None
        else:
            log_path = None
    else:
        available_logs = available_files
        if selected_file in available_logs:
            log_path = os.path.join(root_log_dir, selected_file)
        else:
            log_path = None

    if selected_file and log_path and os.path.exists(log_path):
        try:
            log_data = parse_log(log_path)

            if search_term:
                log_data = [entry for entry in log_data if search_term.lower() in entry['content'].lower()]

            log_data = sorted(log_data, key=lambda x: x['timestamp'], reverse=True)

            if limit != 'all':
                count = int(limit)
                log_data = log_data[:count]
        except Exception as e:
            return render_template(
                'logs.html',
                error=f'Error al procesar el log: {e}',
                log_data=[],
                available_dirs=available_dirs,
                available_logs=available_logs,
                selected_dir=selected_dir,
                selected_log_file=selected_file,
                selected_limit=limit,
                search_term=search_term
            )

    return render_template(
        'logs.html',
        log_data=log_data,
        available_dirs=available_dirs,
        available_logs=available_logs,
        selected_dir=selected_dir,
        selected_log_file=selected_file,
        selected_limit=limit,
        search_term=search_term,
        error=None if log_data else 'No se encontraron entradas o archivo no válido.'
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
