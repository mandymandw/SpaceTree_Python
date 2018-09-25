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
rad = 5

def getLabel(node):
    return node.path.split('/')[-1]

# class DirNode(QGraphicsEllipseItem):
#     DIST_NODE_TEXT = 5
#     node_onclick = pyqtSignal(QGraphicsItem)
#     
#     def __init__(self, scene=None, path=''):
#         QGraphicsEllipseItem.__init__(self, -rad, -rad, 2*rad, 2*rad)
#         self.main = scene.main
#         self.scene = scene
class DirNode(QGraphicsObject):
    def __init__(self, scene=None, path=''):
        QGraphicsObject.__init__(self)
        self.main = scene.main
        self.scene = scene
        
        '''
        Determine whether or not nodes properties can be overriden by a particular node. Default's false.
        If given a JSON tree or graph, a node _data_ property contains properties which are the same as defined here but prefixed with 
        a dollar sign (i.e $), the node properties will override the global node properties.
        '''
        self.width, self.height = 2*rad, 2*rad
        self.exist = True  # Flag to display the node or not
        self.drawn = False # Flag for the visually drawing of the node on canvas. True means it is already drawn
        self.selected = False 
                
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
        self.startPos = [0,0,1] #x,y,alpha
        self.endPos = [0,0,1]
        
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setVisible(False)
        self.setToolTip(self.path)
        
    def __getitem__(self,key):
        return getattr(self,key)

    def boundingRect(self):
        rad = 6
        return QRectF(-rad, -rad, 2*rad, 2*rad)

    def paint(self, painter, option, widget=None):
        '''set fill color'''
        painter.setBrush(QBrush(Qt.white))
        if self.children and not self.expanded:
            painter.setBrush(QColor(166,189,219))
        '''
        draw outline
        '''
        if self.selected:
            painter.setPen(QPen(Qt.red,2))
        else:
            painter.setPen(QPen(QColor(43,140,190),2))
        painter.drawEllipse(self.boundingRect()) 
        '''
        display self.label as label
        '''
        painter.setPen(QPen(Qt.black))
        if self == self.scene.layout.root:
            self.displayname = self.path
        else:
            self.displayname = self.label
        self.labelRect = painter.fontMetrics().boundingRect(self.displayname)
        '''top'''
#         x = int(self.rect().bottomLeft().x())
#         y = int(self.rect().topLeft().y()-self.labelRect.height())
        '''right side'''
        x = int(self.boundingRect().bottomLeft().x()+(self.boundingRect().width()+5))
        y = int(self.boundingRect().topLeft().y()-0.5*self.boundingRect().height()+0.25*self.labelRect.height())
        self.paintLabel(painter, x, y)
                
    def paintLabel(self, painter, x, y):
        rect = self.labelRect
        rect.moveTo(x, y)
        painter.drawText(rect, Qt.AlignLeft, self.displayname)
    
    def setAbsolutePos(self, x, y):
        self.xy[0], self.xy[1] = x,y
        self.relativeX = (self.xy[0]-self.scene.canvasX)/self.scene.canvasW
        self.relativeY = (self.xy[1]-self.scene.canvasY)/self.scene.canvasH
        QGraphicsObject.setPos(self, QPointF(self.xy[0],self.xy[1]))
        
    def setPos(self, rx, ry):
        self.relativeX, self.relativeY = rx, ry
        self.xy[0], self.xy[1] = self.scene.canvasX + rx*self.scene.canvasW, self.scene.canvasY + ry*self.scene.canvasH
        QGraphicsObject.setPos(self, QPointF(self.xy[0],self.xy[1]))
    
    def mousePressEvent(self, event):
        QGraphicsObject.mousePressEvent(self, event)
        self.scene.layout.selectPath(self)
        if not self.expanded:
            self.scene.layout.expandNode(self, True)
        else:
            self.scene.layout.collapseNode(self,True)
        
        self.scene.update()