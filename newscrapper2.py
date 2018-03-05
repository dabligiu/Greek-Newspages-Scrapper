import feedparser as fp
import json
import newspaper
from newspaper import Article
from time import mktime
from datetime import datetime
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
# Set the limit for number of articles to download
LIMIT = 2

data = {}
data['newspapers'] = {}

#filepath
script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
rel_path = "newspapers.json"
abs_file_path = os.path.join(script_dir, rel_path)
# Loads the JSON files with news sites
with open(abs_file_path) as data_file:
    companies = json.load(data_file)

count = 1
q = pd.DataFrame()
# Iterate through each news company
for company, value in companies.items():
    # If a RSS link is provided in the JSON file, this will be the first choice.
    # Reason for this is that, RSS feeds often give more consistent and correct data.
    # If you do not want to scrape from the RSS-feed, just leave the RSS attr empty in the JSON file.
    if 'rss' in value:
            d = fp.parse(value['rss'])
            print("Downloading articles from ", company)
            newsPaper = {
                "rss": value['rss'],
                "link": value['link'],
                "articles": []
            }
            for entry in d.entries:
                # Check if publish date is provided, if no the article is skipped.
                # This is done to keep consistency in the data and to keep the script from crashing.
                if hasattr(entry, 'published'):
                    if count > LIMIT:
                        break
                    article = {}
                    article['link'] = entry.link
                    article['Πηγή']  = company
                    date = entry.published_parsed
                    article['published'] = datetime.fromtimestamp(mktime(date)).isoformat()
                    try:
                        content = Article(entry.link)
                        content.download()
                        content.parse()
                    except Exception as e:
                        # If the download for some reason fails (ex. 404) the script will continue downloading
                        # the next article.
                        print(e)
                        print("continuing...")
                        continue
                    article['title'] = content.title
                    article['text'] = content.text
                    q1=pd.DataFrame(article, index=[0])
                    q=pd.concat([q,q1])
                    print(count, "articles downloaded from", company, ", url: ", entry.link)
                    count = count + 1
            count = 1
    elif company == "huffpost":
        print("Downloading articles from ", company)
        qn2= pd.DataFrame()
        qn={}
        #getting links from all pages
        for i in ["1","2","3","4","5"]:
            if count > LIMIT:
                break
            link= "https://www.huffingtonpost.gr/oikonomia/"+i
            page = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(page.text, "html.parser")
            name_box = soup.find_all("a", {"class":"card__link bN","href" : True})
            for link in name_box:
                if count > LIMIT:
                    break
                qn['link']=link.get('href')
                qn1=pd.DataFrame(qn, index=[0])
                qn2=pd.concat([qn2,qn1])
                newlink="https://www.huffingtonpost.gr"+qn2.iloc[0]['link']
                print(count, "articles downloaded from", company, ", url: ",newlink)
                count = count + 1
        count = 1
        continue
    else:
        print("no point \n")
script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
rel_path = "scripted.csv"
abs_file_path = os.path.join(script_dir, rel_path)
q.to_csv("scripted.csv", sep='*', encoding='utf-8',index=False)
