'''
Created on Aug 21, 2018

@author: manw
'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView
from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtGui import QPainter
from DiagramScene import DiagramScene

class MainWindow(QMainWindow):
    def __init__(self, scene=None):
        QMainWindow.__init__(self)
        self.scene = scene
        
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        if self.scene:
            self.scene.canvasW, self.scene.canvasH = \
                self.scene.sceneRect().width()-2*self.scene.margin_horizontal,\
                             self.scene.sceneRect().height()-2*self.scene.margin_vertical
        
def main():
    app = QApplication(sys.argv)
    mainw = MainWindow()
    mainw.resize(697, 574)
    scene = DiagramScene(mainw)
    mainw.scene = scene
    view = QGraphicsView(scene)
    view.setGeometry(QRect(0,0,697,574))
    view.setRenderHints(QPainter.Antialiasing)
    mainw.setCentralWidget(view)
    scene.setSceneRect(QRectF(view.geometry()))
    mainw.show()
    scene.createGraph()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    