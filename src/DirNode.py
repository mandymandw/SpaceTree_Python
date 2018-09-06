'''
Created on Aug 21, 2018

@author: manw
'''

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math
'''

'''
rad = 6

def getLabel(node):
    return node.path.split('/')[-1]

# class DirNodeAnima(QGraphicsObject):

class DirNode(QGraphicsEllipseItem):
    DIST_NODE_TEXT = 5
    
    def __init__(self, scene=None, path=''):
        QGraphicsEllipseItem.__init__(self, -rad, -rad, 2*rad, 2*rad)
        self.main = scene.main
        self.scene = scene
        '''
        Determine whether or not nodes properties can be overriden by a particular node. Default's false.
        If given a JSON tree or graph, a node _data_ property contains properties which are the same as defined here but prefixed with 
        a dollar sign (i.e $), the node properties will override the global node properties.
        '''
        self.width, self.height = 2*rad, 2*rad
        self.exist = False
        self.selected = False
        self.drawn = True
        
        self.overridable = False
        self.ignore = False
        self.rad = rad
        self.path = path
        self.label = '/'+getLabel(self)
        
        self.parent = None
        self.children = set()
        self.depth = -1
        self.angle = 0
        self.expanded = False
        self.highlighted = False
        self.relativeX, self.relativeY = 0,0
        self.xy = [0,0,1]
        self.startPos = self.endPos = [0,0,1] #x,y,alpha
        
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPen(QPen(QColor(43,140,190), 3))
        self.setVisible(False)
    
    def __getitem__(self,key):
        return getattr(self,key)
       
    def paint(self, painter, option, widget=None):
        '''set fill color'''
        self.setBrush(QBrush(Qt.white))
        if self.children and not self.expanded:
                self.setBrush(QBrush(QColor(166,189,219)))
        '''
        draw outline
        '''
        QGraphicsEllipseItem.paint(self, painter, option, widget)
        if self.highlighted:
            pass
        '''
        display self.label as label
        '''
        painter.setPen(QPen(Qt.black))
        self.labelRect = painter.fontMetrics().boundingRect(self.label)
        '''top'''
        x = int(self.rect().bottomLeft().x())
        y = int(self.rect().topLeft().y()-self.labelRect.height())
        '''right side'''
#         x = int(self.rect().bottomLeft().x()+(self.rect().width()+5))
#         y = int(self.rect().topLeft().y()-0.5*self.rect().height()+0.25*self.labelRect.height())
        self.paintLabel(painter, x, y)
                
    def paintLabel(self, painter, x, y):
        rect = self.labelRect
        rect.moveTo(x, y)
        painter.drawText(rect, Qt.AlignLeft, self.label)
        
    def setAbsolutePos(self, x, y):
        self.xy = (x,y)
        self.relativeX = (self.xy[0]-self.scene.canvasX)/self.scene.canvasW
        self.relativeY = (self.xy[1]-self.scene.canvasY)/self.scene.canvasH
        QGraphicsEllipseItem.setPos(self, QPointF(self.xy[0],self.xy[1]))
        
    def setPos(self, rx, ry):
        self.relativeX, self.relativeY = rx, ry
#         self.xy = (rx*self.scene.sceneRect().width(),ry*self.scene.sceneRect().height())
#         QGraphicsEllipseItem.setPos(self, QPointF(self.xy[0],self.xy[1]))
        self.xy = (self.scene.canvasX + rx*self.scene.canvasW, self.scene.canvasY + ry*self.scene.canvasH)
        QGraphicsEllipseItem.setPos(self, QPointF(self.xy[0],self.xy[1]))
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.path.updateElement(self.index, value.toPointF())
        return QGraphicsEllipseItem.itemChange(self, change, value)
    
    def mousePressEvent(self, event):
        if not self.expanded:
            self.scene.layout.expandChildrenNode(self)
        else:
            self.scene.layout.collapseChildrenNode(self)
        QGraphicsEllipseItem.mousePressEvent(self, event)
        self.scene.updateAllItemPos()
        self.scene.update()
    
    def mouseMoveEvent(self, event):
        QGraphicsEllipseItem.mouseMoveEvent(self, event)
        self.scene.update()
        
    def mouseReleaseEvent(self, event):
        QGraphicsEllipseItem.mouseReleaseEvent(self, event)
        self.relativeX = self.pos().x()/self.scene.sceneRect().width()
        self.relativeY = self.pos().y()/self.scene.sceneRect().height()
        self.scene.update()