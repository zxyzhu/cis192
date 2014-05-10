'''
Final project

Uses Facebook API to get statuses of friends and stores them 
to a csv file for use later

'''
import csv
import json
import requests
import base64

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
	req = requests.get(friends_url, params=params, headers=headers)
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

def get_friend_tweets(token, csvfile, friends, n):
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

	#write results to csv file with screen name as the label
	#and the tweets as the features		
	with open(csvfile, "w") as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		for ft in tweets_list:
			writer.writerow(ft)

	return tweets_list


def main():

	headers = {"Authorization": get_access_token()}
	friends = get_friends(headers, "fabzialous", 10)
	tweets = get_friend_tweets(headers, "test.csv", friends, 10)


if __name__ == "__main__":
    main()