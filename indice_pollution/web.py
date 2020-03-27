from flask import current_app, render_template

@current_app.route('/')
def root():
    return render_template('index.html')

@current_app.route('/ville/<insee>')
def ville(insee):
    return render_template('indice.html', insee=insee)