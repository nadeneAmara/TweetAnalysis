import twitter
import csv
import time

import nltk
import re
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.classify import apply_features
from string import punctuation 

# initialize API instance
twitter_api = twitter.Api(consumer_key= 'TXX58RuQCDKrR6WKOrDSuhhTp',
						 consumer_secret= 'llAoZ4hA0HPOUg3wVhLVL5beULvn9nYkmrErhB1YaxwXzpm9od',
						 access_token_key= '4635485808-5TgOrcP6MPM6mWxHygSM9KR8YNLAryWFlDs1S2c',
						 access_token_secret= 'c0XtZEzEBGsW1I0PzbdX4Y1k3ZgmMj82mMSvrIz4dSo1r')

def buildTestSet(search_keyword): 
	try:
		tweets_returned = twitter_api.GetSearch(search_keyword, count = 100)
		print("Returned " + str(len(tweets_returned)) + " tweets for the term " + search_keyword)

		return [{"text":status.text, "label":None} for status in tweets_returned]

	except:
		print("Something went wrong")
		return None

search_term = input("Enter a search keyword:")
testDataSet = buildTestSet(search_term)
print(testDataSet[0:4])

def buildTrainingSet(corpusFile, tweetDataFile):

	corpus = []

	with open(corpusFile, 'r') as csvfile:
		lineReader = csv.reader(csvfile, delimiter=',', quotechar="\"")
		for row in lineReader:
			corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})

	# max number of requests = 180, time window = 900s
	rate = 180
	sleep_time = 900/180

	trainingDataSet = []

    # using tweet id, get tweet text and store in training set
	for tweet in corpus:
		try:
			status = twitter_api.GetStatus(tweet["tweet_id"])
			print("Tweet returned " + status.text)
			tweet["text"] = status.text
			trainingDataSet.append(tweet)
			time.sleep(sleep_time)
		except:
			continue 

	# write to CSV file		
	with open(tweetDataFile, 'w') as csv_file:
		lineWriter = csv.writer(csv_file, delimiter=',',quotechar="\"")
		for tweet in trainingDataSet:
			try:
				lineWriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
			except Exception as e:
				print(e)
	return trainingDataSet

	
corpusFile = "/Users/nadeneabuamara/Downloads/corpus.csv"
tweetDataFile = "/Users/nadeneabuamara/Downloads/TweetAnalysis/tweetDataFile.csv"
trainingData = buildTrainingSet(corpusFile, tweetDataFile)

class PreProcessTweets:

	def __init__(self):
		self.stop_words = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])

	def getProcessedTweets(self, tweetList):
		processedTweets = []
		for tweet in tweetList:
			processedTweets.append((self.processTweet(tweet["text"]), tweet["label"]))
		return processedTweets

	def processTweet(self, tweet):
		tweet = tweet.lower() # make tweets lowercase
		tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
		tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
		tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in hashtag
		tweet = word_tokenize(tweet)
		return [word for word in tweet if word not in self.stop_words]


tweetPreProcessor = PreProcessTweets()
preProcessedTrainingSet = tweetPreProcessor.getProcessedTweets(trainingData)
preProcessedTestSet = tweetPreProcessor.getProcessedTweets(testDataSet)

def buildVocabulary(preProcessedTrainingSet):
	word_list = []
	# Add training tweet words to list
	for (words, sentiment) in preProcessedTrainingSet:
		word_list.extend(words)

	wordlist = nltk.FreqDist(word_list)
	# Key is frequency with which word shows up
	word_features = wordlist.keys()

	return word_features

def extract_features(tweet):
	tweet_text = set(tweet)
	features = {}
	# if word is in vocab, give label of 1, else 0
	for word in word_features:
		features['contains(%s' %word] = (word in tweet_text)
	return features

# Build feature vector
word_features = buildVocabulary(preProcessedTrainingSet)
trainingFeatures = apply_features(extract_features, preProcessedTrainingSet)

NBayesClassifier = nltk.NaiveBayesClassifier.train(trainingFeatures)
