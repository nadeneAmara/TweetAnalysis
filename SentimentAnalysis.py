import twitter

# initialize API instance
twitter_api = twitter.Api(consumer_key= TXX58RuQCDKrR6WKOrDSuhhTp,
						 consumer_secret= llAoZ4hA0HPOUg3wVhLVL5beULvn9nYkmrErhB1YaxwXzpm9od,
						 access_token_key= 4635485808-5TgOrcP6MPM6mWxHygSM9KR8YNLAryWFlDs1S2c,
						 access_token_secret= c0XtZEzEBGsW1I0PzbdX4Y1k3ZgmMj82mMSvrIz4dSo1r)

# test authentication
print(twitter_api.VerifyCredentials())