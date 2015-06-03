from flask import Flask, request, redirect, send_from_directory
import twilio.twiml


app = Flask(__name__, static_url_path='')

@app.route('/', methods=['GET', 'POST'])
def get_name():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()

    # Send the initial query
    intro = "Hello, you have reached Mr. Baker's office. Who may I say is calling?"
    resp.say(intro, voice='woman')#  voice='Alice', language='en-GB')

    # Record the caller's response
    resp.record(maxlength=4, action='/hold', playBeep=False, transcribe=True, transcribeCallback='/name')

    return str(resp)

@app.route('/hold', methods=['GET', 'POST'])
def hold():
    """Keeps users on hold indefinitely"""
    resp = twilio.twiml.Response()
    resp.say("Please hold.")
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
    transcription_status = request.values['TranscriptionStatus']

    if transcription_status == 'failed':
        # Maybe send a push notification saying we couldn't figure out who was calling
        return ('', 204)

    transcription = request.values['TranscriptionText']
    # Send a push notification

    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
