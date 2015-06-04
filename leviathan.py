from flask import Flask, request, redirect, send_from_directory
from twilio.rest import TwilioRestClient
from twilio.rest.resources import Call
from urllib.parse import urljoin

import json
import os
import requests
import twilio.twiml


app = Flask(__name__, static_url_path='')

# Get environment variables
IONIC_SECRET = os.environ.get('IONIC_SECRET')
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
HOSTNAME = os.environ.get('HOST', 'http://leviathan.atbaker.me')

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

@app.route('/', methods=['GET', 'POST'])
def get_name():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()

    # Send the initial query
    intro = "Hello, you have reached Mr. Baker's office. Who may I say is calling?"
    resp.say(intro, voice='woman', language='en-GB')#  voice='Alice', language='en-GB')

    # Record the caller's response
    resp.record(maxLength='4', action='/hold', playBeep=True, transcribe=True, transcribeCallback='/name')

    return str(resp)

@app.route('/hold', methods=['GET', 'POST'])
def hold():
    """Keeps users on hold indefinitely"""
    resp = twilio.twiml.Response()
    resp.say("Please hold.", voice='woman', language='en-GB')
    resp.play('/hold_music_one.mp3', loop=0)

    return str(resp)

@app.route('/hold-two', methods=['GET', 'POST'])
def hold_two():
    """A hold track that uses the same song but at a jazzier refrain"""
    resp = twilio.twiml.Response()
    resp.say("Thank you. Please hold.", voice='woman', language='en-GB')
    resp.play('/static/hold_music_two.mp3', loop=0)

    return str(resp)

@app.route('/static/<path:path>')
def hold_music(path):
    """Soothing hold music / some versions of Hell"""
    return send_from_directory('static', path)

@app.route('/name', methods=['GET', 'POST'])
def send_name():
    """Forwards a caller's name to the user"""
    # CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('TranscriptionType', 'fast'), ('ApiVersion', '2010-04-01'), ('Called', '+12027590452'), ('Direction', 'inbound'), ('AccountSid', 'AC11d7931aa764fddb377658396881b41a'), ('Caller', '+17036230231'), ('From', '+17036230231'), ('TranscriptionSid', 'TR64ac7b61c2d52877b8fa5b066921c3db'), ('TranscriptionUrl', 'http://api.twilio.com/2010-04-01/Accounts/AC11d7931aa764fddb377658396881b41a/Recordings/RE98e3a54f49cef63427577c1ff75452d5/Transcriptions/TR64ac7b61c2d52877b8fa5b066921c3db'), ('RecordingSid', 'RE98e3a54f49cef63427577c1ff75452d5'), ('TranscriptionStatus', 'completed'), ('CallStatus', 'in-progress'), ('CallSid', 'CAcc14b2d4b143bf93f37f59c15578e41a'), ('To', '+12027590452'), ('RecordingUrl', 'http://api.twilio.com/2010-04-01/Accounts/AC11d7931aa764fddb377658396881b41a/Recordings/RE98e3a54f49cef63427577c1ff75452d5'), ('TranscriptionText', 'Andrew Baker.')])])

    # Extract the transcription
    transcription = request.values

    status = transcription['TranscriptionStatus']

    if status == 'failed':
        # Say the transcription failed
        name = '(transcription unavailable)'
    else:
        name = transcription['TranscriptionText'].strip('.')
        # name = 'Andrew Baker'

    phone_number = transcription['From']
    # phone_number = "+17036230231"

    humanized_phone_number = "({0}) {1}-{2}".format(phone_number[2:5], phone_number[5:8], phone_number[8:])

    sid = transcription['CallSid']

    # Send a push notification
    headers = {
        'Content-Type': 'application/json',
        'X-Ionic-Application-Id': '650c50f6',
    }
    payload = {
        "tokens": ["1c2a86dd924bac3ff93d6f228d787eecb3b91707c6ce0cb00c45cd0283c5c891"],
        "notification": {
            "alert": "{0} is trying to call you from {1}. Do you want to pick up?".format(name, humanized_phone_number),
            "ios": {
                "badge": 1,
                "payload": {
                    "stage": "name",
                    "sid": sid,
                    "phone_number": humanized_phone_number,
                    "name": name
                }
            }
        }
    }

    response = requests.post('https://push.ionic.io/api/v1/push', data=json.dumps(payload), headers=headers, auth=(IONIC_SECRET, ''))

    return ('', 200)

@app.route('/purpose', methods=['GET', 'POST'])
def send_purpose():
    """Forwards a caller's purpose to the user"""
    # Extract the transcription
    transcription = request.values

    status = transcription['TranscriptionStatus']

    if status == 'failed':
        # Say the transcription failed
        purpose = '(transcription unavailable)'
    else:
        purpose = transcription['TranscriptionText']
        # purpose = "I'm from the IRS and we're coming to arrest you."

    sid = transcription['CallSid']

    # Send a push notification
    headers = {
        'Content-Type': 'application/json',
        'X-Ionic-Application-Id': '650c50f6',
    }
    payload = {
        "tokens": ["1c2a86dd924bac3ff93d6f228d787eecb3b91707c6ce0cb00c45cd0283c5c891"],
        "notification": {
            "alert": '"{0}"'.format(purpose),
            "ios": {
                "badge": 1,
                "payload": {
                    "stage": "purpose",
                    "sid": sid,
                    "purpose": purpose
                }
            }
        }
    }

    response = requests.post('https://push.ionic.io/api/v1/push', data=json.dumps(payload), headers=headers, auth=(IONIC_SECRET, ''))

    return ('', 200)

@app.route('/decide', methods=['GET', 'POST'])
def receive_decision():
    """Accepts decisions from the user on how to handle the incoming call"""
    data = request.get_json()

    sid = data['sid']
    decision = data['decision']

    call = client.calls.get(sid)

    if decision == 'accept':
        # Accept the call
        client.calls.update(sid, method="POST",
            url=urljoin(HOSTNAME, '/dial'),
            callerId=call.from_formatted)
    elif decision == 'reject':
        # Reject the call
        client.calls.update(sid, method="POST",
            url=urljoin(HOSTNAME, '/hangup'))
    elif decision == 'ask':
        # Ask the caller why they're calling
        client.calls.update(sid, method="POST",
            url=urljoin(HOSTNAME, '/ask-purpose'))

    return ('', 200)

@app.route('/dial', methods=['GET', 'POST'])
def dial_user():
    """Connects the caller with the user when a call is accepted"""
    resp = twilio.twiml.Response()
    resp.dial(number='+17036230231')

    return str(resp)

@app.route('/hangup', methods=['GET', 'POST'])
def reject_call():
    """Ends the call when a user does not want to talk to the caller"""
    resp = twilio.twiml.Response()
    resp.say("I'm sorry, Mr. Baker doesn't want to talk to you. Goodbye scum.", voice='woman', language='en-GB')
    resp.hangup()

    return str(resp)

@app.route('/ask-purpose', methods=['GET', 'POST'])
def ask_purpose():
    """Asks the caller to state their business"""
    resp = twilio.twiml.Response()

    # Ask why the caller is calling
    resp.say("Hello again. What is this call concerning?", voice='woman', language='en-GB')

    # Record their response
    resp.record(maxLength='7', action='/hold-two', playBeep=True, transcribe=True, transcribeCallback='/purpose')

    return str(resp)


if __name__ == '__main__':
    app.run(debug=True)
