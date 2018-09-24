'''
Created on Sep 3, 2018

@author: manw
'''
from PyQt5.QtCore import QPropertyAnimation, QParallelAnimationGroup, QPointF, QAbstractAnimation,\
                        QTimer
from PyQt5.Qt import QEasingCurve

def setExistDrawnOfNodes(nodes, flag):
    for n in nodes:
        n.drawn = n.exist = flag
        n.setVisible(flag)
        
class Animation(object):
    '''
    *Animations*
     - _duration_ Duration of the animation in milliseconds. Default's 700.
     - _fps_ Frames per second. Default's 25.
     - _transition_ One of the transitions defined in the <Animation> class. Default's Quart.easeInOut.
     - _clearCanvas_ Whether to clear canvas on each animation frame or not. Default's true.
    '''
    TYPES = ['nothing', 'replot', 'fade:seq', 'fade:con']
    def __init__(self, viz):
        super(Animation, self).__init__()
        self.viz = viz
        self.scene = viz.scene
        self.curve = QEasingCurve(QEasingCurve.InOutQuart)
        self.type = 'nothing'
        self.nodesToShow = set()
        self.nodesToMove = set()
        self.nodesToHide = set()
        self.aniamting = False
        self.animationHideGroup = QParallelAnimationGroup()
        self.animationMoveGroup = QParallelAnimationGroup()
        self.animationShowGroup = QParallelAnimationGroup()
        self._status_update_timer = QTimer()
        self._status_update_timer.setSingleShot(False)
        self._status_update_timer.timeout.connect(self.scene.update)
        
    def setAnimatePosOptions(self, item, start, end, group):
        anim = QPropertyAnimation(item, 'pos')
        anim.setDuration(3000)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(self.curve)
        group.addAnimation(anim)
    
    def computeNodeCategory(self):
        self.nodesToShow = self.viz.nodesDraw2-self.viz.nodesDraw1
        self.nodesToHide = self.viz.nodesDraw1-self.viz.nodesDraw2
        self.nodesToMove = self.viz.nodesDraw2&self.viz.nodesDraw1
#         print 'show', ','.join(n.label for n in self.nodesToShow)
#         print 'hide',','.join(n.label for n in self.nodesToHide)
#         print 'move',','.join(n.label for n in self.nodesToMove)
        setExistDrawnOfNodes(self.nodesToHide, True)
        setExistDrawnOfNodes(self.nodesToShow, False)
        for n in self.nodesToMove:
            n.setAbsolutePos(n.startPos[0], n.startPos[1])
            
    def start(self):
#         print 'Animating...'
        '''We do 1.hide, 2.move, then 3. show'''
        self.computeNodeCategory()
        self._status_update_timer.start(20)
        if self.nodesToHide:
            self.startHideNodeAnimation()
        elif self.nodesToMove:
            self.startMoveNodeAnimation()
        elif self.nodesToShow:
            self.startShowNodeAnimation()
        
    def startHideNodeAnimation(self):
        if self.nodesToHide:
#             print '=======hide============'
            for n in self.nodesToHide:
                if n.parent:
                    self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(n.parent.startPos[0], n.parent.startPos[1]), self.animationHideGroup)
            self.animationHideGroup.finished.connect(self.endAnimation)
            self.animationHideGroup.start()
            
    def startMoveNodeAnimation(self):
        if self.nodesToMove:
#             print '=======move============'
            self.toMove = False
            for n in self.nodesToMove:
#                 print n.path, n.startPos, n.endPos
                if n.startPos==n.endPos: continue
                self.toMove = True
                self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(n.endPos[0], n.endPos[1]), self.animationMoveGroup)
            if self.toMove:
#                 n = next(iter(self.nodesToMove))
#                 print n.path, n.startPos, n.endPos
                self.animationMoveGroup.finished.connect(self.endAnimation)
                self.animationMoveGroup.start()
            else:
                self.startShowNodeAnimation()
        
    def startShowNodeAnimation(self):
        if self.nodesToShow:
            setExistDrawnOfNodes(self.nodesToShow, True)
            for n in self.nodesToShow:
                if n.parent: 
                    parentPos = n.parent.endPos
                    self.setAnimatePosOptions(n, QPointF(parentPos[0], parentPos[1]), QPointF(n.endPos[0], n.endPos[1]), self.animationShowGroup)
            self.animationShowGroup.finished.connect(self.endAnimation)
            self.animationShowGroup.start()
            
    def endAnimation(self):
        if self.nodesToHide:
            self.animationHideGroup.stop()
            setExistDrawnOfNodes(self.nodesToHide, False)
            self.nodesToHide = set()
            self.startMoveNodeAnimation()
        elif self.nodesToMove and self.toMove:
            for n in self.nodesToMove:
                n.setAbsolutePos(n.endPos[0], n.endPos[1])
            self.animationMoveGroup.stop()
            self.nodesToMove = set()
            self.startShowNodeAnimation()
        elif self.nodesToShow:
            self.animationShowGroup.stop()
            self.nodesToShow = set()
        if not self.nodesToHide and not self.nodesToMove and not self.nodesToShow:
            self.viz.busy = False
            self._status_update_timer.stop()
                