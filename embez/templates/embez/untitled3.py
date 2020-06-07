#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 15:02:07 2020

@author: anna
"""

import pandas as pd 
from statsmodels.tsa.statespace.sarimax import SARIMAX

data = pd.read_excel(r'/Users/anna/Downloads/data_eviews.xlsx')
sales = pd.DataFrame(data, columns= ['total_sales'])
other_data =pd.DataFrame(data, columns= ['asaians'])
sarimax_model = SARIMAX(sales, order = (1,0,1), seasonal_order =(1,0,1,4), exog = other_data)
model_fit = sarimax_model.fit()
model_fit.summary()
