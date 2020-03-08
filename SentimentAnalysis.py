import twitter
import csv
import time

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

search_term = input("Enter a search keyword:")
testDataSet = buildTestSet(search_term)
print(testDataSet[0:4])

def buildTrainingSet(corpusFile, tweetDataFile):

	corpus = []

	with open(corpusFile, 'rb') as csvfile:
		lineReader = csv.reader(csvfile,delimiter=',', quotechar="\"")
		for row in lineReader:
			corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})

	# max number of requests = 180, time window = 900s
	rate = 180
	sleep_time = 900/180

	trainingDataSet = []

	for tweet in corpus:
		try:
			status = twitter_api.GetStatus(tweet["tweet_id"])
			print("Tweet returned" + status.text)
			tweet["text"] = status.text
			trainingDataSet.append(tweet)
			time.sleep(sleep_time)
		except:
			continue 

	# write to CSV file		
	with open(tweetDataFile, 'wb') as csv_file:
		lineWriter = csv.writer(csv_file, delimiter=',',quotechar="\"")
		for tweet in trainingDataSet:
			try:
				lineWriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
			except Exception as e:
				print(e)
	return trainingDataSet