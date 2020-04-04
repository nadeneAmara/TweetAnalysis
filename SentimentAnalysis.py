import twitter
import csv
import time
import os.path
import random
import json

import nltk
import re
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.classify import apply_features
from string import punctuation 

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
import numpy as np


# initialize API instance
twitter_api = twitter.Api(consumer_key= 'TXX58RuQCDKrR6WKOrDSuhhTp',
                         consumer_secret= 'llAoZ4hA0HPOUg3wVhLVL5beULvn9nYkmrErhB1YaxwXzpm9od',
                         access_token_key= '4635485808-5TgOrcP6MPM6mWxHygSM9KR8YNLAryWFlDs1S2c',
                         access_token_secret= 'c0XtZEzEBGsW1I0PzbdX4Y1k3ZgmMj82mMSvrIz4dSo1r')


def buildTrainingSet(corpusFile, tweetDataFile):

    # If training data file already exists, directly read from file
    if os.path.isfile(tweetDataFile):
        trainingDataSet = []
        with open(tweetDataFile, 'r') as tweetData:
            line_Reader = csv.reader(tweetData, delimiter=',', quotechar="\"")
            for row in line_Reader:
                trainingDataSet.append({"tweet_id":row[0], "text":row[1], "airline_sentiment":row[2], "airline":row[3]})

        return trainingDataSet

    # Otherwise, gather tweet data using corpus file
    else:

        corpus = []

        with open(corpusFile, 'r') as csvfile:
            lineReader = csv.reader(csvfile, delimiter=',', quotechar="\"")
            for row in lineReader:
                corpus.append({"tweet_id":row[0], "airline_sentiment":row[1], "airline":row[5]})

        # max number of requests = 180, time window = 900s
        rate = 180
        sleep_time = 900/180

        trainingDataSet = []
        counter = 5

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
                    lineWriter.writerow([tweet["tweet_id"], tweet["text"], tweet["airline_sentiment"], tweet["airline"]])
                except Exception as e:
                    print(e)

        return trainingDataSet


#corpusFile = "/Users/nadeneabuamara/Downloads/corpus.csv"
#tweetDataFile = "/Users/nadeneabuamara/Downloads/TweetAnalysis/tweetDataFile.csv"
corpusFile = "/Users/nadeneabuamara/Downloads/twitter-airline-sentiment/Tweets.csv"
tweetDataFile = "/Users/nadeneabuamara/Downloads/twitter-airline-sentiment/tweetDataFile.csv"
trainingData = buildTrainingSet(corpusFile, tweetDataFile)


class PreProcessTweets:

    def __init__(self):
        self.stop_words = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])

    def getProcessedTweets(self, tweetList):
        processedTweets = []
        for tweet in tweetList:
            #tweet["text"] = " ".join(w for w in nltk.wordpunct_tokenize(tweet["text"]) if w.lower() in words or not w.isalpha())
            processedTweets.append((self.processTweet(tweet["text"]), tweet.get("airline_sentiment")))
        return processedTweets

        #processedTweets = dict()
        #for tweet in tweetList:
           # processedTweets.update({(self.processTweet(tweet["text"])) : tweet.get("airline_sentiment")})

    def processTweet(self, tweet):
        tweet = tweet.lower() # make tweets lowercase
        tweet = re.sub(r'[0-9\.]+', '', tweet) # remove numbers
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in hashtag
        tweet = word_tokenize(tweet)
        tweetArray = [word for word in tweet if word not in self.stop_words]
        tweet = " ".join(tweetArray)
        return tweet


tweetPreProcessor = PreProcessTweets()
preProcessedTrainingSet = tweetPreProcessor.getProcessedTweets(trainingData)
preProcessedTestSet = tweetPreProcessor.getProcessedTweets(testDataSet)

random.shuffle(preProcessedTrainingSet)
# Separate tweets from labels
tweetList = []
labelList = []
for (words, sentiment) in preProcessedTrainingSet:
    tweetList.append(words)
    labelList.append(sentiment)

vectorizer = CountVectorizer(binary=True, lowercase=True)
total = vectorizer.fit_transform((np.array(tweetList)))

tweetTrain, tweetTest, labelTrain, labelTest = train_test_split(total, labelList, test_size=0.2, random_state=0)
model = GaussianNB()
model.fit(tweetTrain.toarray(), labelTrain)

predicted_sentiment = model.predict(tweetTest.toarray())



