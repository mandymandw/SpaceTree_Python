'''
Created on Aug 21, 2018

@author: manw
'''
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QMessageBox
from DirNode import DirNode
# from DirEdge import DirEdge
from Graph import Graph
from STLayout import STLayout
from collections import namedtuple
UNIXPerm = namedtuple('UNIXPerm', ('perms', 'user', 'group'))

class DiagramScene(QGraphicsScene):

    def __init__(self, main):
        super(DiagramScene, self).__init__(main)
        
        self.main = main
        self.margin_vertical = 20
        self.margin_horizontal = 10
        self.canvasX, self.canvasY = self.margin_horizontal, self.margin_vertical
        self.canvasW, self.canvasH = self.sceneRect().width()-2*self.margin_horizontal,\
                                     self.sceneRect().height()-2*self.margin_vertical
        '''For drawing graphs'''
        self.graph = Graph(self) #Access a <Graph> instance.
        '''set pos for canvas'''
        self.translateOffsetX, self.translateOffsetY = 0, 0
        self.scaleOffsetX, self.scaleOffsetY = 1,1
    
    def checkInputPath(self, path):
        if len(path)>1 and path[-1] == '/':
            path = path[0:len(path)-1]
            self.main.searchLineEdit.setText(path)
        if path not in self.graph.nodeDict.keys():
            QMessageBox.warning(self.main, '', 'The specified object does not exist!')
            return None
        return path
            
    def confirmSearch(self):
        path = self.main.searchLineEdit.text()
        path = self.checkInputPath(path)
        if not path: return
        self.layout.onClick(path)
#         self.layout.select(path)
        self.layout.setRoot(path)
        self.update()
        
    def processCrawlerResult(self, filename):
        import os.path
        if not os.path.exists(filename): return 
        directories = {}
        f = open(filename, 'r')
        for line in f.readlines():
            path, perm, uowner, gowner= line.split('\t')
            directories[path] = UNIXPerm(perm, uowner, gowner)
        return directories
    
    def createGraph(self, directories):
        self.view = self.main.centralWidget()
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.graph.createGraph(directories)
        self.layout = STLayout(self.graph.root, self.graph.nodeDict, self)
        self.layout.onClick(self.graph.root.path)
#         self.translate(0, 300)
#         self.view.translate(0,300)
#         pos = self.view.mapToScene(self.graph.root.pos().x(),self.graph.root.pos().y())
        
    def updateAllItemPos(self):
        for i in self.items():
            if isinstance(i, DirNode):
                i.setPos(i.relativeX, i.relativeY)
        self.update()

    '''
    Method: translate
      
      Applies a translation to the canvas.
      
      Parameters:
      
      x - (number) x offset.
      y - (number) y offset.
      disablePlot - (boolean) Default's *false*. Set this to *true* if you don't want to refresh the visualization. 
    '''
#     def translate(self, x, y, disablePlot=False):
#         self.translateOffsetX += x*self.scaleOffsetX
#         self.translateOffsetY += y*self.scaleOffsetY
#         self.view.translate(x, y)
#         print x, y
#         pos = self.view.mapToScene(x,y)
#         print pos.x(), pos.y()
#         for i in self.items():
#             i.setPos(pos.x(), pos.y())
#         if not disablePlot:
#             self.update()
# 
    '''Method: scale
       
      Scales the canvas.
       
      Parameters:
       
      x - (number) scale value.
      y - (number) scale value.
      disablePlot - (boolean) Default's *false*. Set this to *true* if you don't want to refresh the visualization.
    '''
    def scale(self, x, disablePlot=False):
        y = x
        px, py = self.scaleOffsetX * x, self.scaleOffsetY * y
#         dx, dy = self.translateOffsetX*(x-1)/px, self.translateOffsetY*(y-1)/py
        self.scaleOffsetX, self.scaleOffsetY = px, py
        self.view.scale(x,y)
#         self.view.translate(dx, dy)
        self.scaleGraph(1/x)
        self.update()
    
    def scaleGraph(self, ratio):
        for i in self.items():
            if isinstance(i, DirNode):
                i.setScale(ratio)
    
    def scaleObjectGraph(self):
        import sys
        topLeftX, topLeftY, bottomRightX, bottomRightY = sys.maxint, sys.maxint, 0, 0
        for n in self.layout.nodesDraw2:
            topLeftX = min(topLeftX, n.xy[0])
            topLeftY = min(topLeftY, n.xy[1])
            bottomRightX = max(bottomRightX, n.xy[0])
            bottomRightY = max(bottomRightY, n.xy[1])
        width, height = bottomRightX-topLeftX, bottomRightY-topLeftY
#         print topLeftX, topLeftY, self.scaleOffsetX*width, self.scaleOffsetX*height, self.width(), self.height()
        ratio = max((1.0*self.scaleOffsetY*height)/self.height(), (1.0*self.scaleOffsetX*width)/self.width())
#         print ratio
        if ratio>1:
            self.scale(0.9/ratio)
#             self.view.centerOn(topLeftX+0.5*self.width(), topLeftY+0.5*self.height())
              
    def clearScreen(self):
        for i in self.items():
            i.exit = False
            i.drawn = False
            i.setVisibile(False)
