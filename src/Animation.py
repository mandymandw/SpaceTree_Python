'''
Created on Sep 3, 2018

@author: manw
'''
from PyQt5.QtCore import QPropertyAnimation, QParallelAnimationGroup, QPointF, QAbstractAnimation,\
                        QTimer, QSequentialAnimationGroup
from PyQt5.Qt import QEasingCurve

def setExistDrawnOfNodes(nodes, flag):
    for n in nodes:
        n.drawn = n.exist = flag
        n.setVisible(flag)
        
class Animation(object):
    '''
    *Animations*
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
        self.nodesToHideDuringMove = set()
        self.group = QSequentialAnimationGroup()
        self.animationHideGroup = QParallelAnimationGroup()
        self.animationMoveGroup = QParallelAnimationGroup()
        self.animationShowGroup = QParallelAnimationGroup()
        self._status_update_timer = QTimer()
        self._status_update_timer.setSingleShot(False)
        self._status_update_timer.timeout.connect(self.scene.update)
        self.animationHideGroup.finished.connect(self.endHideAnimation)
        self.animationMoveGroup.finished.connect(self.endMoveAnimation)
        self.animationShowGroup.finished.connect(self.endShowAnimation)
        self.isExpand = None
        
    def setAnimatePosOptions(self, item, start, end, group):
        anim = QPropertyAnimation(item, 'pos')
        anim.setDuration(2000)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(self.curve)
        group.addAnimation(anim)
    
    def setAnimateOpaticyOptions(self, item, start, end, group):
        anim = QPropertyAnimation(item, 'opacity')
        anim.setDuration(2000)
        anim.setStartValue(start)
        anim.setEndValue(end)
        group.addAnimation(anim)
        
    def computeNodeCategory(self):
        self.nodesToShow = self.viz.nodesDraw2-self.viz.nodesDraw1
        self.nodesToHide = self.viz.nodesDraw1-self.viz.nodesDraw2
        self.nodesToMove = self.viz.nodesDraw2&self.viz.nodesDraw1
        print 'show', ','.join(n.label for n in self.nodesToShow)
        print 'hide',','.join(n.label for n in self.nodesToHide)
        print 'move',','.join(n.label for n in self.nodesToMove)
        setExistDrawnOfNodes(self.nodesToHide, True)
        setExistDrawnOfNodes(self.nodesToShow, False)
        self.toMove = False
        for n in self.nodesToMove:
            if n.startPos==n.endPos: continue
            self.toMove = True
#             print 'nodesToMove', n.path, n.startPos, n.xy, n.endPos
            n.setAbsolutePos(n.startPos[0], n.startPos[1])
        for n in self.nodesToHide:
#             print 'nodesToMove', n.path, n.startPos, n.xy, n.endPos
            n.setAbsolutePos(n.startPos[0], n.startPos[1])
    
    def start(self, isExpandNode):
        self.isExpand = isExpandNode
        '''We do 1.hide, 2.move, then 3. show'''
        self.computeNodeCategory()
        self.startHideNodeAnimation()
        self.startMoveNodeAnimation()
        self.startShowNodeAnimation()
        self._status_update_timer.start(20)
        if self.nodesToHide:
            self.animationHideGroup.start()
        elif self.nodesToMove:
            self.animationMoveGroup.start()
        elif self.nodesToShow:
            self.animationShowGroup.start()
        
    def startHideNodeAnimation(self):
        for n in self.nodesToHide:
            if self.isExpand:
                if self.viz.root.parent and n == self.viz.root.parent: continue
                if n.parent:
                    self.setAnimateOpaticyOptions(n, 1, 0, self.animationHideGroup)
                    self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(n.parent.startPos[0], n.parent.startPos[1]), self.animationHideGroup)
                else:
                    self.nodesToHideDuringMove.add(n)
            else:
                self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(self.viz.clickedNode.startPos[0], self.viz.clickedNode.startPos[1]), self.animationHideGroup)
        
    def startMoveNodeAnimation(self):
        if not self.toMove: return
        for n in self.nodesToMove:
            if self.viz.root.parent and n == self.viz.root.parent: continue
            self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(n.endPos[0], n.endPos[1]), self.animationMoveGroup)
        for n in self.nodesToHideDuringMove:
            self.setAnimateOpaticyOptions(n, 1, 0, self.animationMoveGroup)
        
    def startShowNodeAnimation(self):
        for n in self.nodesToShow:
            self.setAnimateOpaticyOptions(n, 0, 1, self.animationShowGroup)
            if n == self.viz.root: continue
            if n.parent: 
                parentPos = n.parent.endPos
                self.setAnimatePosOptions(n, QPointF(parentPos[0], parentPos[1]), QPointF(n.endPos[0], n.endPos[1]), self.animationShowGroup)
            
    def endHideAnimation(self):
        for n in self.nodesToHide:
            if n.parent:
                n.setAbsolutePos(n.parent.startPos[0], n.parent.startPos[1])
            else:
                n.setAbsolutePos(n.endPos[0], n.endPos[1])
        setExistDrawnOfNodes(self.nodesToHide, False)
        self._status_update_timer.stop()
        self.animationHideGroup.stop()
        self.animationHideGroup.clear()
        self.nodesToHide = set()
        self.viz.busy = False
        print 'out of hide animation======='
        if self.nodesToMove and self.toMove:
            self.viz.busy = True
            self._status_update_timer.start(20)
            self.animationMoveGroup.start()
        elif self.nodesToShow:
            self.viz.busy = True
            self._status_update_timer.start(20)
            self.animationShowGroup.start()
        self.scene.update()
        
    def endMoveAnimation(self):
        if self.nodesToMove and self.toMove:
            print 'out of move animation======='
            for n in self.nodesToMove:
                n.setAbsolutePos(n.endPos[0], n.endPos[1])
            self.nodesToMove = set()
            self.nodesToHideDuringMove = set()
            self.animationMoveGroup.stop()
            self.animationMoveGroup.clear()
            self._status_update_timer.stop()
            self.viz.busy = False
        if self.nodesToShow:
            self.viz.busy = True
            setExistDrawnOfNodes(self.nodesToShow, True)
            self._status_update_timer.start(20)
            self.animationShowGroup.start()
        self.scene.update()
        
    def endShowAnimation(self):
        for n in self.nodesToShow:
            n.setAbsolutePos(n.endPos[0], n.endPos[1])
        self._status_update_timer.stop()
        self.animationShowGroup.stop()
        self.animationShowGroup.clear()
        self.nodesToShow = set()
        self.scene.scaleObjectGraph()
        self.scene.update()
        self.viz.busy = False
        print 'out of show animation======='
                