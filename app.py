import os

from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

# Render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle a POST request to send a text message. This is called via ajax
# on our web page
@app.route('/message', methods=['POST'])
def message():
    # Send a text message to the number provided
    message = client.sms.messages.create(to=request.form['to'],
                                         from_=TWILIO_NUMBER,
                                         body='Good luck on your Twilio quest!')

    # Return a message indicating the text message is enroute
    return 'Message on the way!'

@app.route('/incoming/sms', methods=['POST', 'GET'])
def sms_handler():
    rv = """<Response>
        <Sms>I just responded to a text message. Huzzah!</Sms>
    </Response>"""
    # Send a text message to the number provided
    # Return a message indicating the text message is enroute
    return rv

# Handle a POST request to make an outbound call. This is called via ajax
# on our web page
@app.route('/incoming/call', methods=['POST', 'GET'])
def call():
    # Make an outbound call to the provided number from your Twilio number
    #request.form["Digits"]
    rv = """<Response>
    <Gather action="/incoming/called" timeout="10" finishOnKey="*">
        <Say>Press 1 to record a message, press 2 to play the previously recorded message</Say>
    </Gather></Response>"""
    # Return a message indicating the call is coming
    return rv
    
@app.route('/incoming/called', methods=['POST', 'GET'])
def called():
    digits = request.form["Digits"]
    if digits == "1":
        rv = """<Response>
            <Say>Please record after the beep. Press STAR when you are finished.</Say>
            <Record playBeep='True' maxLength="60" timeout="10" transcribe="true" finishOnKey="*"/>
        </Response>"""
        return rv
    elif digits == "2":
        recordings = client.recordings.list()
        rsp = """<Response>"""
        for recording in recordings:
            rsp += """<Play>%s</Play>"""%recording.uri
        rv = """<Response>
        <Say>Here are the previously recorded messages.</Say>
        <Play>
        </Response>"""
        rsp += "</Response>"
        return rsp
    if request.form['RecordingUrl']:
        return """<Response><Say>You recorded a message.</Say></Response>"""
    # Send a text message to the number provided
    # Return a message indicating the text message is enroute
    

# Generate TwiML instructions for an outbound call
@app.route('/hello')
def hello():
    response = twiml.Response()
    response.say('Hello there! You have successfully configured a web hook.')
    response.say('Good luck on your Twilio quest!', voice='woman')
    return Response(str(response), mimetype='text/xml')

if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)