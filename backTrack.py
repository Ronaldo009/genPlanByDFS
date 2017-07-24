#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/30 下午12:35
# @Author  : Huang HUi
# @Site    : 
# @File    : backTrack.py
# @Software: PyCharm

class Graph(object):

    def __init__(self,*args,**kwargs):
        self.node_neighbors = {}
        self.visited = {}

    def add_nodes(self,nodelist):

        for node in nodelist:
            self.add_node(node)

    def add_node(self,node):
        if  node not in self.nodes():
            self.node_neighbors[node] = []

    def add_edge(self,edge):
        u,v = edge
        if(v not in self.node_neighbors[u]) and ( u not in self.node_neighbors[v]):
            self.node_neighbors[u].append(v)
            # if(u!=v):
            #     self.node_neighbors[v].append(u)

    def update_node_neighbours(self,stack):

        last = stack.pop()
        if stack:
            self.node_neighbors[stack[-1]].remove(last)
        else:
            return None



    def nodes(self):
        return self.node_neighbors.keys()

    def is_leafNode(self,order):
        last=order[-1]
        if self.node_neighbors[last]:
            return False
        return True

    def depth_first_search(self,node=None):
        stack = [node]
        while stack:
            # 判断是否是叶节点  如果不是 则继续深入，是叶节点 则判断order是否满足条件
            try:
                node = min(self.node_neighbors[node])
                stack.append(node)
                if node==9:
                    return stack
            except:
                self.update_node_neighbours(stack)
                if len(stack)>0:
                    node=stack[-1]




if __name__ == '__main__':
    g = Graph()
    g.add_nodes([i+1 for i in range(8)])
    g.add_edge((1, 2))
    g.add_edge((1, 3))
    g.add_edge((2, 4))
    g.add_edge((2, 5))
    g.add_edge((4, 8))
    g.add_edge((5, 8))
    g.add_edge((3, 6))
    g.add_edge((3, 7))
    g.add_edge((6, 7))
    print ("nodes:", g.nodes())
    orderDFS = g.depth_first_search(1)
    print(orderDFS)