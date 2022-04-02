#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 10:42:10 2022
Last edit on Sat Apr 2 13:26:00 2022

@author: Giulio Gabrieli
"""

#import required libraries
import os
import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import numpy as np 
from tqdm import tqdm

#dictionary to convert months from italian to english. Required to make
#standardized timestamps
months_dict = {'Gennaio':'January','Febbraio':'February','Marzo':'March', 
               'Aprile' : 'April','Maggio':'May','Giugno':'June','Luglio':'July',
               'Agosto':'August','Settembre':'September','Ottobre':'October',
               'Novembre':'November','Dicembre':'December'}

#PARAMETERS
FIRSTPAGE = 1 #unless the developer was drunk, this shouldbe 1
BASEPATH = '/home/giulio/Repositories/ukrainenewsscraper'
RAWPATH = BASEPATH + os.sep + 'Raw' + os.sep #Path to raw data folder
BASEURL = 'https://www.open.online/temi/ucraina/page/' #URL to scrape
DB = RAWPATH+'Open/open.csv' #name of the database

if(__name__ == '__main__'):
    print('Initializing scraper for Open Online') 

    #check if the database is already present, otherwise initialize an empty dataframe
    if not os.path.exists(DB):
        print('Database not present in ',DB)
        print('Initializing empty dataframe')
        df = pd.DataFrame([], columns=['ID','Title','url','Date'])
    else:      
        print('Database present in',DB)
        df = pd.read_csv(DB)
        print('Database contains',len(df), 'articles')
        
    print('Starting Download of news\' details (ID, url, Title, Date)')

    #initialize data array and set the page counter
    page = FIRSTPAGE
    data = []
    
    #initialize the download control
    download = True
    
    #while donwload is true, loop the pages and get article details
    while download:
        print('Scraping page:', page)
        url = BASEURL + str(page) # generates the URL
        r = requests.get(url) #request the URL
        
        if(r.status_code == 200): #Verify if the page exists
            html = r.text #get the HTML of the page
             
            soup = BeautifulSoup(html, 'html.parser') #initialize the parser
            
    
            articles = [x for x in soup.find_all('article') if x.get('id') not in df.ID.to_list()]
            
            toupdate = []
            for article in soup.find_all('article'):
                if('news' in article.get('class')):
                    newsDay = article.find(class_="news__date-day").text[1:] #get the day
                    newsTime = article.find(class_="news__date-time").text.replace('- ','') #get the time
                    #translate the month from italian to english
                    for key in months_dict.keys():
                        newsDay = newsDay.replace(key, months_dict[key])
                    timestring = newsDay + newsTime #generates the string
                    #and convert from string to datetime format
                    newsDate = datetime.datetime.strptime(timestring, '%d %B %Y %H:%M')
                    newsDate = newsDate.strftime('%Y-%m-%d %H:%M:%S')
                    if len(df[(df.ID == article.get('id')) & (df.Date != newsDate)]):
                        print('One article', article.get('id'), 'removed. An updated version has been posted.')
                        df = df.drop(df[(df.ID == article.get('id')) & (df.Date != newsDate)].index)
                        articles.append(article)

            if(len(articles) > 0):
                for article in articles: #for each article element in the page
                    if('news' in article.get('class')):
                        newsID = article.get('id') #unique identifier of the news
                        #get the other details 
                        newsTitle = article.h2.text.replace('\n','')
                        newsUrl = article.a.get('href')
                        newsDay = article.find(class_="news__date-day").text[1:] #get the day
                        newsTime = article.find(class_="news__date-time").text.replace('- ','') #get the time
                        #translate the month from italian to english
                        for key in months_dict.keys():
                            newsDay = newsDay.replace(key, months_dict[key])
                        timestring = newsDay + newsTime #generates the string
                        #and convert from string to datetime format
                        newsDate = datetime.datetime.strptime(timestring, '%d %B %Y %H:%M')
                        data.append([newsID, newsTitle, newsUrl, newsDate]) #temporarily save the date in data
            else:
                download = False
                
            page +=1 #update the page number
        else:
            #if the status code of the page is not 200 stop the scraper, we have reached the last page contaning news
            download = False

    #create or update the database
    print(len(data), 'new articles added to the database')
    if(len(data) > 0):
        df = df.append(pd.DataFrame(data, columns=['ID','Title','url','Date']))   
        if not os.path.exists(RAWPATH + 'Open'):
            os.mkdir(RAWPATH + 'Open')
            
        df = df.sort_values(by='Date', ascending=False)
        df.to_csv(DB, index = False)
    
        print('Database saved open.csv in',RAWPATH+'Open')    
    
    #create the article folder if it is not present
    if not os.path.exists(RAWPATH + 'Open/Articles'):
        os.mkdir(RAWPATH + 'Open/Articles')
    
    #limit to the articles that are not present in the article folder
    todowload = df[~df.ID.isin([x.replace('.txt', '') for x in os.listdir(RAWPATH + 'Open/Articles')])]
    print('There are',len(todowload),'new articles to download')
    
    #if there are new articles to download
    if(len(todowload) > 0):
        #get article ID and url
        for ID, url in tqdm(np.transpose([todowload.ID.to_list(), todowload.url.to_list()])):
            r = requests.get(url) #get the page
            if(r.status_code == 200): #check the status code
                html = r.text #get the html
                soup = BeautifulSoup(html, 'html.parser') #initialize the parser
                title = soup.article.h1.text #get the title
                elements = [element.text for element in soup.findAll(['p','h2'])] #get all the elements of the article
                text = title  + '\n' + '\n' + '\n'.join(elements[:-2]) #merge title and other elements
                
                #Write the news to a text file. name of the file is the ID of te news
                myText = open(RAWPATH + 'Open/Articles/' + ID + '.txt','w')
                myText.write(text)
                myText.close()
            else:
                #if the status code of the page is not 200 skip this news. URL may be wrong
                print(ID,'Skipped. Status Code:',r.status_code)