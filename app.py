"""

A simple webhook event handler for Sendgrid

"""

import os
import json

import flask
from flask import request, jsonify
import flask_sqlalchemy
from sqlalchemy.ext.hybrid import hybrid_property

app = flask.Flask(__name__)
app.config['BASE_URL'] = os.environ['BASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# username/pass to POST
post_user, post_pass = os.environ['POST_USERNAME'], os.environ['POST_PASSWORD']

db = flask_sqlalchemy.SQLAlchemy()
db.init_app(app)

# Based on 
# https://sendgrid.com/docs/for-developers/tracking-events/event/#event-objects
# These are other rarer(?) possibilities:
# asm_group_id, unique_args, marketing_campaign_id, marketing_campaign_name, pool
class Event(db.Model):
    email           = db.Column(db.Text)
    timestamp       = db.Column(db.Integer) # DateTime)
    event           = db.Column(db.Text)
    smtp_id         = db.Column(db.Text) # sg key is 'smtp-id'
    useragent       = db.Column(db.Text)
    ip              = db.Column(db.Text)
    sg_event_id     = db.Column(db.String(100), primary_key=True)
    sg_message_id   = db.Column(db.Text)
    reason          = db.Column(db.Text)
    status          = db.Column(db.Text)
    response        = db.Column(db.Text)
    tls             = db.Column(db.Text)
    url             = db.Column(db.Text)
    urloffset       = db.Column(db.Text)
    attempt         = db.Column(db.Text)
    category        = db.Column(db.Text)
    type_           = db.Column(db.Text)
    _other          = db.Column('other', db.Text, default='[]')

    @hybrid_property
    def other(self):
        return json.loads(self._other)

    @other.setter
    def other(self, lst):
        self._other = json.dumps(lst)

event_keys = [k.strip('_')
    for k in flask_sqlalchemy.inspect(Event).columns.keys()
        if not k.startswith('_')]

@app.route('/', methods=['POST'])
def home():
    if request.authorization["username"] != post_user or \
       request.authorization["password"] != post_pass:
        return jsonify({"message": "Unauthorized"}), 401

    # No data, just return
    if not request.json:
        return ""

    # fix name mangling
    if 'smtp-id' in request.json.keys():
        request.json['smtp_id'] = request.json.pop('smtp-id')
    
    # collect keys not in model
    other = {}
    for k in list(request.json.keys()):
        if k not in event_keys:
            other[k] = str(request.json.pop(k))

    obj = Event(**request.json)
    obj.other = other

    db.session.merge(obj)
    db.session.commit()

    return ""

@app.cli.command("initdb")
def init_db():
    db.create_all()
    db.session.commit()
    return

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=True)
