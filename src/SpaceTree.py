'''
Created on Aug 21, 2018

@author: manw
'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView
from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtGui import QPainter
from DiagramScene import DiagramScene

def main():
    app = QApplication(sys.argv)
    mainw = QMainWindow()
    mainw.resize(697, 574)
    scene = DiagramScene(mainw)
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
    