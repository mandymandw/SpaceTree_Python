'''
Created on Aug 21, 2018

@author: manw
'''
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.font_manager import path

def computeControlPointForBezierCurve(point1, point2):
    ratio = 0.7
    midx = ratio*point1.pos().x()+(1-ratio)*point2.pos().x()
    midy = ratio*point1.pos().y()+(1-ratio)*point2.pos().y()
    if point1.angle<point2.angle:
        c1 = QPointF((1-ratio)*point1.pos().x()+ratio*midx, (1-ratio)*point1.pos().y()+ratio*midy) 
        c2 = QPointF((1-ratio)*point2.pos().x()+ratio*midx, (1-ratio)*point2.pos().y()+ratio*midy) 
    else:
        c1 = QPointF(ratio*point2.pos().x()+(1-ratio)*midx, ratio*point1.pos().y()+(1-ratio)*midy) 
        c2 = QPointF(ratio*point1.pos().x()+(1-ratio)*midx, ratio*point2.pos().y()+(1-ratio)*midy) 
    return c1, c2

# def getControlPoints(x0,y0,x1,y1,x2,y2,t):
#     import math
#     d01 = math.sqrt(math.pow(x1-x0,2)+math.pow(y1-y0,2))
#     d12 = math.sqrt(math.pow(x2-x1,2)+math.pow(y2-y1,2))
#     fa = t*d01/(d01+d12)   # scaling factor for triangle Ta
#     fb = t*d12/(d01+d12)   # ditto for Tb, simplifies to fb=t-fa
#     p1x = x1-fa*(x2-x0)    # x2-x0 is the width of triangle T
#     p1y = y1-fa*(y2-y0)    # y2-y0 is the height of T
#     p2x = x1+fb*(x2-x0)
#     p2y = y1+fb*(y2-y0) 
#     return [p1x,p1y,p2x,p2y]
'''
Dir
'''
class DirEdge(QGraphicsLineItem):
    def __init__(self, scene=None, startItem=None, endItem=None):
        super(DirEdge, self).__init__()
        self.scene = scene
        self.main = scene.main
        '''    
        overridable_ Determine whether or not edges properties can be overriden by a particular edge object. Default's false.
        If given a JSON _complex_ graph (defined in <Loader.loadJSON>), an adjacency _data_ property contains properties which are the same as defined here but prefixed with 
        a dollar sign (i.e $), the adjacency properties will override the global edge properties.
        '''
        self.ignore = False
        self.startItem = startItem
        self.endItem = endItem
        self.highlighted = False
        self.drawn = False
        
        self.setZValue(0)

    def __getitem__(self,key):
        return getattr(self,key)
    
    def updateElement(self, index, pos):
        path.setElementPositionAt(index, pos.x(), pos.y())
        self.setPath(path)
        
    def shape(self):  
        c1, c2 = computeControlPointForBezierCurve(self.startItem, self.endItem)
        myPath = QPainterPath()
        myPath.moveTo(self.startItem.pos())
        myPath.cubicTo(c1, c2, self.endItem.pos())
        return myPath
    
    def paint(self, painter, option, widget=None):
        if self.startItem.collidesWithItem(self.endItem):
            return
         
        if not self.startItem.isVisible() or not self.endItem.isVisible():
            return 
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        pen = QPen(Qt.SolidLine)
        pen.setWidth(2.0)
        pen.setColor(Qt.lightGray)
        painter.setPen(pen)
        painter.drawPath(self.shape()) #for beizercurve 
        
    def updatePosition(self):
        self.setPath(self.shape())
