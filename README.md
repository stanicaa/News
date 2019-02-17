# News
News parsing, searching. There are 3 programs here: news_rss.py is checking and building your personal news DB (mysql used), latest.py is presenting you with the latest keywords in the news for the day. Reader_project folder is a django implementation of this concept, where users can create their own news streams, set up their own news feeds that want to follow.

The programs is using feedparser (https://pythonhosted.org/feedparser/) to go through various feeds aroundthe world, and save them in a personal database for future usgae. You can then use latest.py to have an overall presentation of what have been the latest keywords.

The examples are on an "as is" basis, and are meant to be just an example - not necessarily the most efficient code implementation here.
