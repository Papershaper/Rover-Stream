#!/usr/bin/python

import httplib2
import os
import sys

from time import sleep

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow



# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_id.json"

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_BROADCAST_STATUSES = ("all", "active", "completed", "upcoming")

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_READONLY_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

# Retrieve a list of broadcasts with the specified status.
def list_broadcasts(youtube, broadcast_status):
  print "Broadcasts with status '%s':" % broadcast_status

  list_broadcasts_request = youtube.liveBroadcasts().list(
    broadcastStatus=broadcast_status,
    broadcastType="all",
    part="id,snippet",
    maxResults=50
  )
   
  while list_broadcasts_request:
    list_broadcasts_response = list_broadcasts_request.execute()
       
    for broadcast in list_broadcasts_response.get("items", []):
		print "Cast:  %s (%s)" % (broadcast["snippet"]["title"], broadcast["id"])
		print "published@ %s" % (broadcast["snippet"]["publishedAt"])
		if "liveChatId" in broadcast["snippet"]:
			print "liveChatId@ %s" % (broadcast["snippet"]["liveChatId"])


    list_broadcasts_request = youtube.liveBroadcasts().list_next(
      list_broadcasts_request, list_broadcasts_response)

# Just get the active Live Chat ID
def get_liveChatId(youtube, broadcast_status="all"):
    list_broadcasts_request = youtube.liveBroadcasts().list(
        broadcastStatus=broadcast_status,
        broadcastType="all",
        part="snippet,id",
        maxResults=50
    )

    list_broadcasts_response = list_broadcasts_request.execute()
    casts = list_broadcasts_response.get("items", [])
    for cast in casts:
        if "liveChatId" in cast['snippet']:
            print "Found live Chat ID: %s" % (cast['snippet']['liveChatId'])
            return cast['snippet']['liveChatId']

#for when your ready to insert
def insert_message(youtube, live_chat_id, message):
    list_streams_request = youtube.liveChatMessages().insert(
        part="snippet",
        body=dict(
          snippet=dict(
            liveChatId=live_chat_id,
            type="textMessageEvent",
            textMessageDetails=dict(
              messageText=message
            )
          ),
        )
    ).execute()

#return a list of messages
def get_list_messages(youtube, liveChatId, pageToken=None):
    if (pageToken):
        list_messages_request = youtube.liveChatMessages().list(
            liveChatId=liveChatId,
            part="id,snippet,authorDetails",
            pageToken=pageToken,
        )
    else:
        list_messages_request = youtube.liveChatMessages().list(
            liveChatId=liveChatId,
            part="id,snippet,authorDetails",
        )
    while list_messages_request:
        list_messages_reponse = list_messages_request.execute()
        return list_messages_reponse

#harvest the messages
def harvest_messages(youtube, liveChatId):
	nextPageToken = None;
	prevMessage = None;
	isActive = True
	while isActive:
		response = get_list_messages(youtube, liveChatId, nextPageToken)

		nextPageToken = response['nextPageToken']
		pollingIntervalInMillis = response['pollingIntervalMillis']
		pollingIntervaLInSeconds = pollingIntervalInMillis/1000
		messages = response.get("items", [])
		for message in messages:
			print "Message:  "+message['authorDetails']['displayName']+" "+message['snippet']['displayMessage']
			if (message['snippet']['displayMessage'] == "##"):
				isActive = False
		print "Time:polling interval in Seconds: " + str(pollingIntervaLInSeconds)
		sleep(pollingIntervaLInSeconds)

if __name__ == "__main__":
  #argparser.add_argument("--broadcast-status", help="Broadcast status",
    #choices=VALID_BROADCAST_STATUSES, default=VALID_BROADCAST_STATUSES[0])
  args = argparser.parse_args()

  print "Start You Tube Chat"
  liveChatId = None

  youtube = get_authenticated_service(args)
  try:
	#list the broadcasts available
    list_broadcasts(youtube, "all")
    #find the active broadcast, and return liveChatID
    liveChatId = get_liveChatId(youtube)
    #list the liveChatMessages - owner and text
    if liveChatId is not None:
		print "Harvest Messages for :" + liveChatId
		harvest_messages(youtube, liveChatId)
		
  except HttpError, e:
    print "ERROR:  the API call- HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
