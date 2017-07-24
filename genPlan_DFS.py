#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 下午7:35
# @Author  : Huang HUi
# @Site    : 
# @File    : genPlan_DFS.py
# @Software: PyCharm
import genPlanConstraint
import random
import time
import csv
import query_parse
import ast
import copy
class Graph(object):

    def __init__(self,GIVEN_QUERY,*args,**kwargs):

        self.parts_all,self.nextPartsOf,self.startParts,self.endparts ,self.pois,self.parts,self.places, \
        self.schedulePois,self.schedulePlaces,self.poiTags,self.placePoisMapping,self.currencies,self.poiCalendar, \
        self.poi_ids_satisfy_parts,self.countryIds_query,self.days_query,self.regions_query,self.regionDic_query,\
        self.pois_query,self.regionNotGo_query,self.poiNotGo_query,self.regionSorted_query,self.availableMonths_query,self.price_query,\
        self.hotelRating_query,self.arrivalRegionId_query,self.departRegionId_query= query_parse.query_parse(GIVEN_QUERY)

        self.node_neighbors = self.nextPartsOf
        self.tabuDic={}
        self.start=time.clock()
        self.end=time.clock()
        self.runtime=self.end-self.start

        self.days_aver = 0
        if self.days_query:
            if type(self.days_query) == int:
                self.days_aver = self.days_query
            else:
                self.days_aver = round(sum(self.days_query) / len(self.days_query))



    def nodes(self):
        return self.node_neighbors.keys()

    def update_node_neighbours(self,node,stack):
        if stack:
            try:
                self.node_neighbors[stack[-1]].remove(node)
            except:
                pass
        else:
            return None

    def addPoi(self,node,poiList):
        poi_ids=self.parts[node]['poi_ids']
        poi_ids_copy=copy.deepcopy(poi_ids)
        poiList.extend(poi_ids_copy)
        return poiList

    def minsPoi(self,stack,poiList):
        node=stack[-1]
        poi_ids=self.parts[node]['poi_ids']
        poi_ids_copy=copy.deepcopy(poi_ids)
        poiList=list(set(poiList)-set(poi_ids_copy))
        return poiList

    # def backTrack(self,node,stack,poiList):
    #     poiList = self.minsPoi(node=node, poiList=poiList)
    #     self.update_node_neighbours(stack)
    #     if len(stack) > 0:
    #         node = stack[-1]

    def addTabuDic(self,tabuDic,stack):
        """
        #
        :param tabuDic:dict self.tabuDic
        :param stack:path 路径 list
        :return:更新self.tabuDic
        """
        node1=stack[-1]
        node2=stack[0:-1]
        if node1 in tabuDic:
            tabuDic[node1].append(node2)
        if node1 not in tabuDic:
            tabuDic[node1]=[node2]
        return tabuDic

    def addTabuDic_deduPoi(self, tabuDic, stack,node):
        """
        #
        :param tabuDic:dict self.tabuDic
        :param stack:path 路径 list
        :return:更新self.tabuDic
        """

        if node in tabuDic:
            tabuDic[node].append(stack)
        if node not in tabuDic:
            tabuDic[node] = [stack]
        return tabuDic


    def getNode(self,stack, notAvailableDict, prevPath):
        """
        :param nodeList: 可选择的所有node，即前一节点可连通的所有节点
        :param notAvailableDict: 比如{4:{[1,2]}, 5:{[9,2]}}
        :param prevPath: 比如[1,2]，即前面已连通的所有节点
        :return: 选择的节点
        """
        node=stack[-1]
        nodeList=self.node_neighbors[node]
        copyNodeList = copy.deepcopy(nodeList)
        indexOfNode = 0
        while indexOfNode <= (len(copyNodeList) - 1):
            nodeId = copyNodeList[indexOfNode]
            if nodeId in notAvailableDict:
                if prevPath in notAvailableDict[nodeId]:
                    copyNodeList.pop(indexOfNode)
                else:
                    indexOfNode += 1
            else:
                indexOfNode+=1
        return random.choice(copyNodeList)



    def isEnd(self,stack):
        indexMap = genPlanConstraint.getPathDetail(stack, self.parts, self.pois, self.schedulePois,self. places, self.schedulePlaces,
                                                   self.poiTags, self.placePoisMapping, self.currencies, self.poiCalendar)
        if self.querySatisfied(indexMap,self.pois, self.parts,self. places):
            return stack

    def querySatisfied(self,result,broadPois,broadParts,broadPlaces):
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
            if not genPlanConstraint.station_constraint(result['part_ids'][i], result['part_ids'][i + 1], broadPois, broadParts):
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

    def depth_first_search(self,node=None):
        stack = [node]
        poiList_copy=self.parts[node]['poi_ids']
        poiList=copy.deepcopy(poiList_copy)
        while stack :
            try:
                node = self.getNode(stack,self.tabuDic,stack)
                if  genPlanConstraint.deduPoiConstraint(node,poiList,self.parts,self.pois):
                    if self.daysConstraint(node,stack):# 如果添加node之后发现 days大于顾客需求，则停止并回溯。将之前走过的路径添加到Tabu
                        if self.poiNotGoConstraint(node,poiList):  # 判断是否有不想去的poi，有则剪枝
                            if genPlanConstraint.station_constraint(stack[-1],node,self.pois,self.parts): # # 判断两个part连接的交通方式是否满足要
                                if self.regionConstraint(node,stack,self.parts):# 判断region是否满足要求，如果不满足 剪枝
                                    stack.append(node)
                                    poiList = self.addPoi(node=node, poiList=poiList)
                                    print("addPoi")
                                    # 判断是否结束
                                    if node in self.endparts:
                                        indexMap = genPlanConstraint.getPathDetail(stack, self.parts, self.pois,
                                                                                   self.schedulePois,
                                                                                   self.places, self.schedulePlaces,
                                                                                   self.poiTags, self.placePoisMapping,
                                                                                   self.currencies,
                                                                                   self.poiCalendar)
                                        print("ssss")
                                        if self.querySatisfied(indexMap, self.pois, self.parts, self.places):
                                            print("aaaaa")
                                            return stack, self.runtime
                                    if not self.days_query and len(stack) > 10:
                                        poiList = self.minsPoi(stack, poiList=poiList)
                                        self.tabuDic = self.addTabuDic(self.tabuDic, stack)
                                        print("part过长")
                                        stack = stack[0:8]
                                        if len(stack) > 0:
                                            node = stack[-1]
                                else:
                                    self.update_node_neighbours(node, stack)
                            else:
                                self.update_node_neighbours(node, stack)
                        else:
                            self.update_node_neighbours(node,stack)
                    else:
                        self.tabuDic = self.addTabuDic_deduPoi(self.tabuDic, stack, node)
                else:
                    self.tabuDic=self.addTabuDic_deduPoi(self.tabuDic,stack,node)
                self.end = time.clock()
                self.runtime = self.end - self.start
                if self.runtime>7:
                    return [],self.runtime
            except:
                poiList = self.minsPoi(stack, poiList)
                self.tabuDic = self.addTabuDic(self.tabuDic, stack)
                self.update_node_neighbours(node,stack)
                stack.pop()
                print("except")
                if len(stack) > 0:
                    node = stack[-1]
        self.end=time.clock()
        self.runtime=self.end-self.start
        return [],self.runtime
    def run(self):
        runtime=0
        orderDFS=[]
        for node in self.startParts:
            orderDFS ,runtime= g.depth_first_search(node)
            if orderDFS:
                break
            # if runtime<7 and orderDFS:
            #     break
            # if runtime>7:
            #     break
        print("----------------程序完成,用时" + str(("%.2f") % (runtime)) + "秒------------------")

        return orderDFS,runtime

if __name__ == '__main__':
    count = 0
    with open("result2.csv",'w') as csvout ,open('result1.csv','r') as csvin:
        reader=csv.reader(csvin)
        next(reader,None)
        writer=csv.writer(csvout)
        writer.writerow(['IsGot','Path','Time''Query'])
        for row in reader:
            if row[0]=="False":
                GIVEN_QUERY = ast.literal_eval(row[3])
                # GIVEN_QUERY={'days': 12, 'countries': [{'country_id': 28, 'day': None}],
                #              'regions': [{'region_id': 2, 'day': None}, {'region_id': 70, 'day': None}],
                #              'pois': [1361]}
                g = Graph(GIVEN_QUERY)
                res,runtime=g.run()
                isGot=False
                if res:
                    isGot=True
                writer.writerow([isGot,res,runtime,row[3]])
                count+=1









