import sys
import random
import pprint

from PyQt5.Qt import Qt, QColor
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem, QWidget, QGraphicsEllipseItem


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
        if not root:
            return

        self.colors = [
            QColor(255, 0, 0),
            QColor(255, 63, 0),
            QColor(255, 127, 0),
            QColor(190, 190, 0),
            QColor(127, 255, 0),
            QColor(63, 255, 0),
            QColor(0, 255, 0),
            QColor(0, 255, 63),
            QColor(0, 255, 127),
            QColor(0, 190, 190),
            QColor(0, 127, 255),
            QColor(0, 63, 255),
            QColor(0, 0, 255),
            QColor(63, 0, 255),
            QColor(127, 0, 255),
            QColor(190, 0, 190),
            QColor(255, 0, 127),
            QColor(255, 0, 63),
        ]

        self.objects = [[]]

        self.__y_used = []

        for n, branch in enumerate(tree_data):
            if branch[0] == [-1, -1]:
                continue
            clr = self.colors[n % len(self.colors)]
            self.pen.setColor(clr)
            self.brush.setColor(clr)
            self.objects.append([])
            self.objects[n] += self.addNode(branch[0][1], n, branch[0][0])
            self.objects[n][-1].setData(0, [n, 0, branch[0]])
            self.objects[n][-1].setZValue(100)
            for i, item in enumerate(branch[2:]):
                self.objects[n] += self.addNode(branch[0][1] + i + 1, n)
                self.objects[n][-1].setData(0, [n, i+1, branch[0]])
                self.objects[n][-1].setZValue(100)

        self.pen.setColor(self.colors[0])
        self.brush.setColor(self.colors[0])
        for n, obj in enumerate(root[1:]):
            self.objects[0] += self.addNode(n, 0)
            self.objects[0][-1].setData(0, [0, n])
            self.objects[0][-1].setZValue(100)
        # self.objects[0][0].setData(0, [0, 0])

        self.selected = None

        self.scene.selectionChanged.connect(self.handleSelection)

    def handleSelection(self):
        ss = self.scene.selectedItems()

        def __clear_selection():
            if not self.selected:
                return
            for obj in reversed(self.selected):
                if obj.data(0):
                    self.pen.setColor(self.colors[obj.data(0)[0]])
                    self.brush.setColor(self.colors[obj.data(0)[0]])
                if hasattr(obj, "setBrush"):
                    obj.setBrush(self.brush)
                obj.setPen(self.pen)
                obj.update()

        if len(ss) == 0:
            __clear_selection()
            self.selected = None
            return
        __clear_selection()

        pprint.pprint(self.objects)

        self.selected = self.objects[ss[-1].data(0)[0]]

        def __clear_up_to(objects, wants):
            to_include = 0
            for i in objects:
                if not i.data(0):
                    to_include += 1
                    continue
                if i.data(0)[1] != wants:
                    to_include += 1
                    continue
                to_include += 1
                break
            return objects[:to_include]

        branch = __clear_up_to(self.selected, ss[-1].data(0)[1]).copy()
        while True:
            if isinstance(branch[1], QGraphicsEllipseItem):
                # we are at the root, stop traversing
                break
            if isinstance(branch[2], QGraphicsEllipseItem):
                branch = __clear_up_to(self.objects[branch[2].data(0)[2][0]], branch[2].data(0)[2][1] - 1) + branch
                continue
            pprint.pprint(branch)
            raise ValueError("could not find the root??? wtf??")

        self.selected = branch
        self.pen.setColor(QColor(255, 255, 255))
        self.brush.setColor(self.pen.color())
        curcol = self.pen.color()
        progression = 0
        lerp = lambda a, b, t: (1 - t) * a + t * b
        for obj in reversed(self.selected):
            if obj.data(0):
                curcol = self.colors[obj.data(0)[0]]
            obj.setPen(self.pen)
            if hasattr(obj, "setBrush"):
                obj.setBrush(self.brush)
                progression += 1
            obj.update()
            newcol = self.pen.color()
            newcol = QColor.fromHsv(
                int(lerp(newcol.hsvHue(), curcol.hsvHue(),
                         min(1, max(0, progression / (len(self.selected)+5))))),
                int(lerp(newcol.hsvSaturation(), curcol.hsvSaturation(),
                         min(1, max(0, progression / (len(self.selected)+5))))),
                int(lerp(newcol.value(), curcol.value(),
                         min(1, max(0, progression / (len(self.selected)+5)))))
            )
            self.pen.setColor(newcol)
            self.brush.setColor(self.pen.color())

    def addNode(self, x, y, links_from=None):
        scale = 2
        off = 30 * scale
        x, y = y * off, x * off
        w, h = 7 * scale, 7 * scale
        objects = []
        if links_from is not None:
            itrs = 0
            while y in self.__y_used:
                itrs += 1
                y += self.pen.width()
            self.__y_used.append(y)
            off -= self.pen.width() * itrs
            objects += [self.scene.addLine(links_from * off, y, x, y, self.pen)]
            # y -= 3*itrs
        objects += [self.scene.addLine(x, y, x, y + off, self.pen)]
        objects += [self.scene.addEllipse(x - w / 2, y - h / 2 + off, w, h, self.pen, self.brush)]
        objects[-1].setFlag(QGraphicsItem.ItemIsSelectable)
        return objects


if __name__ == "__main__":
    app = QApplication(sys.argv)

    l = 10

    tree_data = [
        [
            [-1, -1],
            'goog://home',
            'https://www.google.com/'
        ],
        [
            [0, 1],
            'https://stackoverflow.com/'
        ],
        [
            [0, 1],
            'https://www.wikipedia.org/'
        ]
    ]

    drawer = TreeViewer(tree_data)
    drawer.show()

    sys.exit(app.exec_())
