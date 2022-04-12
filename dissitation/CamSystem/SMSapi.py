import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'ACf88ce8a625d86341b538ab617611c8ae'
auth_token = '11b1159333c9ff56b123998d3f4d17da'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Alert person has been detected in living room at 15:43",
                     from_='+14404968162',
                     to='+447470 426038'
                 )

print(message.sid)