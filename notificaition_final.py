#!/usr/bin/env python
from datetime import datetime, timedelta
import pytz
import json
import requests
from exchangelib import Q
import re
from exchangelib import Credentials, Account, DELEGATE, EWSDateTime

# Set up the Exchange server account
credentials = Credentials('noc@digikala.com', '')
account = Account(primary_smtp_address='noc@digikala.com', credentials=credentials, autodiscover=True, access_type=DELEGATE)

# Get the timezone for the Exchange server (replace 'America/New_York' with the correct timezone)
exchange_tz = pytz.timezone('Asia/Tehran')

# Calculate the date and time 2 days ago in the server's timezone
start_date = datetime.now(exchange_tz) - timedelta(days=2)

# Create a timezone-aware EWSDateTime object
start_datetime = EWSDateTime.from_datetime(start_date.astimezone(pytz.utc))



# Fetch unread emails from the last 2 days
for item in account.inbox.filter(Q(datetime_received__gt=start_datetime) & Q(is_read=False)):    
    email_subject = item.subject
    email_sender = item.sender.email_address
    email_text = item.text_body
    email_date = item.datetime_received
    # Prepare the message for Slack

    formatted_date = email_date.astimezone(exchange_tz).strftime('%Y-%m-%d %H:%M:%S')
    clean_email_text = re.sub(r'\[LOGO\].*?\[\/LOGO\]', '', email_text)  # Remove logo tags
    clean_email_text = re.sub(r'<a.*?/a>', '', clean_email_text)  # Remove attached links
    # Send the message to Slack
    slack_data = {
        "attachments": [
            {
                "color": "#A020F0",
                "username": "NOC-Bot",
                "icon_emoji": ":bell:",
                "channel": 'mail-notification',
                "text": f"*New Email Received From*: {email_sender}\n*Subject*: {email_subject}\n*Date*: {formatted_date}\n```{email_text}```"
            }
        ]
    }    
    # Send the message to Slack
    webhook_url = 'https://hooks.slack.com/services/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'
    headers = {'Content-Type': "application/json"}
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers=headers)

    # Check the response from the Slack API
    if response.status_code == 200:
        print("Message sent successfully to Slack")
    else:
        print(f"Failed to send message to Slack. Status code: {response.status_code}, Response: {response.text}")
