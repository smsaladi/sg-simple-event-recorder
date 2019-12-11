"""

Simple testing for webhook handler
"""

import os
# set vars read from env (forcing an in-memory database)
os.environ['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
os.environ['BASE_URL'] = 'localhost:5000'
os.environ['POST_USERNAME'] = 'test_username'
os.environ['POST_PASSWORD'] = 'test_passw@@!'

import pytest
from requests.auth import _basic_auth_str

from app import app, db, Event

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            db.session.commit()
        yield client
    return


def test_get(client):
    res = client.get('/')
    assert res.status_code == 405
    return


def test_auth(client):
    headers = {'Authorization': _basic_auth_str(
        os.environ['POST_USERNAME'],
        os.environ['POST_PASSWORD'])
    }

    res = client.post("/", headers=headers)
    assert res.status_code == 200

    headers = {'Authorization': _basic_auth_str(
        os.environ['POST_USERNAME'] + 'x',
        os.environ['POST_PASSWORD'])
    }

    res = client.post("/", headers=headers)
    assert res.status_code == 401

    headers = {'Authorization': _basic_auth_str(
        os.environ['POST_USERNAME'],
        os.environ['POST_PASSWORD'] + 'x')
    }

    res = client.post("/", headers=headers)
    assert res.status_code == 401

    return


def test_data(client):
    headers = {'Authorization': _basic_auth_str(
        os.environ['POST_USERNAME'],
        os.environ['POST_PASSWORD'])
    }
    for data in sample_data:
        res = client.post("/", headers=headers, json=data)
        with app.app_context():
            obj = Event.query.all()[0]
            obj_keys = obj.__dict__.keys()

            # Check that data made it to the db (handling key mangling)
            for k, v in data.items():
                obj_k = k.replace('-', '_')
                if obj_k in obj_keys:
                    assert getattr(obj, obj_k) == data[k]
                else:
                    assert obj.other[obj_k] == str(data[k])

        assert res.status_code == 200

    return 


# Sample data from 
# https://sendgrid.com/docs/for-developers/tracking-events/event/
sample_data = [
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"processed",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"deferred",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "response":"400 try again later",
      "attempt":"5"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"delivered",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "response":"250 OK"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"open",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "useragent":"Mozilla/4.0 (compatible; MSIE 6.1; Windows XP; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "ip":"255.255.255.255"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"click",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "useragent":"Mozilla/4.0 (compatible; MSIE 6.1; Windows XP; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "ip":"255.255.255.255",
      "url":"http://www.sendgrid.com/"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"bounce",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "reason":"500 unknown recipient",
      "status":"5.0.0"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"dropped",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "reason":"Bounced Address",
      "status":"5.0.0"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"spamreport",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"unsubscribe",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id"
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"group_unsubscribe",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "useragent":"Mozilla/4.0 (compatible; MSIE 6.1; Windows XP; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "ip":"255.255.255.255",
      "url":"http://www.sendgrid.com/",
      "asm_group_id":10
   },
   {
      "email":"example@test.com",
      "timestamp":1513299569,
      "smtp-id":"<14c5d75ce93.dfd.64b469@ismtpd-555>",
      "event":"group_resubscribe",
      "category":"cat facts",
      "sg_event_id":"sg_event_id",
      "sg_message_id":"sg_message_id",
      "useragent":"Mozilla/4.0 (compatible; MSIE 6.1; Windows XP; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "ip":"000.000.000.000",
      "url":"http://www.sendgrid.com/",
      "asm_group_id":10
   }
]
