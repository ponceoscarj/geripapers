from altmetric import Altmetric, AltmetricHTTPException
import pandas as pd
import time
import os.path
import tweepy
import datetime
import config


def main_file_to_list(main_database):
    """
    Takes the overall database with PMIDs already tweeted by the bot and transforms it into a list
    INPUT : main database name - it should be 'pmid_db.txt'
    OUPUT : pmid_db_list - list of PMIDs that have been tweeted so far
    """
    today = time.strftime("%d_%m_%Y")

    with open(main_database, 'r') as main_file, open(f'{today}_pmid.txt', 'a') as copy_file:
        for line in main_file:
            copy_file.write(line)

    pmid_db_pd = pd.read_csv(f'{today}_pmid.txt', skip_blank_lines=True, header=None)
    pmid_db_list = pmid_db_pd[0].values.tolist()  # turns dataframe of PMIDs into a list of PMIDs

    return pmid_db_list


def altmetric_search(list_pmids):
    """
    Takes a list of PMIDs, searches Altmetric information of each PMID and saves it into a dataframe (Pandas)
    Altmetric info includes: https://api.altmetric.com/v1/doi/10.1038/480426a?callback=my_callback
    INPUT : list_pmids - list of PMIDs
    OUPUT : overall_database_pd - dataframe with all necessary info
    """
    today = time.strftime("%d_%m_%Y")
    a = Altmetric()

    # New list to
    overall_list = []

    # Iterating through List of PMIDs
    for i in list_pmids:
        try:
            rsp = a.pmid(str(i))
            if rsp is None:
                print("PMID not found")
            else:
                overall_list.append(rsp)
                print(rsp['pmid'], ': ', rsp['score'], ' - ', rsp['title'])
        except AltmetricHTTPException as e:
            if e.status_code == 403:
                print("You aren't authorized for this call")
            elif e.status_code == 420:
                print("You are being rate limited")
            elif e.status_code == 502:
                print("The API version you are using is currently down for maintenance.")
            elif e.status_code == 404:
                print("Invalid API function")
                print(e.msg)

    # Saving all information into a dataframe
    overall_database_pd = pd.json_normalize(overall_list)
    overall_database_pd.insert(0, "analysis_date", today)

    return overall_database_pd


def highest_altemtric_score(database_overall_df):
    """
    It needs a dataframe with all altmetric information for each PMID

    Checks whether "highest_altemtric_papers.csv" is in the system
    if not, passes the input dataframe to new_pd
    if it exists, takes all PMIDs already in the csv file and deletes them from the input dataframe and
    saves the new dataframe into new_pd

    From new_pd, searches the row that contains the PMID with the highest altmetric score and saves it into
    max_altmetric_score_row

    Checks again whether "highest_altemtric_papers.csv" is in the system
    if not, saves max_altmetric_score_row in the .csv
    if it exists, appends max_altmetric_score_row to the existing .csv file

    INPUT : database_overall_df - pd.df - dataframe with all altmetric information for each PMID
    OUPUT : 'highest_atlemtric_papers.csv' - a .csv file with PMIDs with the highest altmetric scores
    """
    # File to store all PMID with highest altmetric score
    output_file_name = 'highest_altmetric_papers.csv'

    # If CSV with highest altmetric scores not created
    if not os.path.exists(output_file_name):
        new_pd = database_overall_df
    else:
        # Reading highest score altmetrics already used in previous tweets
        altmetric_db = pd.read_csv('highest_altmetric_papers.csv')

        # PMID list of highest altmetric papers and to str
        altmetric_pmid_list = altmetric_db['pmid'].tolist()
        altmetric_pmid_list_str = [str(x) for x in altmetric_pmid_list]

        # new dataframe including all PMIDs from overall_database_pd but without altmetric_pmid_list_str
        new_pd = database_overall_df[~database_overall_df['pmid'].isin(altmetric_pmid_list_str)]

    # Finding the row with highest altmetric score
    max_altemtric_score_row = new_pd[new_pd.score == new_pd.score.max()]
    max_altemtric_score_row = max_altemtric_score_row.iloc[[0]]

    # Print the PMID title and its altmetric score
    # print(f'''\nTitle: {max_altemtric_score_row['title'].values} \nPMID: {max_altemtric_score_row['pmid'].values}''')

    # Save Altmetric database of a specific date - variable today - to CSV
    # new_pd.to_csv(f'{today}_analysis.csv') #Not saving this cause it's usually >5mb

    # Conditional statement -> if file exists create a new file with headers -> if not append without headers
    if not os.path.exists(output_file_name):
        return max_altemtric_score_row.to_csv(output_file_name, index=False), max_altemtric_score_row
    else:
        altmetric_db = pd.read_csv("highest_altmetric_papers.csv")
        altmetric_db_new = pd.concat([altmetric_db, max_altemtric_score_row], sort=False)
        return altmetric_db_new.to_csv(output_file_name, index=False), max_altemtric_score_row


def pubmed_search_individual(pmid):
    """
    Searches PMID in pubmed and retrieves PUBMED related information
    INPUT : pmid - a string
    OUPUT : my_record[0] - a 'Bio.Entrez.Parser.DictionaryElement'
    """
    from Bio import Entrez

    Entrez.email = config.pubmed_email
    Entrez.api_key = config.pubmed_api_key

    pmid_search = Entrez.esummary(db="pubmed", id=pmid)
    my_record = Entrez.read(pmid_search)

    return my_record[0]


if __name__ == '__main__':
    today = datetime.date.today()
    weekday = today.weekday()

    if weekday == 6:  # This conditional statement will let you run the file once week
        pmid_list = main_file_to_list('pmid_db.txt')  # Creates a list of all PMIDs used to date
        overall_pmid_altmetric_df = altmetric_search(pmid_list)  # Retrieves all altmetric info of each PMIDs
        csv_file, row_max_altmetric_score = highest_altemtric_score(overall_pmid_altmetric_df)

        # PMID with the highest altmetric score
        pmid = row_max_altmetric_score['pmid'].values[0]

        # Altmetric value of PMID with highest Altmetric score
        score = round(row_max_altmetric_score['score'].values[0])

        # Retrieves pubmed information for the PMID with the highest altmetric score
        my_pmid = pubmed_search_individual(pmid)
        # Storing pubmed information
        journal_name_short = my_pmid['Source']
        journal_name_full = my_pmid['FullJournalName']
        pub_date = my_pmid['PubDate']
        first_author_etal = my_pmid['AuthorList'][0] + " et al."
        title = my_pmid['Title']

        # PubMed Link to be used in the tweets
        pre_link_pmid = "http://pubmed.ncbi.nlm.nih.gov/"
        full_link_pmid = pre_link_pmid + pmid

        # Emojis and their codes for tweets
        party_emoji = u'\U0001f389'
        fire_emoji = u'\U0001f525'
        journal_emoji = u'\U0001f4f0'
        thread_emoji = u'\U0001F9F5'
        point_down_emoji_medium_tone = u"\U0001F447\U0001F3FD"
        bookmark_paper_emoji = u'\U0001f4d1'

        # Creating First tweet
        first_tweet = f'Check out the #Geripaper of the week! {party_emoji}{party_emoji}{party_emoji}\n' \
                      f'Of all the articles tweeted by @GeriPapers, the article by {first_author_etal} published in ' \
                      f'"{journal_name_short}" received the highest attention on the internet. ' \
                      f'Check it out {point_down_emoji_medium_tone} (1/3 {thread_emoji}) {full_link_pmid}'

        # Second tweet
        second_tweet = f'''We used the @Altmetric Attention Score to select the article with the highest online activity. This article's total score was {fire_emoji}{score}{fire_emoji} and was mentioned by:\n'''

        if 'cited_by_tweeters_count' in row_max_altmetric_score and pd.notna(
                row_max_altmetric_score['cited_by_tweeters_count'].values[0]):
            twitter = f'''{round(row_max_altmetric_score['cited_by_tweeters_count'].values[0])} Twitter users\n'''
            second_tweet += twitter

        if 'cited_by_fbwalls_count' in row_max_altmetric_score and pd.notna(
                row_max_altmetric_score['cited_by_fbwalls_count'].values[0]):
            facebook = f'''{round(row_max_altmetric_score['cited_by_fbwalls_count'].values[0])} Facebook users\n'''
            second_tweet += facebook

        if 'cited_by_msm_count' in row_max_altmetric_score.columns and pd.notna(
                row_max_altmetric_score['cited_by_msm_count'].values[0]):
            news_media = f'''{round(row_max_altmetric_score['cited_by_msm_count'].values[0])} News Media outlets\n'''
            second_tweet += news_media

        if 'cited_by_wikipedia_count' in row_max_altmetric_score.columns and pd.notna(
                row_max_altmetric_score['cited_by_wikipedia_count'].values[0]):
            wiki = f'''{round(row_max_altmetric_score['cited_by_wikipedia_count'].values[0])} Wikipedia pages\n'''
            second_tweet += wiki

        if 'cited_by_feeds_count' in row_max_altmetric_score.columns and pd.notna(
                row_max_altmetric_score['cited_by_feeds_count'].values[0]):
            blogs = f'''{round(row_max_altmetric_score['cited_by_feeds_count'].values[0])} Blogs\n'''
            second_tweet += blogs

        second_tweet += f'(2/3 {thread_emoji})'

        # Third tweet
        third_tweet = f'''Every week, @GeriPapers highlights a new research article in the field of Geriatrics that has received the highest attention on the internet. If you know any of the authors of this article, feel free to tag them. Stay tuned for next week's article {bookmark_paper_emoji}! (3/3 {thread_emoji})'''


        # Generating tweets for @GeriPapers
        auth = tweepy.OAuthHandler(config.api_key, config.api_key_secret)
        auth.set_access_token(config.access_token, config.access_token_secret)
        api = tweepy.API(auth)

        # First tweet
        original_tweet = api.update_status(status=first_tweet)
        # Second tweet
        tweet2 = api.update_status(status=second_tweet, in_reply_to_status_id=original_tweet.id,
                                   auto_populate_reply_metadata=True)
        # Third tweet
        tweet3 = api.update_status(status=third_tweet, in_reply_to_status_id=tweet2.id,
                                   auto_populate_reply_metadata=True)

    else:
        print('It is not Sunday')
