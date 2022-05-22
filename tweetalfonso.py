#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 21:14:57 2022

@author: giulio
"""

import tweepy
from datetime import datetime, timezone
import re
import pandas as pd
import matplotlib.pyplot as plt

ckey = 'QdBC9Vyefms44N5mvNYBiSX52'
csecret = 'jHbGdXGH52syfa3wky0rwBkupB7lGOK3edR9Na0m9MdFbEjS4y'
atoken = '353011825-uBmrd5lj5gMMODp4OXVRWwoJlhO0NgPrn4udLvsi'
asecret = '2sCxjPXliMk3zbtJIIQByKCNaPUT7XKjcaA7i98tfeg5U'

auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)

lastID = None
lastTime = None
tweets = []


while True:
    print(lastID)
    if lastID == None:
        stuff = api.user_timeline(screen_name = 'Viminale', include_rts = False, count=100, tweet_mode='extended')
    else:
        stuff = api.user_timeline(screen_name = 'Viminale', include_rts = False, max_id = lastID, tweet_mode='extended')

    lastID = stuff[-1].id
    
    uk = [x for x in stuff if '#AccoglienzaUcraina' in x.full_text or '#Accoglienza #Ucraina' in x.full_text]
    for tweet in uk:
        #print( tweet.text)
        tweets.append(tweet)
    
    if(lastTime != tweets[-1].created_at):
        lastTime = tweets[-1].created_at
    else:
        break
    
data = []
for tweet in tweets:
    try:
        uomini = int(re.search(r"[0-9.]* uomini", tweet.full_text).group().replace(' uomini','').replace('.',''))
        donne = int(re.search(r"[0-9.]*. donne", tweet.full_text).group().replace(' donne','').replace('.',''))
        minori = int(re.search(r"[0-9.]* minori", tweet.full_text).group().replace(' minori','').replace('.',''))
        
            
        data.append([tweet.created_at.strftime("%m/%d/%Y"), uomini, donne, minori, tweet.full_text])
    except:
        print(tweet.full_text)
        
df = pd.DataFrame(data, columns=['Data','Uomini','Donne','Minori', 'Tweet'])
df.Data = pd.to_datetime(df.Data)
df = df.sort_values(by='Data')

plt.figure()
plt.subplot(2,1,1)
plt.title('Cumulative number of ukranian refugees in Italy\nby day, Sex, and Age')
plt.plot(df.Data, df.Uomini, label='Uomini')
plt.plot(df.Data, df.Donne, label='Donne')
plt.plot(df.Data, df.Minori, label='Minori')
plt.legend()

df = df.assign(nuoviUomini = [0] + list(df.Uomini)[:-1])
df = df.assign(nuoviDonne = [0] + list(df.Donne)[:-1])
df = df.assign(nuoviMinori = [0] + list(df.Minori)[:-1])
df.nuoviUomini = df.Uomini - df.nuoviUomini
df.nuoviDonne = df.Donne - df.nuoviDonne
df.nuoviMinori = df.Minori - df.nuoviMinori

plt.subplot(2,1,2)
plt.title('New ukranian refugees in Italy\nby day, Sex, and Age')
plt.scatter(df.Data, df.nuoviUomini)
plt.scatter(df.Data, df.nuoviDonne)
plt.scatter(df.Data, df.nuoviMinori)