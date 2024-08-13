
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem, QWidget
from PyQt5.QtGui import QPen, QBrush
from PyQt5.Qt import Qt, QColor
import random

class TreeViewer(QWidget):
    def __init__(self, tree):
        super().__init__()
        self.tree = tree

        self.w, self.h = 1000, 500
        self.__y_used = []

        self.resize(self.w, self.h)
        self.scene = QGraphicsScene(self)

        self.pen = QPen()
        self.pen.setWidth(2)
        self.brush = QBrush(Qt.SolidPattern)

        self.view = QGraphicsView(self.scene, self)

        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        self.view.move(0, 0)
        self.view.resize(self.w, self.h)

        root = None
        for branch in tree_data:
            if branch[0] == [-1, -1]:
                root = branch
                break
        if not root: return

        self.colors = [
            QColor(255,   0,   0),
            QColor(255,  63,   0),
            QColor(255, 127,   0),
            QColor(190, 190,   0),
            QColor(127, 255,   0),
            QColor( 63, 255,   0),
            QColor(  0, 255,   0),
            QColor(  0, 255,  63),
            QColor(  0, 255, 127),
            QColor(  0, 190, 190),
            QColor(  0, 127, 255),
            QColor(  0,  63, 255),
            QColor(  0,   0, 255),
            QColor( 63,   0, 255),
            QColor(127,   0, 255),
            QColor(190,   0, 190),
            QColor(255,   0, 127),
            QColor(255,   0,  63),
        ]

        self.objects = [[]]

        for n, branch in enumerate(tree_data):
            if branch[0] == [-1, -1]:
                continue
            clr = self.colors[(n+1)%len(self.colors)]
            self.pen.setColor(clr)
            self.brush.setColor(clr)
            self.objects.append([])
            self.objects[-1] += self.addNode(branch[0][1], n, branch[0][0], draw_line=True, draw_ellipse=False)
            for i, item in enumerate(branch[2:]):
                self.objects[-1] += self.addNode(branch[0][1]+i+1, n, draw_line=True, draw_ellipse=False)

        self.__y_used = []

        for n, branch in enumerate(tree_data):
            if branch[0] == [-1, -1]:
                continue
            clr = self.colors[(n+1)%len(self.colors)]
            self.pen.setColor(clr)
            self.brush.setColor(clr)
            self.objects[n] += self.addNode(branch[0][1], n, branch[0][0], draw_line=False, draw_ellipse=True)
            self.objects[n][-1].setData(0, [n, 0])
            for i, item in enumerate(branch[2:]):
                self.objects[n] += self.addNode(branch[0][1]+i+1, n, draw_line=False, draw_ellipse=True)
                self.objects[n][-1].setData(0, [n, i])

        self.pen.setColor(self.colors[0])
        self.brush.setColor(self.colors[0])
        for n, obj in enumerate(root[1:]):
            self.objects[0] += self.addNode(n, 0, draw_line=True, draw_ellipse=True)
            self.objects[0][-1].setData(0, [0, n])

        self.selected = None

        self.scene.selectionChanged.connect(self.handleSelection)

    def handleSelection(self):
        ss = self.scene.selectedItems()
        if (len(ss) == 0):
            if self.selected:
                self.pen.setColor(self.colors[self.selected[-1].data(0)[0]-1])
                self.brush.setColor(self.colors[self.selected[-1].data(0)[0]-1])
                for obj in self.selected:
                    obj.setPen(self.pen)
                    if hasattr(obj, "setBrush"):
                        obj.setBrush(self.brush)
                    obj.update()
            self.selected = None
        else:
            if self.selected:
                self.pen.setColor(self.colors[self.selected[-1].data(0)[0]-1])
                self.brush.setColor(self.colors[self.selected[-1].data(0)[0]-1])
                for obj in self.selected:
                    obj.setPen(self.pen)
                    if hasattr(obj, "setBrush"):
                        obj.setBrush(self.brush)
                    obj.update()
            self.selected = self.objects[ss[-1].data(0)[0]]
            to_include = 0
            for i in self.selected:
                if not i.data(0):
                    to_include += 1
                    continue
                if i.data(0)[1] != ss[-1].data(0)[1]:
                    to_include += 1
                    continue
                to_include += 1
                break
            self.selected = self.selected[:to_include]
            self.pen.setColor(QColor(255, 255, 255))
            self.brush.setColor(QColor(255, 255, 255))
            for obj in self.selected:
                obj.setPen(self.pen)
                if hasattr(obj, "setBrush"):
                    obj.setBrush(self.brush)
                obj.update()

    def addNode(self, x, y, links_from=None, draw_line=True, draw_ellipse=False):
        scale = 2
        off = 30 * scale
        x, y = y * off, x * off
        w, h = 7 * scale, 7 * scale
        objects = []
        if links_from != None and draw_line:
            itrs = 0
            while y in self.__y_used:
                itrs += 1
                y += self.pen.width()
            self.__y_used.append(y)
            off -= self.pen.width()*itrs
            objects += [self.scene.addLine(links_from*off, y, x, y, self.pen)]
            #y -= 3*itrs
        if draw_line: objects += [self.scene.addLine(x, y, x, y+off, self.pen)]
        if draw_ellipse:
            objects += [self.scene.addEllipse(x-w/2, y-h/2+off, w, h, self.pen, self.brush)]
            objects[-1].setFlag(QGraphicsItem.ItemIsSelectable)
        return objects

if __name__ == "__main__":
    app = QApplication(sys.argv)

    tree_data = [
        [[-1, -1], "a", "b"],
        *[[[ 0,  1], "h"]] * 5
    ]

    drawer = TreeViewer(tree_data)
    drawer.show()

    sys.exit(app.exec_())
