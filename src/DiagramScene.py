'''
Created on Aug 21, 2018

@author: manw
'''
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from DirNode import DirNode
# from DirEdge import DirEdge
from Graph import Graph
from STLayout import STLayout
        
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
        
#         self.timer = QTimer(5000)
#         self.timer.setFrameRawnge(0,100)
#         self.timer.timeout().connect(self.animateDirNodeExpansion)
    
    def drawDirNodes(self):
        self.layout = STLayout(self.graph.root, self.graph.nodeDict, self)
        self.layout.config.levelsToShow = 2
        self.layout.onClick(self.graph.root.path)
#         self.layout.select('/classes/security')
# #         self.layout.select('/tools/t3/school')
#         '''need to add filepath check, remove last slash'''
#         self.layout.fitTreeInLevel(self.graph.getNode('/classes/security'))
    
    def createGraph(self):
        self.view = self.main.centralWidget()
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
#         directories = ['/', '/tools', '/home', '/classes/os', '/classes/security', '/classes/security/public', '/classes/os/public']
#         directories = ['/']
        directories = ['/', '/tools/t2/mine', '/tools/t1/mine', '/tools/t3/school/mine' ,'/home', '/classes/os', '/classes/security', '/classes/security/public', '/classes/os/public']

        self.graph.createGraph(directories)
#         n1 = self.createDirNode('1', id)
#         n2 = self.createDirNode('2')
#         n3 = self.createDirNode('3')
#         e1 = self.createDirEdge(n1, n2)
#         e2 = self.createDirEdge(n1, n3)
        self.drawDirNodes()
#         self.translate(0, 300)
#         self.view.translate(0,300)
#         print self.graph.root.pos()
#         pos = self.view.mapToScene(self.graph.root.pos().x(),self.graph.root.pos().y())
#         print pos.x(), pos.y()
#         self.graph.root.setPos(pos.x()/self.canvasW, pos.y()/self.canvasY)
#         self.scale(.8, .8)

        
#     def animateDirNodeExpansion(self):
#         animations = []
#         for c in self.root.children:
#             c.setVisible(True)
#             animation = QPropertyAnimation(c, b"pos")
#             animation.setDuration(5);  # 5 seconds
#             animation.setStartValue(self.root.pos())
#             animation.setEndValue(c.pos())
#             animation.setEasingCurve(QEasingCurve.Linear)
#             animations.append(animation)
#         #Construct a parallel animation containg "animation" and "animation2"
#         animgroupPara = QParallelAnimationGroup()
#         for a in animations:
#             animgroupPara.addAnimation(a)
#         animgroupPara.start()

    
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
            i.drawn = False
            i.setVisibile(False)
            
    def mousePressEvent(self, event):
#         self.updateAllItemPos()
#         self.timer.start(1000)
        return QGraphicsScene.mousePressEvent(self, event)