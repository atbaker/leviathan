from flask import Flask, request, redirect, send_from_directory
import twilio.twiml


app = Flask(__name__, static_url_path='')

@app.route('/', methods=['GET', 'POST'])
def get_name():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()

    # Send the initial query
    intro = "Hello, you have reached Mr. Baker's office. Who may I say is calling?"
    resp.say(intro)#  voice='Alice', language='en-GB')

    # Record the caller's response
    resp.record(maxlength=5, action='/hold', transcribe=True, transcribe_callback='/name')

    return str(resp)

@app.route('/hold', methods=['GET', 'POST'])
def hold():
	"""Keeps users on hold indefinitely"""
	resp = twilio.twiml.Response()
	resp.play('/girl-from-ipanema', loop=0)

	return str(resp)

@app.route('/girl-from-ipanema')
def hold_music():
	"""Soothing hold music / some versions of Hell"""
	return send_from_directory('', 'girl_from_ipanema.mp3')

@app.route('/name', methods=['GET', 'POST'])
def review_name():
	"""Forwards a caller's name to the user"""
	resp = twilio.twiml.Response()

	import pdb; pdb.set_trace()


if __name__ == '__main__':
    app.run(debug=True)
