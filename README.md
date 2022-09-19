# Twitter Bot - [@GeriPapers](https://twitter.com/geripapers) 
_Developed by [Oscar Ponce](https://twitter.com/PonceOJ) and [Eloy Ruiz](https://twitter.com/RuizEF)_


This Twitter bot that has 3 functions:
1. Tweets the latest research articles in Geriatric Medicine recently indexed in [PubMed](https://pubmed.ncbi.nlm.nih.gov)
2. Tweets the research article that has had the highest attention on the internet ([Altmetric Attention Scores](https://www.altmetric.com/about-altmetrics/what-are-altmetrics/)
3. Retweets any tweet with the hashtags #Geripapers #GeriTwitter and #GeriJC

## Requirements
- [Biopython](https://biopython.org)
- [Tweepy](https://www.tweepy.org)
- [Altmetric](https://pypi.org/project/altmetric/)
- [Pandas](https://pandas.pydata.org)
- [Requests](https://pypi.org/project/requests/)


  
## Setting up Twitter API Access
Create a new Twitter Account ([@GeriPapers](https://twitter.com/geripapers)) and through the [Twitter Developer Portal](https://developer.twitter.com/) apply to **Elevated Access** for **Twitter API V2**.

## [```config.py```](https://github.com/ponceoscarj/geripapers/blob/main/config.py)
Save all API keys, tokens, emails, and usernames in ```config.py```.


## [```pubmed.py```](https://github.com/ponceoscarj/geripapers/blob/main/pubmed.py)
This ```script``` will search in [PubMed](https://pubmed.ncbi.nlm.nih.gov) the latest research articles in Geriatric Medicine and will Tweet one article every 20 minutes. The file utilises a search strategy available in [```line 140```](https://github.com/ponceoscarj/geripapers/blob/48a101c7adf3eaffb97e41655690a3487b650d34/pubmed.py#L140). 

Every Tweet will have the following information ([Example](https://twitter.com/geripapers/status/1571766417753513987?s=20&t=WD5EIugTsibiIV21UT4Jtg)):
- Research article title 
- PubMed Link
- The hashtag #Geripapers

Every research article identifier that has been tweeted, namely **PMID** ([What is a PMID?](https://uwyo.libanswers.com/faq/176930)), will be added to a ```.txt``` file called [```pmid_db.txt```](https://github.com/ponceoscarj/geripapers/blob/main/pmid_db.txt). You can find this file in this repository as example.


## [```geripapers_altmetric.py```](https://github.com/ponceoscarj/geripapers/blob/main/geripapers_altmetric.py)
Every week, this ```script``` will use the ```pmid_db.txt``` file and retrieve every article's [Altmetric Attention Scores](https://www.altmetric.com/about-altmetrics/what-are-altmetrics/). This score reflects how much attention the article has received throughout the internet; the higher the score the higher the online attention the paper had. After retrieving all Altemtric Attention Scores, it will select the **PMID** with the highest score and create a thread about it ([Example](https://twitter.com/geripapers/status/1571382608289992704?s=20&t=WD5EIugTsibiIV21UT4Jtg)).


## [```hashtag_reteweet.py```](https://github.com/ponceoscarj/geripapers/blob/main/hashtag_reteweet.py)
This ```file``` finds and retweets all tweets containing the following hashtags #Geripapers, #GeriTwitter, and #Gerijc. However, it excludes retweets, quoted tweets and tweets generated by @GeriPapers](https://twitter.com/geripapers). 


## [Pythonanywhere](https://www.pythonanywhere.com/)
We use this web hosting service to execute all scripts regularly. 

The following ```python scripts``` are run as [Always-on Tasks](https://help.pythonanywhere.com/pages/AlwaysOnTasks/):
- [```pubmed.py```](https://github.com/ponceoscarj/geripapers/blob/main/pubmed.py)
- [```hashtag_reteweet.py```](https://github.com/ponceoscarj/geripapers/blob/main/hashtag_reteweet.py)

The following python files are run as 24-hour/Daily [Scheduled Tasks](https://help.pythonanywhere.com/pages/ScheduledTasks/):
- [```geripapers_altmetric.py```](https://github.com/ponceoscarj/geripapers/blob/main/geripapers_altmetric.py): _Although this python file is run everyday, bear in mind that the script itself has a conditional statement that allows it to run only once a week_
- [```pythonanywhere_api.py```](https://github.com/ponceoscarj/geripapers/blob/main/pythonanywhere_api.py): _Although ```pubmed.py``` is continuously run, we make sure the search we use is run everyday to capture new articles._

