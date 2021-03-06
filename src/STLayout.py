'''
Created on Aug 22, 2018

@author: manw
'''
from PyQt5.QtCore import Qt
from collections import namedtuple
from DirNode import DirNode
from DirEdge import DirEdge 
from Graph import Graph
from Group import Group
from Options import *
from platform import node
import sys

class Size(object):
    def __init__(self, w, h):
        self.width = w
        self.height = h
        
    def __getitem__(self, name):
        return getattr(self, name)

class Subtree(object):
    def __init__(self, tree, extent):
        self.tree = tree
        self.extent = extent

class Config(object):
    '''
    Configuration:
     The configuration object can have the following properties (all properties are optional and have a default value)
      
     *General*
     - _orientation_ Sets the orientation layout. Implemented orientations are _left_ (the root node will be placed on the left side of the screen), _top_ (the root node will be placed on top of the screen), _bottom_ and _right_. Default's "left".
     - _levelsToShow_ Depth of the plotted tree. The plotted tree will be pruned in order to fit the specified depth. Default's 2.
     - _subtreeOffset_ Separation offset between subtrees. Default's 8.
     - _siblingOffset_ Separation offset between siblings. Default's 5.
     - _levelDistance_ Distance between levels. Default's 30.
     - _withLabels_ Whether the visualization should use/create labels or not. Default's *true*.
    '''
    def __init__(self):
        self.align = 'center'
        self.orientation = 'left'
        self.levelsToShow = 2  #the levels to show after the root
        self.subtreeOffset = 0  #50
        self.siblingOffset = 5#50
        self.levelDistance = 200
        self.node = None
        self.offsetX, self.offsetY = 0,0

class Geom(object):
    '''Provide lowlevel geometrical computations'''
    def __init__(self, viz):
        self.viz = viz
        self.scene = viz.scene
        self.graph = viz.graph
        self.config = viz.config
        self.node = DirNode(self.scene)
        self.edge = DirEdge(self.scene)
    
    '''
     Method: translate

     Applies a translation to the tree.
     Parameters:
     pos - A [x,y] number specifying translation vector.
     prop - A <DirNode> position property ('pos', 'startPos' or 'endPos').
     Example:
     (start code js)
      st.geom.translate(new Complex(300, 100), 'endPos');
     (end code)
     '''
    def translate(self, pos, props):
        for elem in self.viz.graph.nodeDict.values():
            for p in props:
                elem[p][0] += pos[0]
                elem[p][1] += pos[1]
    '''
    Changes the tree current orientation to the one specified.
       You should usually use <ST.switchPosition> instead.
    '''
    def swithOrientation(self, orn=None):
        if orn:
            self.config.orientation = orn
        else:
            s = self.dispatch('bottom', 'top', 'left', 'right')
            self.config.orientation = s
    
    '''
    Makes a value dispatch according to the current layout
    Works like a CSS property, either _top-right-bottom-left_ or _top|bottom - left|right_.
    '''
    def dispatch(self, *argvs):
        length = len(argvs)
        s = self.config.orientation
        def val(a):
            if callable(a): return a()
            else: return a
        if length==2:
            if (s=='top' or s=='bottom'): return val(argvs[0])
            else: return val(argvs[1])
        elif length==4:
            if s=='top': return val(argvs[0])
            elif s=='right': return val(argvs[1])
            elif s=='bottom': return val(argvs[2])
            elif s=='left': return val(argvs[3])
        return None
    '''
    Returns label height or with, depending on the tree current orientation.
    '''
    def getSize(self, n, invert):
        node = self.node
        siblingOffset = self.config.siblingOffset
        w = node.width + siblingOffset
        h = node.height + siblingOffset
        if not invert:
            return self.dispatch(h,w)
        else:
            return self.dispatch(w,h)
    ''' 
    Calculates a subtree base size. This is an utility function used by _getBaseSize_
    '''
    def getTreeBaseSize(self, node, level, leaf):
        size = self.getSize(node, True)
        baseHeight = 0
        if leaf(level, node): return 0
        for elem in node.children:
            baseHeight += self.getTreeBaseSize(elem, level-1, leaf)
        return (size if size>baseHeight else baseHeight)+self.config.subtreeOffset
    
    '''
    Method: getEdge
       
       Returns a Complex instance with the begin or end position of the edge to be plotted.
       Parameters:
       node - A <Graph.Node> that is connected to this edge.
       type - Returns the begin or end edge position. Possible values are 'begin' or 'end'.
       Returns:
       A <Complex> number specifying the begin or end position.
    '''
    def getEdge(self, node, typee):
        def func(a,b):
            return [node.pos().x()+a, node.pos().y()+b]
        C=func
        dim = self.node
        w = dim.width
        h = dim.height
        if typee=='begin':
            '''alignment center'''
            return self.dispatch(C(0, h/2), C(-w/2,0),\
                                 C(0, -h/2), C(w/2,0))
        elif typee=='end':
            return self.dispatch(C(0, -h/2), C(w/2,0),\
                                 C(0, h/2), C(-w/2,0))
    '''
    Adjusts the tree position due to canvas scaling or translation.
    '''
    def getScaledTreePosition(self, node, scale):
        dim = self.node
        w = dim.width
        h = dim.height
        def C(a,b):
            return (node.pos[0]+(1-scale)*a, node.pos[1]+(1-scale)*b)
        
        return self.dispatch(C(0,h/2), C(-w/2,0),\
                             C(0,-h/2), C(w/2,0))
    '''
    Method: treeFitsInCanvas
       
       Returns a Boolean if the current subtree fits in canvas.
       Parameters:
       node - A <Graph.Node> which is the current root of the subtree.
       canvas - The <Canvas> object.
       level - The depth of the subtree to be considered.
    '''
    def treeFitsInCanvas(self, node, canvas, level):
        size = self.scene.canvasH #self.dispatch(self.config.orientation, self.scene.canvasW, self.scene.canvasH)
        def leaf(level, node):
            return level==0 or (not node.children)
        baseSize = self.getTreeBaseSize(node, level, leaf)
        print baseSize, size, (baseSize<size)
        return (baseSize<size)
    '''
    Returns the right level to show for the current tree in order to fit in canvas.
    '''
    def getRightLevelToShow(self, node, canvas):
        level = self.config.levelsToShow
#         while (not self.treeFitsInCanvas(node, canvas, level) and level>1):
#             level -= 1
        return level
    
    def scaleGraphToFitCanvas(self, node, canvas):
        level = self.config.levelsToShow
        while (not self.treeFitsInCanvas(node, canvas, level) and level>1):
            level -= 1
#             level -= 1
            
    '''
    Hides levels of the tree until it properly fits in canvas.
    '''
    def setRightLevelToShow(self, node, canvas, callback={}):
        level = self.getRightLevelToShow(node, canvas)
        for n in self.graph.nodeDict.values():
            '''change n.depth<0 added'''
            d = n.depth-node.depth
#             print n.path, node.path, d>level
            if n.depth<0 or d>level:
                if 'onHide' in callback.keys(): callback['onHide'](n)
                if 'execHide' in callback.keys():
                    if callback['execHide']:
                        n.exist = False
                        n.drawn = False
                        n.setVisible(False)
                        if n in self.scene.layout.nodesDraw2:
                            self.scene.layout.nodesDraw2.remove(n)
            else:
                if 'onShow' in callback.keys(): callback['onShow'](n)
        node.drawn = True
        node.setVisible(True)
        self.scene.layout.nodesDraw2.add(node)
        
class Controller(object):
    
    def __init__(self):
        self.request = False
     
class STLayout(object):
    
    def __init__(self, root, nodes, scene):
        self.scene = scene
        self.graph = scene.graph
        self.config = Config()
        self.geom = Geom(self)
        self.group = Group(self)
        self.fx = Plot(self)
        self.op = Options(self)
        self.controller = Controller()
        '''for layout'''
        self.level_dist = 0.15
        self.min_intervalH = root.rad
        self.max_intervalH = 0.3*self.scene.canvasH
        
        self.root = root
        self.nodes = nodes
        self.nodesInPath = []
        self.nodesDraw1 = set()
        self.nodesDraw2 = set()
        self.clickedNode = None
        self.busy = False
    
    def computePosForChildren(self, node, numChildren):
        intervalH = self.scene.canvasH/numChildren
        intervalH = min(self.max_intervalH, max(self.min_intervalH, intervalH))
        intervalH /= self.scene.canvasH
        if numChildren%2==0: # if number of children is even
            half = numChildren/2
            startY = node.relativeY-(half-0.5)*intervalH
        else:
            half = numChildren/2
            startY = node.relativeY-intervalH*half
        i=0
        for c in node.children:
            c.setVisible(True)
            c.relativeX = node.relativeX+self.level_dist
            c.relativeY = startY+i*intervalH
            i+=1
        node.setPos(node.relativeX, node.relativeY)
         
    def expandNode(self, node, isClickedNode=False):
#         print 'expand: ', self.busy
        if not node.children: return
        if self.busy: return
        self.busy = True
#         if node.parent: self.group.setExistenceDrawnOfNodes([node.parent], False)
        # set the existence of the children nodes so that they should be drawn in the resulting graph
        self.group.setExistenceDrawnOfNodes(node.children, True)
        self.group.expand([node], isClickedNode = isClickedNode) 
        # make sure only specified levels are shown: hide the first level and expand one more level from the clicked node
        for n in node.children:
            self.fitTreeInLevel(n, 1)
            break
        node.expanded = True
#         print 'expand'
        self.getNodesToDraw()
        self.group.animation.start(True)

    def collapseNode(self, node, clickedNode=False):
#         print 'collapse: ', self.busy
        if not node.children: return
        if self.busy: return
        self.busy = True
        self.group.contract([node])
        node.expanded = False
#         if node.parent: self.group.setExistenceDrawnOfNodes([node.parent], True)
#         self.group.setExistenceDrawnOfNodes(node.children, False)
#         print 'collapse'
        self.getNodesToDraw()
        if clickedNode:
            self.fitTreeInLevel(node, -1)
        self.group.animation.start(False)

    '''from space tree layout'''
    def plot(self):
        self.fx.plot(self.controller)
        
    def movetree(self, node, prop, val, orn):
        p = 1 if (orn=='left' or orn=='right') else 0
        node[prop][p] += val
   
    def moveextent(self, extent, val):
        ans = []
        for e in extent:
            e[0] += val
            e[1] += val
            ans.append(e)
        return ans
    
    def merge(self, ps, qs):
        if len(ps)==0: return qs
        if len(qs)==0: return ps
        p = ps.pop(0)
        q = qs.pop(0)
        return [[p[0], q[1]]]+(self.merge(ps, qs))
        
    def mergelist(self, ls, deff=[]):
        if len(ls)==0: return deff
        ps = ls.pop()
        return self.mergelist(ls, self.merge(ps, deff))
    
    def fit(self, ext1, ext2, subtreeOffset, siblingOffset, i):
        '''do computation within the same level of the subtrees of the toplevel siblings'''
        if len(ext1)<=i or len(ext2)<=i: return 0 
        p, q = ext1[i][1], ext2[i][0]
        return max(self.fit(ext1, ext2, subtreeOffset, siblingOffset, i+1) + subtreeOffset,\
                   p-q+siblingOffset)
        
    def fitlistl(self, es, subtreeOffset, siblingOffset):
        def fitlistll(acc, es, i):
            #i is depth
            if len(es)<=i: return []
            e = es[i]
            ans = self.fit(acc, e, subtreeOffset, siblingOffset, 0)
            return [ans]+(fitlistll(self.merge(acc, self.moveextent(e, ans)), es, i+1))
        return fitlistll([], es,0)
    
    def fitlistr(self, es, subtreeOffset, siblingOffset):
        def fitlistrr(acc, es, i):
            if len(es)<=i: return []
            e = es[i]
            ans = -self.fit(e, acc, subtreeOffset, siblingOffset,0)
            return [ans]+(fitlistrr(self.merge(self.moveextent(e, ans), acc), es, i+1))
        ans = fitlistrr([], list(reversed(es)), 0)
        return list(reversed(ans))

    def fitlist(self, es, subtreeOffset, siblingOffset):
        es1 = copy.deepcopy(es)
        es2 = copy.deepcopy(es)
        esl = self.fitlistl(es1, subtreeOffset, siblingOffset)
        esr = self.fitlistr(es2, subtreeOffset, siblingOffset)
        ans = [0]*len(esl)
        for i in xrange(len(esl)):
            ans[i] = (esl[i]+esr[i])/2
        return ans

    def design(self, graph, node, prop, config):
        orn = config.orientation
        auxp = ['x', 'y']
        auxs = ['width', 'height']
        ind = (orn=='left' or orn=='right')
        p, notp = auxp[ind], auxp[1-ind]
        cnode = DirNode(self.scene)
        s, nots = auxs[ind], auxs[1-ind]
        siblingOffset = config.siblingOffset
        subtreeOffset = config.subtreeOffset
        params = (graph, prop, config, s, nots, p, notp, cnode, siblingOffset, subtreeOffset)
        def designn(node, maxsize, acum, params):
            graph, prop, config = params[0], params[1], params[2]
            s, nots, p, notp = params[3], params[4], params[5], params[6]
            cnode, siblingOffset, subtreeOffset = params[7], params[8], params[9]
            sval = node[s]
            notsval = maxsize or node[nots]
            trees, extents, chmaxsize = [], [], False
            chacum = notsval + config.levelDistance
            for n in node.children:
#                 if True or n.exist: # change
                if n.exist:
                    if not chmaxsize:
                        chmaxsize= self.getBoundaries(graph, config, n.depth)
                    else:
                        chmaxsize=Size(n.width, n.height)
                    s = designn(n, chmaxsize[nots], acum+chacum, params)
                    trees.append(s.tree)
                    extents.append(s.extent)
            positions = self.fitlist(extents, subtreeOffset, siblingOffset)
            ptrees, pextents = [], []
            for i in xrange(len(trees)):
                self.movetree(trees[i], prop, positions[i], orn)
                pextents.append(self.moveextent(extents[i], positions[i]))
            resultextent = [[-sval/2, sval/2]]+self.mergelist(pextents)
            pp = 0 if p=='x' else 1
            node[prop][pp] = 0
            notpp = 0 if notp=='x' else 1
            if orn=='top' or orn=='left':
                node[prop][notpp] = acum
            else:
                node[prop][notpp] = -acum
            return Subtree(node, resultextent)
        xx = designn(node, False, 0, params)
        '''test'''
#         queue = [self.graph.root]
#         print '-------'
#         while len(queue)>0:
#             node = queue.pop(0)
#             print node.path, node.xy
#             queue.extend(node.children)
        
    '''Calculates the max width and height nodes for a tree level'''
    def getBoundaries(self, graph, config, level):
        dim = DirNode(self.scene)
        return Size(dim.width, dim.height)
        
    '''Nodes to expand'''
    def getNodesToShow(self, node=None):
        nodeArray = []
        if not node: node = self.clickedNode
        levelNodes = self.graph.eachLevel(node, 0, self.config.levelsToShow)
        for alevel in levelNodes:
            for n in alevel:
                if n.drawn and not self.graph.anySubnode(n, 'drawn'):
                    nodeArray.append(n)
        return nodeArray
    
    '''Nodes to collapse or no need to show its subtrees'''
    def getNodesToHide(self, node=None):
        if not node:
            node = self.clickedNode
        geom = self.geom
        graph = self.graph
        level = node.depth
        nodeArray = []
        for n in graph.nodeDict.values():
            if n.exist and not n.selected:
                if graph.isDescendantOf(n, node.path):
                    if n.depth <= level: 
                        nodeArray.append(n)
                elif n.depth>0:
                    nodeArray.append(n)
        leafLevel = geom.getRightLevelToShow(node, self.scene)
        leafLevelNodes = graph.eachLevel(node, leafLevel, leafLevel)
        for level in leafLevelNodes:
            for c in level:
                if c.exist and not c.selected: nodeArray.append(c)
        for i in xrange(len(self.nodesInPath)):
            n = graph.getNode(self.nodesInPath[i])
            if not graph.isDescendantOf(n, node.path):
                nodeArray.append(n)
        return nodeArray
    
    '''
    Method: compute
    Computes nodes' positions.
    '''
    def compute(self, propertyy='startPos', computeLevels=True):
        node = self.graph.root
        node.drawn = True
        node.setVisible(True)
        node.exist = True
        node.selected = True
        if computeLevels or node.depth==-1:
            self.graph.computeLevels(self.root.path, 0, 'ignore')
        self.computePositions(node, propertyy)
        self.computeRelativePos(node, propertyy)
        
    def computeRelativePos(self, node, prop):
        startX, startY = self.scene.canvasX, self.scene.canvasY+0.5*self.scene.canvasH
        for n in self.graph.nodeDict.values():
            if True or n.exist: #change
                if prop!='startPos':
                    n.startPos[0], n.startPos[1] = n.xy[0], n.xy[1]
                n[prop][0] += startX
                n[prop][1] += startY
                n.setAbsolutePos(n[prop][0], n[prop][1])
            
    def computePositions(self, node, prop):
        self.design(self.graph, node, prop, self.config)
        orn = self.config.orientation
        i = (orn=='left' or orn=='right' )#['x', 'y'][orn=='left' or orn=='right']
        def red(x):
            for c in x.children:
                if c.exist:
                    c[prop][i] += x[prop][i]
                    red(c)
        red(node)
        
    '''
    Method: select
     Selects a node in the <ST> without performing an animation. Useful when selecting
     nodes which are currently hidden or deep inside the tree.
    Parameters:
     id - (string) The id of the node to select.
     onComplete - (optional|object) an onComplete callback.
     
    Example:
    (start code js)
        st.select('mynodeid', {
          onComplete: function() {
            alert('complete!');
          }
        });
    (end code)
    '''
        
    def select(self, path, onComplete=None):
        group  = self.group
        geom = self.geom
        node = self.graph.getNode(path)
        scene = self.scene
        if not self.root: self.root = node
        complete = onComplete
        self.selectPath(node)
        self.clickedNode = node
        def onComplete():
            group.hide(group.prepare(self.getNodesToHide()), complete)
            geom.setRightLevelToShow(node, scene)
            self.compute('xy') #change
            for n in self.graph.nodeDict.values():
                n.startPos = n.xy
                n.endPos = n.xy
                n.visited = False
            self.geom.translate((node.endPos[0]*(-1),node.endPos[1]*(-1)), ['xy', 'startPos', 'endPos'])
            group.show(self.getNodesToShow())
        self.requestNodes(node, onComplete)
    
    def selectPath(self, node):
        for n in self.graph.nodeDict.values():
            n.selected = False
        '''show all nodes along the path from the root to the specified node and its siblings'''
        def path(node):
            if node==None or node.selected: return
            node.selected = True
            for n in self.group.getSiblings([node])[node.path]:
                '''change'''
                if n.depth >=0:
                    ''''''
                    n.exist = True
                    n.drawn = True
                    n.setVisible(True)
            path(node.parent)
        self.clickedNode = node
        ns = [node.path] + (self.nodesInPath)
        for n in ns:
            path(self.graph.getNode(n))
            
    '''
    Method: addNodeInPath
        Adds a node to the current path as selected node. The selected node will be visible (as in non-collapsed) at all times.
        Parameters:
       path - (string) the path of a <DirNode>.
    '''
    def addNodeInPath(self, path):
        self.nodesInPath.append(path)
        self.select((self.clickedNode and self.clickedNode.path) or self.root)
    
    '''
    Method: clearNodesInPath
       Removes all nodes tagged as selected by the <STLayout.addNodeInPath> method.
    '''
    def clearNodesInPath(self, path):
        self.nodesInPath = []
        self.select((self.clickedNode and self.clickedNode.path) or self.root)
        
    '''
    Method: refresh
    Computes positions and plots the tree
    '''
    def refresh(self):
        self.reposition()
        self.select((self.clickedNode and self.clickedNode.path) or self.root)
        
    def reposition(self):
        self.graph.computeLevels(self.root, 0, 'ignore')
        self.geom.setRightLevelToShow(self.clickedNode, self.scene)
        for n in self.graph.nodeDict.values():
            if n.exist: n.drawn = True
        self.compute('endPos')
        if self.clickedNode:
            offset = ((self.scene.translateOffsetX + self.config.offsetX) or 0,\
                      (self.scene.translateOffsetY + self.config.offsetY) or 0)
            self.geom.translate(((self.clickedNode.endPos[0]+offset[0])*(-1), \
                                (self.clickedNode.endPos[1]+offset[1])*(-1)), ['endPos'])
            
    def contract(self, onComplete=None):
        nodes = self.getNodesToHide()
#         for n in nodes:
#             print n.path
#         print '----contract-----'
        controller = copy.copy(self.controller)
        controller.onComplete = onComplete
        self.group.contract(nodes, controller)
        
    def move(self, node, move, onComplete):
        self.compute('endPos', False)
        offset = (move.offsetX, move.offsetY)
        self.geom.translate(((node.endPos[0]+offset[0])*(-1), (node.endPos[1]+offset[1])*(-1)), ['endPos'])
        onComplete()

    def expand(self, node, onComplete):
        nodeArray = self.getNodesToShow(node)
        controller = self.controller
        controller.onComplete = onComplete
        self.group.expand(nodeArray, controller)
        
    '''
    Method: addSubtree
        Adds a subtree.
    Parameters:
          subtree - (object) A Tree object.
          method - (string) Set this to "animate" if you want to animate the tree after adding the subtree. You can also set this parameter to "replot" to just replot the subtree.
          onComplete - (optional|object) An action to perform after the animation (if any).
    '''
    def addSubtree(self, subtree, method, onComplete):
        if method == 'replot':
            self.op.sum(subtree, {type:'replot'}, onComplete)
        elif method == 'animate':
            self.op.sum(subtree, {type:'fade:seq'}, onComplete)
    '''
    Method: removeSubtree
        Removes a subtree.
       Parameters:
          path - (string) The _path_ of the subtree to be removed.
          removeRoot - (boolean) Default's *false*. Remove the root of the subtree or only its subnodes.
          method - (string) Set this to "animate" if you want to animate the tree after removing the subtree. You can also set this parameter to "replot" to just replot the subtree.
          onComplete - (optional|object) An action to perform after the animation (if any).
    '''
    def removeSubtree(self, path, removeRoot, method, onComplete):
        node = self.graph.getNode(path)
        subids = []
        levelNodes = self.graph.eachLevel(node, (not removeRoot), False)
        for alevel in levelNodes:
            for n in alevel:
                subids.push(n.path)
        if method == 'replot':
            self.op.removeNode(subids, {type:'replot'}, onComplete)
        elif method == 'animate':
            self.op.removeNode(subids, {type:'fade:seq'}, onComplete)
            
    '''
    Method: onClick
    This method is called when clicking on a tree node. It mainly performs all calculations and the animation of contracting, translating and expanding pertinent nodes.
        Animates the <ST> to center the node specified by *id*.
        Parameters:
        id - (string) A node id.
        options - (optional|object) A group of options and callbacks described below.
        onComplete - (object) An object callback called when the animation finishes.
        Move - (object) An object that has as properties _offsetX_ or _offsetY_ for adding some offset position to the centered node.
    '''
    def onClick(self, path, options={}):
        scene = self.scene
        geom = self.geom
        fx = self.fx
        config = self.config
        graph = self.graph
        ''''''
        def Move(): return
        Move.offsetX, Move.offsetY = scene.translateOffsetX+config.offsetX or 0,\
                                scene.translateOffsetY+config.offsetY or 0
        ''''''
        node = graph.getNode(path)
        self.selectPath(node)
        self.clickedNode = node
        def onComplete1():
            def onComplete2():
                geom.setRightLevelToShow(node, scene)
                def onComplete3():
                    def onComplete4():
                        return
                    self.expand(node, onComplete4)
                    '''----------expand----------'''
                self.move(node, Move, onComplete3)
                '''----------move----------'''
            self.contract(onComplete2)
            '''----------contract----------'''
        onComplete1()
        self.getNodesToDraw()
        self.scene.scaleObjectGraph()
    
    def requestNodes(self, node, onComplete=None):
        handler = self.controller
        level = self.config.levelsToShow
        '''no request for json graph'''
        if False and handler.request:
            ''''''
            leaves = []
            d = node.depth
            def func(n):
                if n.drawn and not n.children:
                    leaves.append(n) #get nodes with no children in the original graph
                    n.level = level-(n.depth-d) #The level as in the graph to display starting from 0
            levelNodes = self.graph.eachLevel(node, 0, level)
            for alevel in levelNodes:
#                 print '------alevel-------'
                for n in alevel:
#                     print n.path
                    func(n)
#             print '------leaves-------'
#             for n in leaves:
#                 print n.path
            self.group.requestNodes(leaves, handler)
        onComplete()
    
    '''Method: set first level'''
    def setFirstLevel(self, path, method='replot'):
        callback = {'execHide': True}
        scene = self.scene
        self.graph.clickedNode = clickedNode = self.graph.getNode(path)
        self.graph.root = self.root = clickedNode
        self.graph.computeLevels(path, 0, 'ignore')
        def onShow(node):
            if not node.drawn and (node.parent and node.parent.expanded): #do not expand the unexpanded nodes
                node.exist = True
                node.drawn = True
                node.setVisible(True)
                self.nodesDraw2.add(node)
        callback['onShow']=onShow
        self.geom.setRightLevelToShow(clickedNode, scene, callback)
        self.compute('endPos', False)
        
    '''
    Method: setRoot
             Switches the current root node. Changes the topology of the Tree.
            Parameters:
               id - (string) The id of the node to be set as root.
               method - (string) Set this to "animate" if you want to animate the tree after adding the subtree. You can also set this parameter to "replot" to just replot the subtree.
               onComplete - (optional|object) An action to perform after the animation (if any).
    '''
    def setRoot(self, path, method='replot', onComplete=None):
        if self.busy: return
        self.busy = True
        scene = self.scene
        self.graph.clickedNode = clickedNode = self.graph.getNode(path)
        self.graph.root = self.root = clickedNode
        self.graph.computeLevels(path, 0, 'ignore')
        callback = {'execHide': True}
        def onShow(node):
            if not node.drawn:
                node.exist = True
                node.drawn = True
                node.setVisible(True)
        callback['onShow']=onShow
        self.geom.setRightLevelToShow(clickedNode, scene, callback)
        '''for no animation'''
        def onComplete2():
            onComplete and onComplete.onComplete()
        self.onClick(path, onComplete2)
#         if method == 'animate':
#             self.selectPath(clickedNode)
#         elif method == 'replot':
#             self.select(self.root.path)
        for n in self.nodesDraw2:
            n.setOpacity(1)
        self.busy = False
    
    def fitTreeInLevel(self, selectedNode, translateDirec = 0):
        diff = self.config.levelsToShow
        n = selectedNode
        while diff>0 and n.parent:
            n = n.parent
            diff -= 1
        '''
        find if there is any other nodes on the last level after collapsing a node
        if not, move up a level; otherwise, stay still
        '''
        for nn in self.nodesDraw2:
            if (not self.clickedNode.expanded) and (nn.depth == self.clickedNode.depth+1):
                n = self.root
        if translateDirec==0:
            self.setRoot(n.path)
        else: 
            '''for expanding node and collapsing node'''
            self.setFirstLevel(n.path)

    def setOpacityOfDrawnNodes(self):
        for n in self.nodesDraw2:
            if n.selected or n in self.clickedNode.children:
                n.setOpacity(1)
            else:
                n.setOpacity(0.3)
                
    def getNodesToDraw(self):
        self.nodesDraw1 = self.nodesDraw2
        self.nodesDraw2 = set()
        for n in self.graph.nodeDict.values():
            if n.drawn:
                self.nodesDraw2.add(n)