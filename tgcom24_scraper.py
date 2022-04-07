#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Scraper for TGCOM24

Created on Sat Apr  2 10:42:10 2022
Last edit on Thurs Apr 7 12:30:00 2022

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
from bs4 import Comment
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
BASEURL = 'https://www.tgcom24.mediaset.it/d/crisi-ucraina' #URL to scrape
DB = RAWPATH+'TGCOM24/tgcom24.csv' #name of the database

if(__name__ == '__main__'):
    print('Initializing scraper for TGCOM24') 

    #check if the database is already present, otherwise initialize an empty dataframe
    if not os.path.exists(DB):
        print('Database not present in ',DB)
        print('Initializing empty dataframe')
        df = pd.DataFrame([], columns=['Type','Title','url','Date','Subtitle','Article'])
    else:      
        print('Database present in',DB)
        df = pd.read_csv(DB)
        print('Database contains',len(df), 'articles')
        
    print('Starting Download of news\' details (ID, url, Title, Date)')

    #initialize data array and set the page counter
    data = []
    
    url = BASEURL# generates the URL
    r = requests.get(url) #request the URL
    
    if(r.status_code == 200): #Verify if the page exists
        html = r.text #get the HTML of the page
         
        soup = BeautifulSoup(html, 'html.parser') #initialize the parser
    
        headers = soup.find_all(class_='container-5-cose')
        
        #get the list of indexed, one per day
        urlstocheck = [header.find('a').get('href') for header in headers]
        
        for dailyurl in tqdm(urlstocheck):
            r = requests.get(dailyurl) #request the URL
            if(r.status_code == 200):
                html = r.text #get the HTML of the page
                soup = BeautifulSoup(html, 'html.parser') #initialize the parser
                
                #get the daily summary
                title = soup.find('h1').text.replace('\n','').replace('\t','')          
                subtitle = soup.find('h2').text.replace('\n','').replace('\t','') 
                paragraph = soup.find(class_='txb_first_paragraph').text.replace('\n','').replace('\t','') 
                publicationDate = soup.find(class_='rt__ribbon').find('time').get('datetime')
                publicationDate = datetime.datetime.strptime(publicationDate, '%Y-%m-%dT%H:%M:%S')
                data.append(['summary', title, dailyurl, publicationDate.strftime('%Y-%m-%d %H:%M:%S'), subtitle,paragraph])
                
                #find the temporeale ID and number of pages
                temporeale = soup.find(class_='more').get('data-href').split('?')[0]
                
                comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                lastpage = int([x.replace(' ','') for x in comments if x.replace(' ','').startswith('totpage')][0].replace('totpage',''))
                
                for page in range(FIRSTPAGE, lastpage+1):
                    print(page)
                    r = requests.get('https://www.tgcom24.mediaset.it/'+temporeale+'?'+str(page))
                    if(r.status_code == 200):
                        html = r.text #get the HTML of the page
                        soup = BeautifulSoup(html, 'html.parser') #initialize the parser
                        
                        for article in soup.find('ul').find_all('li'):
                            try:
                                date = article.find('date').text.replace('\r','').replace('\t','').replace('\n','')
                                time = article.find('time').text.replace('\r','').replace('\t','').replace('\n','')
                                title = article.find('h3').text.replace('\r','').replace('\t','').replace('\n','')
                                text = article.find('p').text
                                date = date.replace('feb','02').replace('mar','03').replace('apr','04')
                                date = date + ' 2022'
                                publicationDate = date+' ' +time
                                publicationDate = datetime.datetime.strptime(publicationDate, '%d %m %Y %H:%M')
                                data.append(['entry', title, 
                                             'https://www.tgcom24.mediaset.it/'+temporeale+'?'+str(page), 
                                             publicationDate.strftime('%Y-%m-%d %H:%M:%S'),'',text])
                            except:
                                pass
            else:
                print(dailyurl, 'skipped. page returned ',r.status_code)
    
        
    #create or update the database
    print(len(data), 'new articles added to the database')
    if(len(data) > 0):
        df = df.append(pd.DataFrame(data, columns=['Type','Title','url','Date','Subtitle','Article']))   
        if not os.path.exists(RAWPATH + 'TGCOM24'):
            os.mkdir(RAWPATH + 'TGCOM24')
            
        df = df.sort_values(by='Date', ascending=False)
        df.to_csv(DB, index = False)
    
        print('Database saved tgcom24.csv in',RAWPATH+'TGCOM24')