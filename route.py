from app import app
from flask import render_templates

@app.route('/')
@app.route('/index')
def index():
    return render_templates('index.html', title='Home')

@app.rout('/about')
def about():
    return render_templates('about.html', title='About')