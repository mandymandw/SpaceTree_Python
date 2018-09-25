'''
Created on Aug 21, 2018

@author: manw
'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsProxyWidget, QLineEdit
from PyQt5.QtCore import QRect, QRectF, QTimer
from PyQt5.QtGui import QPainter
from DiagramScene import DiagramScene
from PyQt5.Qt import QPushButton

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
        
    def addSearchBox(self):
        self.searchConfirmWidget = QGraphicsProxyWidget()
        self.confirmSearchBtn = QPushButton('OK')
        self.searchConfirmWidget.setWidget(self.confirmSearchBtn)
        self.scene.addItem(self.searchConfirmWidget)
        self.searchConfirmWidget.setPos(self.scene.sceneRect().width()-self.searchConfirmWidget.geometry().width()-10, 10)
        self.confirmSearchBtn.clicked.connect(self.scene.confirmSearch)
    
        self.searchLineEdit = QLineEdit()
        self.searchWidget = QGraphicsProxyWidget()
        self.searchWidget.setWidget(self.searchLineEdit)
        self.scene.addItem(self.searchWidget)
        self.searchWidget.setPos(self.searchConfirmWidget.pos().x()-self.searchLineEdit.geometry().width()-10, \
                                self.searchConfirmWidget.pos().y()-0.5*(self.searchLineEdit.geometry().height()-self.searchConfirmWidget.geometry().height()))
        
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
    directories = scene.processCrawlerResult('/Users/manw/Documents/Projects/OSCrawler/InterviewCrawl.txt')
#         directories = self.processCrawlerResult('/Users/manw/Documents/Projects/OSCrawler/DownloadsCrawl.txt')
    scene.createGraph(directories)
    mainw.addSearchBox()
    sys.exit(app.exec_())

if __name__ == '__main__':
#         directories = ['/', '/tools', '/home', '/classes/os', '/classes/security', '/classes/security/public', '/classes/os/public']
#     directories = ['/', '/tools/t2/mine', '/tools/t1/mine', '/tools/t3/school/mine' ,'/home', '/classes/os', '/classes/security', '/classes/security/public', '/classes/os/public']
#         directories = ['/Users/manw/Documents/interview', 
#              '/Users/manw/Documents/interview/gdbiblio.pdf', 
#              '/Users/manw/Documents/interview/notes',
#              '/Users/manw/Documents/interview/cv_temp', 
#              '/Users/manw/Documents/interview/notes/main.pdf', 
#              '/Users/manw/Documents/interview/cv_temp/cv.pdf']
    main()
    