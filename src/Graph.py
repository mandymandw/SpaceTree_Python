'''
Created on Sep 2, 2018

@author: manw
'''
from DirNode import DirNode
from DirEdge import DirEdge

class Graph(object):

    def __init__(self, scene):
        self.scene = scene
        self.clearGraph()
        
    def clearGraph(self):
        self.nodeDict = {}
        self.edgeDict = {}
        self.graphHier = []
        self.root = None
        
    def createDirNode(self, path):
        node = DirNode(self.scene, path)
        self.nodeDict.update({path:node})
        self.scene.addItem(node)
        return node
    
    def getNode(self, path):
        return self.nodeDict[path]
    
    def createDirEdge(self, start, end):
        if not start or not end: return
        e = DirEdge(self.scene, start, end)
        if start not in self.edgeDict.keys():
            self.edgeDict.update({start:{end: e}})
        else:
            self.edgeDict[start].update({end:e})
        self.scene.addItem(e)
        return e
    
    def getEdge(self, start, end):
        if start in self.edgeDict.keys():
            if end in self.edgeDict[start].keys():
                return self.edgeDict[start][end]
        return None
    
#     def createGraph(self, dirs):
#         import os
#         dirset = set('/')
#         for d in dirs:
#             ds = d.split('/')
#             path='/'
#             for dd in ds:
#                 path += '/'+dd
#                 path = os.path.abspath(path.replace("//", "/"))
#                 dirset.add(path)
#         dirlist = sorted(list(dirset))
#         self.dirlist = dirlist
#         for d in dirlist:
#             self.createDirNode(d)
#         self.mycomputeLevels(dirlist)
    '''for file list'''
#     def createGraph(self, dirs):
#         import os
#         '''can remove when reading from crawl file'''
#         dirset = set('/')
#         for d in dirs:
#             ds = d.split('/')
#             path='/'
#             for dd in ds:
#                 path += '/'+dd
#                 path = os.path.abspath(path.replace("//", "/"))
#                 dirset.add(path)
#         dirlist = sorted(list(dirset))
#         self.dirlist = dirlist
#         for d in dirlist:
#             self.createDirNode(d)
#         self.mycomputeLevels(dirlist)
#          
#     def mycomputeLevels(self, dirlist):
#         self.root = self.nodeDict[dirlist[0]]
#         self.root.depth = 0
#         startDepth = 0 if self.root.path=='/' else self.root.path.count('/')
#         '''get parent and children nodes'''
#         for i in xrange(len(dirlist)):
#             d = dirlist[i]
# #             dset = set(d.split('/'))
#             node = self.nodeDict[d]
#             p = d[0:d.rfind('/')]
#             if p=='': p = '/'  #remove after using crawl file
#             if node != self.root:
# #                 p = d[0:d.rfind('/')]
#                 pn = self.nodeDict[p]
#                 node.parent = pn
#                 pn.children.add(node)
#                 node.depth = d.count('/')-startDepth
#             self.createDirEdge(node.parent, node)
# #         '''test'''
# #         for p,n in self.nodeDict.iteritems():
# #             print p, 'None' if not n.parent else n.parent.path, ','.join(x.path for x in n.children)

    '''For file crawl file'''
    def createGraph(self, dirs):
        import os
        '''can remove when reading from crawl file'''
#         dirset = set('/')
#         for d in dirs.keys():
#             ds = d.split('/')
#             path='/'
#             for dd in ds:
#                 path += '/'+dd
#                 path = os.path.abspath(path.replace("//", "/"))
#                 dirset.add(path)
        ''''''
#         dirlist = sorted(list(dirset))
        dirlist = sorted(dirs.keys())
        self.dirlist = dirlist
        for d in dirlist:
            self.createDirNode(d)
        self.mycomputeLevels(dirlist)
          
    def mycomputeLevels(self, dirlist):
        self.root = self.nodeDict[dirlist[0]]
        self.root.depth = 0
        startDepth = 0 if self.root.path=='/' else self.root.path.count('/')
        '''get parent and children nodes'''
        for i in xrange(len(dirlist)):
            d = dirlist[i]
            dset = set(d.split('/'))
            node = self.nodeDict[d]
#             if p=='': p = '/'  #remove after using crawl file
            if node != self.root:
                p = d[0:d.rfind('/')]
                pn = self.nodeDict[p]
                node.parent = pn
                pn.children.add(node)
                node.depth = d.count('/')-startDepth
            self.createDirEdge(node.parent, node)
#         '''ZNOUSE_test'''
#         for p,n in self.nodeDict.iteritems():
#             print p, 'None' if not n.parent else n.parent.path, ','.join(x.path for x in n.children)
            
            
#     def mycomputeLevels(self, dirlist):
#         self.root = self.nodeDict[dirlist[0]]
#         self.root.depth = 0
#         maxdepth = 0
#         '''get parent and children nodes'''
#         for i in xrange(len(dirlist)):
#             d = dirlist[i]
#             dset = set(d.split('/'))
#             node = self.nodeDict[d]
#             p = d[0:d.rfind('/')]
#             if p=='': p = '/' 
#             node.parent = self.nodeDict[p]
#             if node.parent == node: node.parent = None
#             self.createDirEdge(node.parent, node)
#             maxdepth = max(maxdepth, node.depth)
#             for j in xrange(i+1, len(dirlist)):
#                 c = dirlist[j]
#                 cset = set(c.split('/'))
#                 if len(dset)+1==len(cset) and dset.issubset(cset):
#                     cnode = self.nodeDict[c]
#                     node.children.add(cnode)
#                     cnode.depth = node.depth+1
# #         for i in xrange(len(dirlist[-1].split('/'))):
# #             self.graphHier.append([])
# #         for d in self.nodeDict.values():
# #             self.graphHier[d.depth].append(d)
            
    def computeLevels(self, path, startDepth=0, flags='ignore'):
        filterr = self.filte(flags)
        for elem in self.nodeDict.values():
            if filterr(elem):
                elem._flag = False
                elem.depth = -1
        root = self.getNode(path)
        root.depth = startDepth
        queue = [root]
        def getDepth(adj):
            n = adj.endItem
            if(n._flag==False and filterr(n)):
                if n.depth<0: n.depth = node.depth+1+startDepth
                queue.insert(0, n)
        while len(queue)!=0:
            node = queue.pop(0)
            node._flag = True
            self.eachAdjacency(node, getDepth, flags)
        
    def isDescendantOf(self, node, path):
        '''Returns a boolean indicating if some node is descendant of the node with the given id.'''
        if node.path==path: return True
        ans = False
        return (ans or (node.parent and self.isDescendantOf(node.parent, path)))
        
    '''Returns true if any subnode matches the given condition.'''
    def anySubnode(self, node, cond=True, flags=[]):
        flag = False
        def func(nn):
            return nn[cond]
        if isinstance(cond, str):
            c = func
        else:
            c = cond
        for n in node.children:
            if c(n): 
                flag = True
        return flag
#         for c in node.children:
#             return (getattr(c, cond)==flags)
#         return False

    '''
    Method: eachSubgraph
    Iterates over a node's children recursively.
    Parameters:
       node - (object) A <Graph.Node>.
       action - (function) A callback function having a <Graph.Node> as first formal parameter.
    '''
    def eachSubgraph(self, node):
        return self.eachLevel(node, 0)
        
    '''Iterates over a nodes subgraph applying action to the nodes of relative depth between levelBegin and levelEnd.'''
    def eachLevel(self, node, levelBegin=0, levelEnd=20):
        import copy
        leaflevelChildren = []
        templevel2 = []
        templevel1 = [node]
        if levelBegin==0: leaflevelChildren.append([node])
        for i in xrange(1,levelEnd+1):
            while templevel1:
                curr = templevel1.pop(0)
                templevel2.extend(curr.children)
            if templevel2 and i >= levelBegin and i <= levelEnd:
                leaflevelChildren.append(templevel2)
            templevel1 = copy.copy(templevel2)
            templevel2 = []
        return leaflevelChildren

    '''
    Method: eachAdjacency
        Iterates over <Graph.Node> adjacencies applying the *action* function.
     Parameters: 
        node - (object) A <Graph.Node>.
        action - (function) A callback function having <Graph.Adjacence> as first formal parameter.
    '''
    def eachAdjacency(self, node, action, flags):
        if node not in self.edgeDict.keys(): return []
        adj = self.edgeDict[node] #contain {endNode: edge}
        filterr = self.filte(flags)
        for enode, edge in adj.iteritems():
            if filterr(edge):
                if edge.startItem != node:
                    tmp = edge.startItem
                    edge.startItem = edge.endItem
                    edge.endItem = tmp
            action(edge)
                  
    '''provides a filtering function based on flags'''         
    def filte(self, param):
        if not param or not isinstance(param, basestring): return True
        props = param.split(" ")
        def func(elem):
            for p in props:
                if elem[p]: return False
            return True
        return func