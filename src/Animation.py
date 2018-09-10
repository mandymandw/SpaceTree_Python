'''
Created on Sep 3, 2018

@author: manw
'''
from PyQt5.QtCore import QPropertyAnimation

class Animation(QPropertyAnimation):
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
        self.duration = 700
        self.fps = 25
#         self.transition = Quart.easeInOut
        self.clearCanvas = True
        self.type = 'nothing'
        self.aniamting = False
        
    def setOptions(self, controller, compute, onComplete=None):
        self.anim = QPropertyAnimation(self.frame, b"geometry")
#         self.anim.setDuration(10000)
#         self.anim.setStartValue(QRect(150, 30, 100, 100))
#         self.anim.setEndValue(QRect(150, 30, 200, 200))
#         self.anim.start()
        
    def start(self):
        self.start()

    def end(self):
        self.stop()
        