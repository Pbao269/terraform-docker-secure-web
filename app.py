from flask import Flask

app = Flask(__name__)


@app.get('/')
def home():
    return '<h1>Secure Web Application</h1>'


@app.get('/health')
def health():
    return {'status': 'healthy'}
