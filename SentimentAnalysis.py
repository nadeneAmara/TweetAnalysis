import twitter

# initialize API instance
twitter_api = twitter.Api(consumer_key= 'TXX58RuQCDKrR6WKOrDSuhhTp',
						 consumer_secret= 'llAoZ4hA0HPOUg3wVhLVL5beULvn9nYkmrErhB1YaxwXzpm9od',
						 access_token_key= '4635485808-5TgOrcP6MPM6mWxHygSM9KR8YNLAryWFlDs1S2c',
						 access_token_secret= 'c0XtZEzEBGsW1I0PzbdX4Y1k3ZgmMj82mMSvrIz4dSo1r')

def buildTestSet(search_keyword): 
	try:
		tweets_returned = twitter_api.GetSearch(search_keyword, count = 100)
		print("Returned" + str(len(tweets_returned)) + " tweets for the term " + search_keyword)

		return [{"text":status.text, "label":None} for status in tweets_returned]

	except:
		print("Something went wrong")
		return None
