#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import requests
import base64
from webapp2_extras import JSON as json
from google.appengine.api import files

API_KEY = "sERWOjmLUvqYAyYtMBIOSnTWy"
API_SECRET = "yhSCi56jXKhjNHbdeWiBfVPFcR42aJz8dMew4tQkqeIxF5GTOe"

request_token_url = "https://api.twitter.com/oauth2/token"
friends_url = "https://api.twitter.com/1.1/friends/list.json"
tweets_url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

def get_access_token():
	'''app-only authentication
	returns access token to make requests
	'''

	token = "Basic " + base64.b64encode("%s:%s" %(API_KEY, API_SECRET))
	data = {"grant_type": "client_credentials"}
	headers = {"Authorization": token,\
			   "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
	req = requests.post(request_token_url, data=data, headers=headers)

	access_token = "Bearer " + req.json()["access_token"]

	return access_token

def get_friends(token, screen_name, n):
	'''gets a list of n people the user with screen_name follows 
	stores ids in a list and returns it
	'''

	#get list of people you follow 
	params = {"count": n, "screen_name": screen_name}
	req = requests.get(friends_url, params=params, headers=token)
	friends = []
	
	try:
		friends_info= req.json()

		#check for rate limits
		if "errors" in friends_info:
			print friends_info["errors"]
		else:
			users = friends_info["users"]
			for u in users:
				friends.append(unicode(u["screen_name"]).encode("UTF-8"))
	except:
		print req.status_code

	return friends

def get_friend_tweets(token, friends, n):
	'''gets the most recent n tweets of your friends
	and saves it to csvfile
	'''
	tweets_list = []

	for friend in friends:
		params = {"count": n, "screen_name": friend}
		req = requests.get(tweets_url, params = params, headers=token)

		try:
			tweets = req.json()
			#check for rate limit
			if "errors" in tweets:
				print tweets["errors"]
			else:
				current_tweets = [friend]
				
				#append tweets to the list
				for t in tweets:
					current_tweets.append(unicode(t["text"]).encode("UTF-8"))

				#append [friend_name, tweet1, tweet2, ....] to tweets_list
				tweets_list.append(current_tweets)

		except:
			print req.status_code
			return 0

	#write results to Google Cloud Storage file with screen name as the label
	#and the tweets as the features	
	filename = '/gs/cis192_prediction_test/data.txt'
	writable_file_name = files.gs.create(filename, mime_type='application/octet-stream', acl='public-read')

	with files.open(writable_file_name, 'a') as f:
		for ft in tweets_list:
			for i in range(1, len(ft)):
		 		f.write(ft[0] + ', ' + ft[i])

	return tweets_list

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
            """
            <html> <body>
            <h1>Hello!</h1>
            <ul>
            """)

        # A form to allow the user to enter a twitter user's name
        self.response.out.write(
            """
            </ul>
            <form action="train" method="post">
              Twitter name: <input type="text" name="twitterName" />
              <input type="submit" value="Submit" />
            </form>
            </body> </html>
            """)

# Train Google Prediction model with the twitter user's friends' tweets
class TrainModel(webapp2.RequestHandler):
    def post(self):
    	twitterName = self.request.get('twitterName')

    	# Retrieve the user's friends tweets
    	headers = {"Authorization": get_access_token()}
		friends = get_friends(headers, "twhiddleston", 20)
		tweets = get_friend_tweets(headers, friends, 100)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/train', TrainModel)
], debug=True)
