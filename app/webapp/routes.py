from flask import render_template
from flask import current_app as app


@app.route('/')
def home():
    return render_template(
        'index.jinja2',
        title='US Representative Demographics Home Page',
        description='App to show demographics',
        template='home-template',
        body="Homepage with Flask"
    )