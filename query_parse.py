#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/20 下午4:00
# @Author  : Huang HUi
# @Site    : 
# @File    : query_parse.py
# @Software: PyCharm
from mysqlConnection import mysqlConnection
import yaml
import copy
import time
import csv
import json
from collections import OrderedDict
import ast

#
# GIVEN_QUERY = {'days': [10,14], 'countries': [{'country_id': 28, 'day': None}],
#     'regions': [{'region_id': 2, 'day': None}, {'region_id': 27, 'day': None}, {'region_id': 69, 'day': None}], 'pois': [],
#     'regionNotGo': [], 'poiNotGo': [], 'regionSorted': [135, 131], 'availableMonths': [],
#     'price': [5000, 15000], 'hotelRating': None, 'arrivalRegionId': 27, 'departRegionId': None}

# GIVEN_QUERY={'days': [10,13], 'countries': [{'country_id': 11, 'day': None}], 'regions': [{'region_id': 266, 'day': None},
#         {'region_id': 220, 'day': None}], 'pois': [795, 800,878,1536]}

# GIVEN_QUERY={'days': [12], 'countries': [{'country_id': 28, 'day': None}],
#              'regions': [{'region_id': 2, 'day': None}, {'region_id': 70, 'day': None}],
#              'pois': [1361, 1380, 1382, 1385, 1386, 1413, 1512, 1700, 1701, 1712, 1713]}

def query_parse(GIVEN_QUERY):

    try:
        countryIds_query = list(map(lambda x: x['country_id'], GIVEN_QUERY['countries']))
    except :
        countryIds_query=None
    try:
        days_query=GIVEN_QUERY['days']
    except :
        days_query=None
    try:
        regions_query = GIVEN_QUERY['regions']
    except :
        regions_query=[]
    try:
        regionDic_query = list(map(lambda x: {x['region_id']: x['day']}, regions_query))
    except :
        regionDic_query=[]
    try:
        pois_query=GIVEN_QUERY['pois']
    except :
        pois_query=[]
    try:
        regionNotGo_query=GIVEN_QUERY['regionNotGo']
    except :
        regionNotGo_query=[]
    try:
        poiNotGo_query=GIVEN_QUERY['poiNotGo']
    except :
        poiNotGo_query=[]
    try:
        regionSorted_query=GIVEN_QUERY['regionSorted']
    except :
        regionSorted_query=[]
    try:
        availableMonths_query=GIVEN_QUERY['availableMonths']
    except :
        availableMonths_query=[]
    try:
        price_query=GIVEN_QUERY['price']
    except :
        price_query=None
    try:
        hotelRating_query=GIVEN_QUERY['hotelRating']
    except :
        hotelRating_query=None
    try:
        arrivalRegionId_query=GIVEN_QUERY['arrivalRegionId']
    except :
        arrivalRegionId_query=None
    try:
        departRegionId_query=GIVEN_QUERY['departRegionId']
    except:
        departRegionId_query=None


    connection=mysqlConnection()
    try:
        with connection.cursor() as cursor:

            if GIVEN_QUERY['countries']:
                # country condition
                if arrivalRegionId_query:
                    sql = "SELECT tidy_parts.id as id, country_id,region_id FROM tidy_parts join regions on tidy_parts.region_id = regions.id WHERE tidy_parts.is_start = 1 and tidy_parts.poi_ids is not NULL and tidy_parts.state!='canceled' and tidy_parts.deleted_at is null and region_id =(%s) and country_id in (%s)" % (arrivalRegionId_query,str(countryIds_query)[1:-1])
                else:
                    sql = "SELECT tidy_parts.id as id, country_id FROM tidy_parts join regions on tidy_parts.region_id = regions.id WHERE tidy_parts.is_start = 1 and tidy_parts.poi_ids is not NULL and tidy_parts.state!='canceled' and tidy_parts.deleted_at is null and country_id in (%s)" % str(countryIds_query)[1:-1]
            else:
                # all
                sql = "SELECT id FROM tidy_parts WHERE tidy_parts.is_start = 1 and tidy_parts.poi_ids is not NULL and tidy_parts.state!='canceled' and tidy_parts.deleted_at is null "
            cursor.execute(sql)
            startParts = cursor.fetchall()
            if GIVEN_QUERY['countries']:
                if departRegionId_query:
                    sql = "SELECT tidy_parts.id as id, country_id,region_id FROM tidy_parts join regions on tidy_parts.region_id = regions.id WHERE tidy_parts.is_end = 1 and tidy_parts.poi_ids is not NULL and tidy_parts.state!='canceled' and tidy_parts.deleted_at is null and region_id =(%s) and country_id in (%s)" % (departRegionId_query, str(countryIds_query)[1:-1])
                else:
                    sql = "SELECT tidy_parts.id as id, country_id FROM tidy_parts join regions on tidy_parts.region_id = regions.id WHERE tidy_parts.is_end = 1 and tidy_parts.poi_ids is not NULL and tidy_parts.state!='canceled' and tidy_parts.deleted_at is null and country_id in (%s)" % str(countryIds_query)[1:-1]
            else:
                sql = "SELECT id FROM tidy_parts WHERE tidy_parts.is_end = 1 and tidy_parts.poi_ids is not NULL and tidy_parts.state!='canceled' and tidy_parts.deleted_at is null "
            cursor.execute(sql)
            endParts = cursor.fetchall()




    finally:
        connection.close()

    startParts = [dict['id'] for dict in startParts]
    endParts = [dict['id'] for dict in endParts]


    return  countryIds_query, days_query, regions_query, regionDic_query, \
            pois_query, regionNotGo_query, poiNotGo_query, regionSorted_query, availableMonths_query, price_query, \
            hotelRating_query, arrivalRegionId_query, departRegionId_query,startParts,endParts



