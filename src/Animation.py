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
        self.nodesToHideDuringMove = set()
        self.aniamting = False
        self.group = QSequentialAnimationGroup()
        self.animationHideGroup = QParallelAnimationGroup()
        self.animationMoveGroup = QParallelAnimationGroup()
        self.animationShowGroup = QParallelAnimationGroup()
        self._status_update_timer = QTimer()
        self._status_update_timer.setSingleShot(False)
        self._status_update_timer.timeout.connect(self.scene.update)
        self.group.finished.connect(self.endAnimation)
        
    def setAnimatePosOptions(self, item, start, end, group):
        anim = QPropertyAnimation(item, 'pos')
        anim.setDuration(3000)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(self.curve)
        group.addAnimation(anim)
    
    def setAnimateOpaticyOptions(self, item, start, end, group):
        anim = QPropertyAnimation(item, 'opacity')
        anim.setDuration(3000)
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
        self.group.addAnimation(self.animationHideGroup)
        self.group.addAnimation(self.animationMoveGroup)
#         self.group.addAnimation(self.animationShowGroup)
        setExistDrawnOfNodes(self.nodesToHide, True)
        setExistDrawnOfNodes(self.nodesToShow, False)
        for n in self.nodesToMove:
            print 'nodesToMove', n.path, n.startPos, n.xy, n.endPos
            n.setAbsolutePos(n.startPos[0], n.startPos[1])
    
    def start(self):
#         print 'Animating...'
        '''We do 1.hide, 2.move, then 3. show'''
        self.computeNodeCategory()
        if self.nodesToHide:
            self.startHideNodeAnimation()
            
        if self.nodesToMove:
            self.startMoveNodeAnimation()
            
        if self.nodesToShow:
            self.startShowNodeAnimation()
            
        self._status_update_timer.start(20)
        self.group.start()
             
#     def start(self):
# #         print 'Animating...'
#         '''We do 1.hide, 2.move, then 3. show'''
#         self.computeNodeCategory()
# #         self._status_update_timer.start(20)
#         if self.nodesToHide:
#             self.startHideNodeAnimation()
#         elif self.nodesToMove:
#             self.startMoveNodeAnimation()
#         elif self.nodesToShow:
#             self.startShowNodeAnimation()
        
    def startHideNodeAnimation(self):
#             print '=======hide============'
        for n in self.nodesToHide:
            if n.parent:
                self.setAnimateOpaticyOptions(n, 1, 0, self.animationHideGroup)
                self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(n.parent.startPos[0], n.parent.startPos[1]), self.animationHideGroup)
            else:
                self.nodesToHideDuringMove.add(n)
                n.setAbsolutePos(n.startPos[0], n.startPos[1])
#                 n.setVisible(False)
                
    def startMoveNodeAnimation(self):
#             print '=======move============'
        self.toMove = False
        for n in self.nodesToMove:
#                 print n.path, n.startPos, n.endPos
            if n.startPos==n.endPos: continue
            self.toMove = True
            self.setAnimatePosOptions(n, QPointF(n.startPos[0], n.startPos[1]), QPointF(n.endPos[0], n.endPos[1]), self.animationMoveGroup)
        for n in self.nodesToHideDuringMove:
            self.setAnimateOpaticyOptions(n, 1, 0, self.animationMoveGroup)
        
    def startShowNodeAnimation(self):
        for n in self.nodesToShow:
            self.setAnimateOpaticyOptions(n, 0, 1, self.animationShowGroup)
            if n.parent: 
                parentPos = n.parent.endPos
                self.setAnimatePosOptions(n, QPointF(parentPos[0], parentPos[1]), QPointF(n.endPos[0], n.endPos[1]), self.animationShowGroup)
            
    def endAnimation(self):
        for n in self.nodesToMove:
            n.setAbsolutePos(n.endPos[0], n.endPos[1])
        setExistDrawnOfNodes(self.nodesToHide, False)
        setExistDrawnOfNodes(self.nodesToShow, True)
        
        self.viz.busy = False
        self.group.stop()
        self._status_update_timer.stop()
        self.animationHideGroup.clear()
        self.animationMoveGroup.clear()
        
        self.nodesToMove = set()
        self.nodesToHide = set()
        self.nodesToHideDuringMove = set()
#         print 'out of animation======='
        if self.nodesToShow:
            self.animationShowGroup.finished.connect(self.endShowAnimation)
            self._status_update_timer.start(20)
            self.animationShowGroup.start()
        
    def endShowAnimation(self):
        if self.nodesToShow:
            self._status_update_timer.stop()
            self.animationShowGroup.stop()
            self.animationShowGroup.clear()
            self.nodesToShow = set()
#             print 'out of show animation======='
                