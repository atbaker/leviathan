from flask import Flask, request, redirect, send_from_directory

import json
import os
import requests
import twilio.twiml


app = Flask(__name__, static_url_path='')
ionic_secret = os.environ.get('IONIC_SECRET')

@app.route('/', methods=['GET', 'POST'])
def get_name():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()

    # Send the initial query
    intro = "Hello, you have reached Mr. Baker's office. Who may I say is calling?"
    resp.say(intro, voice='woman', language='en-GB')#  voice='Alice', language='en-GB')

    # Record the caller's response
    resp.record(maxlength=4, action='/hold', playBeep=False, transcribe=True, transcribeCallback='/name')

    return str(resp)

@app.route('/hold', methods=['GET', 'POST'])
def hold():
    """Keeps users on hold indefinitely"""
    resp = twilio.twiml.Response()
    resp.say("Please hold.", voice='woman', language='en-GB')
    resp.play('/girl-from-ipanema', loop=0)

    return str(resp)

@app.route('/girl-from-ipanema')
def hold_music():
    """Soothing hold music / some versions of Hell"""
    return send_from_directory('', 'girl_from_ipanema.mp3')

@app.route('/name', methods=['GET', 'POST'])
def review_name():
    """Forwards a caller's name to the user"""
    # CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('TranscriptionType', 'fast'), ('ApiVersion', '2010-04-01'), ('Called', '+12027590452'), ('Direction', 'inbound'), ('AccountSid', 'AC11d7931aa764fddb377658396881b41a'), ('Caller', '+17036230231'), ('From', '+17036230231'), ('TranscriptionSid', 'TR64ac7b61c2d52877b8fa5b066921c3db'), ('TranscriptionUrl', 'http://api.twilio.com/2010-04-01/Accounts/AC11d7931aa764fddb377658396881b41a/Recordings/RE98e3a54f49cef63427577c1ff75452d5/Transcriptions/TR64ac7b61c2d52877b8fa5b066921c3db'), ('RecordingSid', 'RE98e3a54f49cef63427577c1ff75452d5'), ('TranscriptionStatus', 'completed'), ('CallStatus', 'in-progress'), ('CallSid', 'CAcc14b2d4b143bf93f37f59c15578e41a'), ('To', '+12027590452'), ('RecordingUrl', 'http://api.twilio.com/2010-04-01/Accounts/AC11d7931aa764fddb377658396881b41a/Recordings/RE98e3a54f49cef63427577c1ff75452d5'), ('TranscriptionText', 'Andrew Baker.')])])

    # Extract the transcription
    transcription = request.values

    # status = transcription['TranscriptionStatus']

    # if status == 'failed':
    #     # Maybe send a push notification saying we couldn't figure out who was calling
    #     return ('', 200)

    # phone_number = transcription['From']
    phone_number = "+17036230231"
    humanized_phone_number = "({0}) {1}-{2}".format(phone_number[2:5], phone_number[5:8], phone_number[8:])
    # name = transcription['TranscriptionText']
    name = 'Andrew Baker'

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
                    "phone_number": humanized_phone_number,
                    "name": name
                }
            }
        }
    }

    response = requests.post('https://push.ionic.io/api/v1/push', data=json.dumps(payload), headers=headers, auth=(ionic_secret, ''))

    return ('', 200)

if __name__ == '__main__':
    app.run(debug=True)
