#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/3 上午10:38
# @Author  : Huang HUi
# @Site    : 
# @File    : qq.py
# @Software: PyCharm

import  json
import ast
from  collections import OrderedDict,Counter
GIVEN_QUERY=str({'days': 12, 'countries': [{'country_id': 28, 'day': None}],
             'regions': [{'region_id': 2, 'day': None}, {'region_id': 70, 'day': None}],
             'pois': [1361, 1380, 1382, 1385, 1386, 1413, 1512, 1700, 1701, 1712, 1713]})

GIVEN_QUERY = ast.literal_eval(GIVEN_QUERY)
countryIds_query = list(map(lambda x: x['country_id'], GIVEN_QUERY['countries']))
try:
    days_query = GIVEN_QUERY['days']
except:
    days_query = None
print(countryIds_query)
print(days_query)



