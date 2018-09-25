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
        self.margin_horizontal = 150
        self.canvasX, self.canvasY = self.margin_horizontal, self.margin_vertical
        self.canvasW, self.canvasH = self.sceneRect().width()-2*self.margin_horizontal,\
                                     self.sceneRect().height()-2*self.margin_vertical
        '''For drawing graphs'''
        self.graph = Graph(self) #Access a <Graph> instance.
#         self.op = viz.op #Access a <ST.Op> instance.
#         self.fx = None #Access a  <ST.Plot> instance.
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
        self.layout.select(path)
        self.layout.setRoot(path)
        self.update()
        
    def drawDirNodes(self):
        self.layout = STLayout(self.graph.root, self.graph.nodeDict, self)
        self.layout.config.levelsToShow = 1
        self.layout.onClick(self.graph.root.path)
    
    def processCrawlerResult(self, filename):
        import os.path
        if not os.path.exists(filename): return 
        directories = {}
        f = open(filename, 'r')
        for line in f.readlines():
            path, perm, uowner, gowner= line.split('\t')
            directories[path] = UNIXPerm(perm, uowner, gowner)
        return directories
    
    def createGraph(self):
        self.view = self.main.centralWidget()
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
#         directories = ['/', '/tools', '/home', '/classes/os', '/classes/security', '/classes/security/public', '/classes/os/public']
#         directories = ['/']
#         directories = ['/', '/tools/t2/mine', '/tools/t1/mine', '/tools/t3/school/mine' ,'/home', '/classes/os', '/classes/security', '/classes/security/public', '/classes/os/public']
#         directories = ['/Users/manw/Documents/interview', 
#              '/Users/manw/Documents/interview/gdbiblio.pdf', 
#              '/Users/manw/Documents/interview/notes',
#              '/Users/manw/Documents/interview/cv_temp', 
#              '/Users/manw/Documents/interview/notes/main.pdf', 
#              '/Users/manw/Documents/interview/cv_temp/cv.pdf']
        directories = self.processCrawlerResult('/Users/manw/Documents/Projects/OSCrawler/InterviewCrawl.txt')
#         directories = self.processCrawlerResult('/Users/manw/Documents/Projects/OSCrawler/DownloadsCrawl.txt')
        self.graph.createGraph(directories)
        self.drawDirNodes()
#         self.translate(0, 300)
#         self.view.translate(0,300)
#         print self.graph.root.pos()
#         pos = self.view.mapToScene(self.graph.root.pos().x(),self.graph.root.pos().y())
#         print pos.x(), pos.y()
#         self.graph.root.setPos(pos.x()/self.canvasW, pos.y()/self.canvasY)
#         self.scale(.8, .8)
        
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
#     '''Method: scale
#       
#       Scales the canvas.
#       
#       Parameters:
#       
#       x - (number) scale value.
#       y - (number) scale value.
#       disablePlot - (boolean) Default's *false*. Set this to *true* if you don't want to refresh the visualization.
#     '''
#     def scale(self, x, y, disablePlot=False):
#         px, py = self.scaleOffsetX * x, self.scaleOffsetY * y
#         dx, dy = self.translateOffsetX*(x-1)/px, self.translateOffsetY*(y-1)/py
#         self.scaleOffsetX, self.scaleOffsetY = px, py
#         self.view.scale(x,y)
#         self.view.translate(dx, dy)
# #         for i in self.items():
# #             i.setPos(, )
#         if not disablePlot:
#             self.update()
    
    def clearScreen(self):
        for i in self.items():
            i.exit = False
            i.drawn = False
            i.setVisibile(False)

#     def mousePressEvent(self, event):
#         QGraphicsScene.mousePressEvent(self, event)
#         if event.buttons() == Qt.LeftButton:
#             self.layout.setRoot('/Users/manw/Documents/interview/cv_temp')