# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Prediction API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
import pprint
import time

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/52127403658/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/devstorage.full_control',
      'https://www.googleapis.com/auth/devstorage.read_only',
      'https://www.googleapis.com/auth/devstorage.read_write',
      'https://www.googleapis.com/auth/prediction',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):

  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  print credentials

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Prediction API.
  service = discovery.build('prediction', 'v1.6', http=http)  

  tm = service.trainedmodels()

  # instert
  body = {'id':'twitteridentifier', 'storageDataLocation':'cis192_prediction_test/test.csv'}
  request = tm.insert(project=52127403658, body=body)
  response = request.execute()
  pprint.pprint(response)

  # wait for the training to complete
  while True:
    status = tm.get(project=52127403658, id='twitteridentifier').execute()
    state = status['trainingStatus']
    print 'Training state: ' + state
    if state == 'DONE':
      break
    elif state == 'RUNNING':
      time.sleep(20)
      continue
    else:
      raise Exception('Training Error: ' + state)

    # Job has completed.
    print 'Training completed:'
    pprint.pprint(status)
    break

  # make a prediction
  body = {'input':{'csvInstance':['i love scrubbing']}}
  request = tm.predict(project=52127403658, id='twitteridentifier', body=body)
  response = request.execute()
  pprint.pprint(response)


# For more information on the Prediction API you can visit:
#
#   https://developers.google.com/prediction/docs/developer-guide
#
# For more information on the Prediction API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/prediction/v1.6/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)
