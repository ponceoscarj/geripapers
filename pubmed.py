import time
import re
import config


# This code is an adaptation of Maxime Borry's code - available on github.com/maxibor/PubTwitMed

def pubmed_search(search_term, nb_max_articles):
    '''
    Search Pubmed for the nb_max_articles most recent articles on the
    search_term subject.
    INPUT : Search Term(str) and nb_max_articles(int)
    OUPUT : Dictionnary of Lists ['PMID':['Title','First Author','PubDate']]
    '''
    from Bio import Entrez

    article_dictionary = {}
    Entrez.email = config.pubmed_email  # You can set up an API key with your ncbi account on www.ncbi.nlm.nih.gov
    Entrez.api_key = config.pubmed_api_key
    max_number_of_articles = nb_max_articles

    myhandle = Entrez.esearch(db="pubmed", term=search_term,
                              retmax=max_number_of_articles)
    my_record = Entrez.read(myhandle)
    my_list = my_record["IdList"]
    for article in range(0, len(my_list)):
        listId = my_list[article]
        my_secondary_handle = Entrez.esummary(db="pubmed", id=listId)
        my_record = Entrez.read(my_secondary_handle)
        one_article = my_record[0]
        try:
            article_dictionary[one_article["Id"]] = [re.sub(re.compile('<.*?>'), '', one_article["Title"]),
                                                     one_article["AuthorList"], one_article["PubDate"]]
        except:
            continue
        time.sleep(0.5)
        # break
    return article_dictionary


def pmid_tool(pmid, pmid_db):
    '''
    Gets a PMID in input, and check if it already in pmid_db.txt file.
    If yes returns "already", if not appends it to pmid_db.txt and returns the
    direct link to the publication
    INPUT :
    PMID_identifier (string)
    pmid_db(str): Path to pmid_db.txt file
    OUTPUT : PMID url
    EXAMPLE : pmid_tool ("35633251")
    '''

    def pmid_url_resolver(pmid):
        '''
        Gets a PMID in input and uses the dx.doi.org service to
        return article url
        INPUT : PMID(str)
        OUTPUT : PMID URL(str)
        EXAMPLE : pmid ("35633251")
        '''
        return "http://pubmed.ncbi.nlm.nih.gov/" + str(pmid)

    def pmid_checker(pmid_string, pmid_db):
        '''
        Gets a PMID in input, and check if it already in pmid_db.txt file.
        If yes, returns TRUE, if not, returns FALSE and DOI
        INPUT :
            PMID(str)
            pmid_db(str): Path to pmid_db.txt file
        OUTPUT : True/False(Bool)
        EXAMPLE : pmid_checker("35633251")
        '''
        pmid_list = []
        with open(pmid_db, "r") as pmid_db:
            for line in pmid_db:
                line = line.rstrip()
                pmid_list.append(line)
        if pmid_string in pmid_list:
            return True, "NA"
        elif pmid_string not in pmid_list:
            pmid_list.append(pmid_string)
            return False, pmid_string

    def pmid_appender(pmid_string, pmid_db):
        '''
        Appends PMID in pmid_db.txt
        INPUT :
            PMID(str)
            pmid_db(str): Path to PMID.txt file
        OUTPUT : None
        EXAMPLE : pmid_appender("35633251")
        '''
        with open(pmid_db, "a") as pmid_db:
            pmid_db.write(pmid_string + "\n")

    if not pmid_checker(pmid, pmid_db)[0]:
        pmid_appender(pmid_checker(pmid, pmid_db)[1], pmid_db)
        return pmid_url_resolver(pmid)
    else:
        return "already"


def string_shortener(string_to_shorten, max_size):
    '''
    Shortens titles strings that are more than max_size
    Returns shortened titled strings
    INPUT : title_string,max_size(str,int)
    OUPUT : shortened_title_string+"..."(str)
    EXAMPLE : title_shortener(title,40)
    '''
    if len(string_to_shorten) > max_size:
        return string_to_shorten[0:max_size] + "..."

    return string_to_shorten


def twitterbot(string_to_tweet, ck, cs, at, ats):
    '''
    Publish on twitter the string_to_tweet
    INPUT :
        string_to_tweet(str): text to tweet
        ck(str): Twitter consumer key
        cs(str): Twitter consumer secret
        at(str): Twitter access token
        ats(str): Twitter access token secret
    OUTPUT : None
    '''
    import tweepy
    login = tweepy.OAuthHandler(ck, cs)
    login.set_access_token(at, ats)
    this_api = tweepy.API(login)
    res = this_api.update_status(status=string_to_tweet)
    return res


if __name__ == '__main__':
    # Be wary when creating a search query for the BioPython "Entrez.esearch"
    # Tried to split the query line into multiple components but
    # it retrieves different results from setting up in one long line
    query = "((elderly[ti] OR ""old age""[ti] OR aging[ti] OR geriatric[ti] OR ""60 years""[ti] OR ""65 years""[ti] OR ""70 years""[ti] OR ""75 years""[ti] OR ""80 years""[ti] OR ""85 years""[ti] OR ""90 years""[ti] OR ""95 years""[ti] OR ""100 years""[ti] OR octogenarian*[ti] OR nonagenarian*[ti] OR older[ti] OR longevity[ti] OR ""parkinson's""[ti] OR dementia[ti] OR delirium[ti]) NOT (correction[ti] OR pediatric[ti] OR paediatric[ti] OR protocol[ti] OR comment[ti] OR editorial[pt] OR review[pt] OR Published Erratum[pt] OR rat[ti] OR anopheles[ti] OR egg*[ti] OR primate*[ti] OR fish[ti] OR catfish[ti] OR zebrafish[ti] rodent[ti] OR rats[ti] OR mouse[ti] OR mice[ti] OR soil[ti] OR vortexmatter[ti] OR ""vortex matter""[ti])) OR ((elderly[ti] OR ""old age""[ti] OR aging[ti] OR geriatric[ti] OR ""60 years""[ti] OR ""65 years""[ti] OR ""70 years""[ti] OR ""75 years""[ti] OR ""80 years""[ti] OR ""85 years""[ti] OR ""90 years""[ti] OR ""95 years""[ti] OR ""100 years""[ti] OR octogenarian*[ti] OR nonagenarian*[ti] OR older[ti] OR longevity[ti] OR ""parkinson's""[ti] OR dementia[ti] OR delirium[ti]) AND (""systematic review"" OR ""meta analysis"" OR ""meta analyses"" OR ""systematic search""[All fields]))"
    gerisearch = pubmed_search(query, 300)

    for article in gerisearch:
        unique_identifier = pmid_tool(article, "pmid_db.txt")
        if unique_identifier != "already":
            print(unique_identifier)
            print("PMID : ", article)
            print("URL : ", unique_identifier)
            print("Title : ", gerisearch[article][0].encode("utf-8").decode("utf-8"))
            print("Authors : ", gerisearch[article][1])
            print("PubDate : ", gerisearch[article][2])
            final_url = unique_identifier
            hashtag = f'#geripapers'  # Includes the #geripapers hashtag in each tweet
            try:
                almost_to_tweet = " " + hashtag + " " + final_url
                max_title_len = 280 - len(almost_to_tweet)
                final_title = string_shortener(
                    gerisearch[article][0].encode("utf-8").decode("utf-8"), max_title_len)
                text_to_tweet = final_title + almost_to_tweet
                print(text_to_tweet)
                print("tweet length :", len(text_to_tweet))
                print("= = = = = = = = = = =")
                twitterbot(text_to_tweet, config.api_key, config.api_key_secret, config.access_token,
                           config.access_token_secret)
                time.sleep(1200)  # 1200 seconds equals 20 minutes
            except Exception as e:
                print(e)
                continue
