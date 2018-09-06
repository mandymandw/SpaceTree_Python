'''
Created on Sep 3, 2018

@author: manw
'''

import copy, types

def copy_func(f, name=None):
    return types.FunctionType(f.func_code, f.func_globals, name or f.func_name,
        f.func_defaults, f.func_closure)
    
def merge_two_dicts(x,y):
    z = x.copy()
    for yk in y.keys():
        if yk not in z.keys():
            z.update({yk:y[yk]})
        else:
            if type(z[yk]) is list:
                tmp = set(z[yk]).union(set(y[yk]))
                z[yk] = list(tmp)
    return z

class Options(object):

    def __init__(self, viz):
        self.viz = viz
    
    def removeNode(self, node, opt, onComplete={}):
        '''
        Method: removeNode
        
           Removes one or more <Graph.Nodes> from the visualization. 
           It can also perform several animations like fading sequentially, fading concurrently, iterating or replotting.
           
           Parameters:
            node - (string|array) The node's id. Can also be an array having many paths.
            opt - (object) Animation options. It's an object with optional properties described below
            type - (string) Default's *nothing*. Type of the animation. Can be "nothing", "replot", "fade:seq",  "fade:con" or "iter".
            duration - Described in <Options.Fx>.
            fps - Described in <Options.Fx>.
            transition - Described in <Options.Fx>.
        '''
        viz = self.viz
        options = merge_two_dicts(merge_two_dicts(self.options, viz.controller), opt)
        if opt.type == 'nothing':
            for i in xrange(len(node)):
                viz.graph.removeNode(node[i])
        elif opt.type == 'replot':
            self.removeNode(node, {type:'nothing'})
            viz.refresh(True)
        elif opt.type == 'fade:seq':
            for i in xrange(len(node)):
                nodeObj = viz.graph.getNode(node[i])
                nodeObj.endPos[2] = 0
            def onComplete1():
                self.removeNode(node, {type:'nothing'})
                viz.reposition()
                viz.fx.animate(merge_two_dicts(options, {'modes':['linear']}))
            viz.fx.animate(merge_two_dicts(options, {'modes':['node-property:alpha']}, onComplete1))
        
        
class Plot(object):
    
    def __init__(self, viz):
        self.viz = viz
#         
        self.Interpolator = {
            #node/edge property parsers
            'map': {
              'border': 'color',
              'color': 'color',
              'width': 'number',
              'height': 'number',
              'dim': 'number',
              'alpha': 'number',
              'lineWidth': 'number',
              'angularWidth':'number',
              'span':'number',
              'valueArray':'array-number',
              'dimArray':'array-number',
              'vertices':'polygon'
            },
            'compute': lambda fromm, to, delta: self.compute(fromm, to, delta),
            'linear': lambda elem, props, delta: self.linear(elem, props, delta),
            'node': lambda elem, props, delta, mapp, getter, setter: self.node(elem, props, delta, mapp, getter, setter),
            'node-property': lambda elem, props, delta: self.nodeProperty(elem, props, delta)
        }
    
    def compute(self, fromm, to, delta):
        return (fromm + (to - fromm) * delta)
    
    def linear(self, elem, props, delta):
        fromm = elem.startPos
        to = elem.endPos
        elem.pos = (self.compute(fromm[0], to[0], delta),\
                      self.compute(fromm[1], to[1], delta))
        
    def nodeProperty(self, elem, props, delta):
        self.node(elem, props, delta, 'map', 'getData', 'setData')
#     
    def node(self, elem, props, delta, mapp, getter, setter):         
        mappp = self.Interpolator[mapp]
        if props:
            length = len(props)
            for i in xrange(length):
                pi = props[i]
                self.Interpolator[mappp[pi]](elem, pi, delta, getter, setter)
        else:
            for pi in mappp.keys():
                self.Interpolator[mappp[pi]](elem, pi, delta, getter, setter)
#     
    def animate(self, opt, onComplete=None, versor=None):
        opt = merge_two_dicts(self.viz.config, opt or {})
        viz = self.viz
        graph = viz.graph
        interp = self.Interpolator
        animation = self.nodeFxAnation if opt.type == 'nodefx' else self.animation
        #prepare graph values
        m = self.prepare(opt.modes)
        #animate
        def compute1(delta):
            for node in graph.nodeDict.values():
                for p in m:
                    interp[p](node, m[p], delta, versor)
        other = {'animating': False, 'compute': compute1}
        options = merge_two_dicts(opt, other)
        animation.SetOptions(options)
        self.plot(options, self.anmating, delta)
#         
    def plotLine(self, edge, canvas, animating):
        if not edge: 
            return
        edge.setVisible(True)
        '''then deal with animating'''
#     
    def plotNode(self, node, canvas):
        node.setVisible(True)
        '''add some animation'''
         
    '''plot a subtree from the spacetree'''
    def plotSubtree(self, node, opt, scale, animating='nothhing'):
        viz = self.viz
        scene = viz.scene
        scale = min(max(0.001, scale), 1)
#         if scale >=0:
#             node.drawn = False
#             diff = viz.geom.getScaledTreePosition(node, scale)
#             scene.translate(diff[0], diff[1])
#             scene.scale(scale, scale)
        self.plotTree(node, not scale, opt, animating)
        if scale>=0: node.drawn = True
        
    '''plot a subtree'''
    def plotTree(self, node, opt, animating):
        viz = self.viz
        scene = viz.scene
        nodeAlpha = node.pos[2]
        for elem in node.children:
            if elem.exist:
                if elem.drawn:
                    adj = viz.graph.edgeDict[elem]
                    for e in adj.values():
                        self.plotLine(e, scene, animating)
                self.plotTree(elem, opt, animating)
        if node.drawn:
            self.plotNode(node, scene, animating)
         
    '''
    Method: plot
     
       Plots a <Graph>.
       Parameters:
       opt - (optional) Plotting options. Most of them are described in <Options.Fx>.
    '''
    def plot(self, opt, animating):
        viz = self.viz
        agraph = viz.graph
        scene = viz.scene
        rootpath = viz.root
        opt = opt or self.viz.controller
         
        if opt.clearCanvas:
#             scene.clear()
            scene.clearScreen()
             
        root = agraph.getNode(rootpath)
        if not root: return
         
        T = not (not root.visited)
        for node in agraph.nodeDict.values():
            nodeAlpha = node.pos[2]
#             def func(adj):
#                 nodeTo = adj.endItem
#                 if ((not (not nodeTo.visited))==T and node.drawn and nodeTo.drawn):
#                     self.plotLine(adj, scene, animating)
#             agraph.eachAdjacency(node, func)
            if node.drawn:
                self.plotNode(node, scene, animating)
            node.visited = not T
        
        