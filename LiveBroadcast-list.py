#!/usr/bin/python

import httplib2
import os
import sys

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
CLIENT_SECRETS_FILE = "client_secrets.json"

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

VALID_BROADCAST_STATUSES = ("all", "active", "completed", "upcoming",)

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
    part="id,snippet",
    maxResults=50
  )

  while list_broadcasts_request:
    list_broadcasts_response = list_broadcasts_request.execute()

    for broadcast in list_broadcasts_response.get("items", []):
      print "%s (%s)" % (broadcast["snippet"]["title"], broadcast["id"])

    list_broadcasts_request = youtube.liveBroadcasts().list_next(
      list_broadcasts_request, list_broadcasts_response)

if __name__ == "__main__":
  argparser.add_argument("--broadcast-status", help="Broadcast status",
    choices=VALID_BROADCAST_STATUSES, default=VALID_BROADCAST_STATUSES[0])
  args = argparser.parse_args()

  youtube = get_authenticated_service(args)
  try:
    list_broadcasts(youtube, args.broadcast_status)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
