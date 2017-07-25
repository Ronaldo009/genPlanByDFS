#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/25 下午2:55
# @Author  : Huang HUi
# @Site    : 
# @File    : genPlan_BFS.py
# @Software: PyCharm

# a sample graph
import genPlanConstraint
import random
import time
import csv
import query_parse
import ast
import copy



class MyQUEUE:  # just an implementation of a queue

    def __init__(self):
        self.holder = []

    def enqueue(self, val):
        self.holder.append(val)

    def dequeue(self):
        val = None
        try:
            val = self.holder[0]
            if len(self.holder) == 1:
                self.holder = []
            else:
                self.holder = self.holder[1:]
        except:
            pass

        return val

    def delete(self,val):
        self.holder.remove(val)

    def IsEmpty(self):
        result = False
        if len(self.holder) == 0:
            result = True
        return result




class BFS():
    def __init__(self, GIVEN_QUERY, nextPartsOf, prevPartsOf, pois, parts, places, schedulePois, schedulePlaces,
                 poiTags, placePoisMapping, currencies, poiCalendar):

        self.countryIds_query, self.days_query, self.regions_query, self.regionDic_query, \
        self.pois_query, self.regionNotGo_query, self.poiNotGo_query, self.regionSorted_query, self.availableMonths_query, self.price_query, \
        self.hotelRating_query, self.arrivalRegionId_query, self.departRegionId_query, self.startParts, self.endParts = query_parse.query_parse(
            GIVEN_QUERY)

        self.nextPartsOf = nextPartsOf
        self.prevPartsOf = prevPartsOf
        self.pois = pois
        self.parts = parts
        self.places = places
        self.placePoisMapping = placePoisMapping
        self.poiTags = poiTags
        self.currencies = currencies
        self.schedulePlaces = schedulePlaces
        self.schedulePois = schedulePois
        self.poiCalendar = poiCalendar

        self.node_neighbors = self.nextPartsOf
        self.tabuDic = {}
        self.start = time.clock()
        self.end = time.clock()
        self.runtime = self.end - self.start

        self.days_aver = 0
        if self.days_query:
            if type(self.days_query) == int:
                self.days_aver = int(self.days_query)
            else:
                self.days_aver = round(sum(self.days_query) / len(self.days_query))


    def update_node_neighbours(self,node,stack):
        if stack:
            try:
                self.node_neighbors[stack[-1]].remove(node)
            except:
                pass
        else:
            return None

    def querySatisfied(self, result, broadPois, broadParts, broadPlaces):
        """

        :param result: 为了判断是否满足query
        :param broadPois: dict
        :param broadParts: dict
        :param broadPlaces: dict
        :return: Boolean
        """
        if self.days_query:
            if type(self.days_query) == list:
                if result['days'] < self.days_query[0] or result["days"] > self.days_query[-1]:
                    return False
            if type(self.days_query) == int:
                if int(result['days']) != self.days_query:
                    return False
        if self.price_query:
            if result['price'] > self.price_query[1] or result['price'] < self.price_query[0]:
                return False
        if self.pois_query:
            if set(self.pois_query) - set(result['poi_ids']):
                return False

        if self.regions_query:
            regionsMapInGenPlan = {x['region_id']: x['days'] for x in result['tour_regions']}
            regionsMapInQuery = {x['region_id']: x['days'] for x in self.regions_query}
            if set(regionsMapInQuery.keys()) - set(regionsMapInGenPlan.keys()):
                return False
            for regionId, days in regionsMapInQuery.items():
                if days and regionsMapInGenPlan[regionId] != days:
                    return False
        if self.regionNotGo_query:
            if set(result['region_ids']) & set(self.regionNotGo_query):
                return False
        if self.poiNotGo_query:
            if set(result['poi_ids']) & set(self.poiNotGo_query):
                return False
        if self.availableMonths_query:
            if set(self.availableMonths_query) - set(result['available_months']):
                return False
        if self.departRegionId_query:
            if self.departRegionId_query and broadPlaces[broadParts[result['part_ids'][-1]]['place_id']][
                'region_id'] != self.departRegionId_query:
                return False
        if self.arrivalRegionId_query:
            if self.arrivalRegionId_query and broadPlaces[broadParts[result['part_ids'][0]]['place_id']][
                'region_id'] != self.arrivalRegionId_query:
                return False
        if self.hotelRating_query:
            if self.hotelRating_query and self.hotelRating_query != result['average_star_rating']:
                return False

        if result['hotel_poi_number'] == 0:
            return False
        if result['rental_car_pois'] % 2 != 0:
            return False
        depuPoi = []
        if len(set(result['poi_ids'])) != len(result['poi_ids']):
            for i in result['poi_ids']:
                if result['poi_ids'].count(i) > 1:
                    depuPoi.append(i)
            for i in set(depuPoi):
                if broadPois[i]['type'] not in ['Pois::CarRental', 'Pois::Airport', 'Pois::Hub']:
                    return False

        for i in range(len(result['part_ids']) - 1):
            if not genPlanConstraint.station_constraint(result['part_ids'][i], result['part_ids'][i + 1], broadPois,
                                                        broadParts):
                return False
        return True

    def poiNotGoConstraint(self,node,poiList):
        poi_ids=self.parts[node]['poi_ids']
        poiList_copy=copy.deepcopy(poiList)
        poiList_copy.extend(poi_ids)
        if self.poiNotGo_query :
            if set(poiList_copy).intersection(set(self.poiNotGo_query)):
                return False
        return True

    def regionConstraint(self,node,stack,broadParts):
        stack_copy=copy.deepcopy(stack)
        stack_copy.append(node)
        regionList=[]
        for part in stack_copy:
            regionList.append(broadParts[part]['region_id'])
        if self.regionNotGo_query:
            if set(regionList).intersection(set(self.regionNotGo_query)):
                return False
        return True

    def daysConstraint(self,node,stack):
        stack_copy=copy.deepcopy(stack)
        stack_copy.append(node)
        days=genPlanConstraint.getDays(stack_copy,self.parts)
        if self.days_query and type(self.days_query) == int:
            if days>self.days_query:
                return False
        if self.days_query and type(self.days_query) == list:
            if days>self.days_query[-1]:
                return False
        return True


    def BFS(self, graph, start, q):
        temp_path = [start]  # start 开始节点
        q.enqueue(temp_path)
        while q.IsEmpty() == False:
            tmp_path = q.dequeue()
            last_node = tmp_path[len(tmp_path) - 1]
            # input('Enter')
            try:
                for link_node in graph[last_node]:
                    if link_node not in tmp_path:
                        if genPlanConstraint.deduPoiConstraint(link_node, genPlanConstraint.getPois(tmp_path,self.parts), self.parts, self.pois):
                            if self.daysConstraint(link_node, tmp_path):  # 如果添加node之后发现 days大于顾客需求，则停止并回溯。将之前走过的路径添加到Tabu
                                if self.poiNotGoConstraint(link_node, genPlanConstraint.getPois(tmp_path,self.parts)):  # 判断是否有不想去的poi，有则剪枝
                                    if genPlanConstraint.station_constraint(tmp_path[-1], link_node, self.pois,self.parts):  # # 判断两个part连接的交通方式是否满足要
                                        if self.regionConstraint(link_node, tmp_path, self.parts):  # 判断region是否满足要求，如果不满足 剪枝
                                            new_path = []
                                            new_path = tmp_path + [link_node]
                                            q.enqueue(new_path)
                                            if link_node in self.endParts:
                                                indexMap = genPlanConstraint.getPathDetail(new_path, self.parts,
                                                                                           self.pois,
                                                                                           self.schedulePois,
                                                                                           self.places,
                                                                                           self.schedulePlaces,
                                                                                           self.poiTags,
                                                                                           self.placePoisMapping,
                                                                                           self.currencies,
                                                                                           self.poiCalendar)
                                                if self.querySatisfied(indexMap, self.pois, self.parts, self.places):
                                                    print("VALID_PATH : ", tmp_path)
                                                    return tmp_path, self.runtime
                                        else:
                                            self.update_node_neighbours(link_node, tmp_path)
                                    else:
                                        self.update_node_neighbours(link_node, tmp_path)
                                else:
                                    self.update_node_neighbours(link_node, tmp_path)

                self.end = time.clock()
                self.runtime = self.end - self.start
                if self.runtime>20:
                    break
            except:
                pass
        return [], self.runtime

    def run(self):
        path_queue = MyQUEUE()  # now we make a queue

        res = []
        runtime = 0
        for node in self.startParts:
            res, runtime = self.BFS(self.node_neighbors, node, path_queue)
            # if res:
            #     break
            if runtime<20 and res:
                break
            if runtime>20:
                break

        return res, runtime


if __name__ == '__main__':

    count = 0
    from getSqlData import getSqlData

    nextPartsOf, prevPartsOf, pois, parts, places, schedulePois, schedulePlaces, poiTags, placePoisMapping, currencies, poiCalendar = getSqlData()

    with open("result3.csv", 'w') as csvout, open('/Users/yanfa/PycharmProjects/CountField/Query.csv', 'r') as csvin:
        reader = csv.reader(csvin)
        next(reader, None)
        writer = csv.writer(csvout)
        writer.writerow(['IsGot','numberOfCountries','numberOfRegions','timeCost','isTimeOut','solutionExists','Path','Query'])
        for row in reader:
            GIVEN_QUERY = ast.literal_eval(row[2])
            bfs = BFS(GIVEN_QUERY, nextPartsOf, prevPartsOf, pois, parts, places, schedulePois, schedulePlaces, poiTags,
                      placePoisMapping, currencies, poiCalendar)
            res, runtime = bfs.run()
            runtime = float(("%.4f") % (runtime))
            isGot = False
            if res:
                isGot = True
            isTimeOut = False
            if float(runtime) > 20:
                isTimeOut = True
            solutionExists = True
            if isGot == False and runtime < 20:
                solutionExists = False
            if isGot == False and runtime >= 20:
                solutionExists = "unknown"
            writer.writerow([isGot, row[0],row[1], runtime, isTimeOut, solutionExists, res, row[2]])

            count += 1
            print("---------程序运行时间为:" + str(runtime) + "----------")

    # GIVEN_QUERY = {'days': [], 'countries': [{'country_id': 2, 'days': None}],
    #                'regions': [{'region_id': 184, 'days': None}],
    #                'regionNotGo': [], 'pois': [253], 'poiNotGo': [], 'price': [2907, 32920], 'arrivalRegionId': 84}
    #
    # bfs = BFS(GIVEN_QUERY, nextPartsOf, prevPartsOf, pois, parts, places, schedulePois, schedulePlaces, poiTags,
    #                   placePoisMapping, currencies, poiCalendar)
    # res, runtime = bfs.run()
