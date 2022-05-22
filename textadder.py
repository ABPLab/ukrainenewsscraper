#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 22 13:43:04 2022

@author: giulio
"""

import os
import pandas as pd
from tqdm import tqdm

BASEPATH = '/home/giulio/Repositories/ukrainenewsscraper'
RAWPATH = BASEPATH + os.sep + 'Raw' + os.sep #Path to raw data folder
DB = RAWPATH+'ilpost/ilpost.csv' #name of the database

df = pd.read_csv(DB)

texts = []
for ID in tqdm(df.ID):
    with open('/home/giulio/Repositories/ukrainenewsscraper/Raw/ilpost/Articles/'+str(ID)+'.txt') as f:
        text = f.readlines()
        texts.append(' '.join(text).replace('\n',''))
        
df = df.assign(Article=texts)
df.to_csv(DB)
