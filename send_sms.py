# we import the Twilio client from the dependency we just installed
# from twilio.rest import TwilioRestClient
from twilio.rest import Client


def send_text(message):
    # the following line needs your Twilio Account SID and Auth Token
    client = Client("AC3e84e9cae2390af9a661c1ab35955444", "4a8bf26cb30107ec85d98f6bf1182522")

    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to="+15129146948", from_="+17372105122",
                           body=message)
if __name__ == '__main__':
    send_text('Hello, this is a test.')