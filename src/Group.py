'''
Created on Sep 2, 2018

@author: manw
'''
from Animation import Animation
from matplotlib.pyplot import flag

class Group(object):
    '''
    Perfoms operations on group of nodes
    '''
    def __init__(self, viz):
        self.viz = viz
        self.scene = viz.scene
        self.config = viz.config
        self.graph = viz.graph
        self.animation = Animation(viz)
        self.nodes = None
        
    '''
    Calls the request method on the controller to request a subtree for each node. 
    used for buffering information into the visualization.  
    When clicking on an empty node, the visualization will make a request for this nodes subtrees, 
    specifying a given level for this subtree (defined by levelsToShow).  
    Once the request is completed, the onComplete callback should be called with the given result.  
    This is useful to provide on-demand information into the visualizations without having to load the entire information from start.
    '''
    def requestNodes(self, nodes, controller):
        '''for json graph loading'''
        length = len(nodes)
        nodeSelected = {}
        complete = controller.onComplete
        if length==0: complete()
        for i in xrange(length):
            nodeSelected[nodes[i].path] = nodes[i]
        complete()
            
    '''collapse group of nodes'''    
    def contract(self, nodes, controller=None):
        nodes = self.prepare(nodes)
        def compute(delta):
            if delta==1: delta=0.99
#             self.plotStep(1-delta, controller, self.animation.animating)
            self.animation.animating = 'contract'
        def complete():
            self.hide(nodes, controller)
        self.animation.animating = False
#         self.animation.setOptions(controller, compute, complete)
#         self.animation.start()
        complete()

        
         
    def hide(self, nodes, controller):
        graph = self.graph
        for i in xrange(len(nodes)):
            self.descendentExpandedUnset(nodes[i])
            levelNodes = graph.eachLevel(nodes[i], 1, False)
            if True or not controller or not controller.request:
                for alevel in levelNodes:
                    for elem in alevel:
                        if elem.exist:
                            elem.drawn = False
                            elem.setVisible(False)
                            elem.exist = False
#             else:
#                 ids = []
#                 for alevel in levelNodes:
#                     for elem in alevel:
#                         ids.append(elem.path)
#                 viz.op.removeNode(ids, {'type':'nothing'}
        if controller: controller.onComplete()
    
    '''expand group of nodes'''        
    def expand(self, nodes, controller=None):
        self.show(nodes)
        def compute(delta):
#             self.plotStep(delta, controller, self.animation.animating)
            self.animation.animating = 'expand'
        def complete():
#             self.plotStep(None, controller, False)
            if controller and getattr(controller, 'onComplete'):
                controller.onComplete()
        self.animation.animating = False
#         self.animation.setOptions(controller, compute, complete)
#         self.animation.start()
        complete()
        
    def plotStep(self, delta, controller, animating):
        viz = self.viz
        scene = viz.scene
        nodes = self.nodes
        graph = self.graph
        '''hide nodes that are meant to be collapsed/expanded'''
        nds = {}
        for i in xrange(len(nodes)):
            node = nodes[i]
            nds[node.path] = []
            subgraph = graph.eachSubgraph(node)
            for alevel in subgraph:
                for n in alevel:
                    if n.drawn:
                        n.drawn = False
                        nds[node.path].append(n)
            node.drawn = True
        '''plot the whole (non-scaled) tree'''
        if len(nodes)>0: viz.fx.plot()
        '''show nodes that were previously hidden'''
        for i in nds:
            for n in nds[i]:
                n.drawn = True
        '''plot each scaled subtree'''
        for i in xrange(len(nodes)):
            node = nodes[i]
            viz.fx.plotSubtree(node, controller, delta, animating)
        
    def show(self, nodes):
        config = self.config
        self.prepare(nodes)
        for n in nodes:
            ns = self.graph.eachLevel(n, 0, config.levelsToShow)
            for nn in ns:
                for nnn in nn:
                    if nnn.exist:
                        self.ancestorExpandedSet(nnn)
                        nnn.drawn=True
                        nnn.setVisible(True)
                
    def ancestorExpandedSet(self, node):
        node  = node.parent
        while node and not node.expanded:
            node.expanded = True
            node = node.parent
            
    def descendentExpandedUnset(self, node):
        if node.expanded == False: return
        queue = [node]
        while queue:
            n = queue.pop(0)
            n.expanded = False
            queue.extend(n.children)
            
    def prepare(self, nodes):
        #self.nodes = self.getNodesWithChidren(nodes)
        return self.getNodesWithChidren(nodes) #self.nodes
    
    def getSiblings(self, nodes):
        siblings = {}
        for n in nodes:
            if not n.parent:
                siblings[n.path] = [n]
            else:
                siblings[n.path] = list(n.parent.children)
        return siblings
    
    '''
    Filters an array of nodes leaving only nodes with children
    '''
    def getNodesWithChidren(self, nodes):
        ans = []
        sorted(nodes, key=lambda a: a.depth)#lambda a,b:(a.depth<=b.depth)-(a.depth>=b.depth))
        for i in xrange(len(nodes)):
            if self.graph.anySubnode(nodes[i], 'exist', []):
#                 print  'got here', nodes[i]
                desc = False
                j = i+1
                while not desc and j<len(nodes):
                    desc = desc or self.graph.isDescendantOf(nodes[i], nodes[j].path)
                    j+=1
                if not desc: ans.append(nodes[i])
        return ans
    
    def setExistenceDrawnOfNodes(self, nodes, flag):
        for n in nodes:
            n.exist = n.drawn = flag
            n.setVisible(flag)