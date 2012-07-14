from random import Random
from core import Target
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem, QGraphicsRectItem
from PyQt4.QtCore import QObject, QPointF as Point, pyqtSignal, pyqtSlot, pyqtProperty

class History(list):
    """ Represent a sequence of items """
    def __init__(self, *initial_items): super().__init__(initial_items)

    @property
    def last(self): return self.recent(0)

    def recent(self, index):
        # indexer for the reversed list, just
        if index>=len(self): raise Exception
        return self[len(self)-1-index]
    
class GraphicItem:
    """ All graphic items must inherit these properties """    
    position = pyqtProperty(Point, QGraphicsItem.pos, QGraphicsItem.setPos)
    parent=pyqtProperty(QGraphicsItem, QGraphicsItem.parentItem)
    
    def findScene(self):
        parent=self
        while not parent.scene():
            parent=parent.parentItem()
        return parent.scene()
    
class LineItem(QGraphicsLineItem):
    pen = pyqtProperty(QtGui.QPen, QGraphicsLineItem.pen, QGraphicsLineItem.setPen)
    
    def __init__(self, start=Point(), end=Point(), parent=None):
        super().__init__(parent)
        self._start=start
        self._end=end
        self._update()
    
    @pyqtProperty(Point)
    def start(self):
        return self._start
    @start.setter
    def start(self, value):
        self._start=value
        self._update()
    
    @pyqtProperty(Point)
    def end(self):
        return self._end
    @end.setter
    def end(self, value):
        self._end = value
        self._update()
    
    def _update(self):
        self.setLine(self.start.x(),self.start.y(), self.end.x(), self.end.y())

class TargetLabel(QGraphicsRectItem, GraphicItem):
    position = pyqtProperty(Point, QGraphicsItem.pos, QGraphicsItem.setPos)
    
    def __init__(self, parent=None):
        super().__init__(10,10,60,40, parent)
        
    def update_location(self):
        pass
        
class TargetView(QGraphicsItem):
    def __init__(self, target, tail_length = 3):
        # super params (x, y, width, height)
        QGraphicsItem.__init__(self)
        
        self.history = History() # used to store the previous points where the target has been
        self.tail_length = tail_length
        self.target = target
        
        # when the target's location is updated update the TargetView position
        target.location_changed.connect(self.update_location)
        
        self.plane = QGraphicsEllipseItem(-2, -2, 4, 4, self)
        self.speed_vector=LineItem(parent = self.plane)
        self.label=TargetLabel(parent = self.plane)
        self.history_marks = [QGraphicsEllipseItem(-1, -1, 2, 2, self) for i in range(tail_length)]
        
        self.update_location() # set target's position based on the target position
    
    @pyqtSlot()
    def update_location(self):
        new_position=self.target.position
        # todo convert coordinate systems
        self.history.append(self.plane.pos())
        
        # todo fix end of th speed vector
        vector=new_position - self.history.last
        self.speed_vector.end = vector
        
        for i in range(min(len(self.history), self.tail_length)):
            self.history_marks[i].setPos(self.history.recent(i))
        
        self.plane.setPos(new_position)
        self.label.update_location()
    
    def boundingRect(self): return QtCore.QRectF()
    
    def paint(self, painter, option, widget=None): pass
    
class RadarView(QtGui.QGraphicsScene):
    def __init__(self):
        super().__init__(-300,-300,600,600)
        
        rand=Random()
        self.targets=[Target() for i in range(5)]
        for target in self.targets:
            self.addItem(TargetView(target, tail_length=5))
        
        self.timer=QtCore.QTimer()
        def update():
            for target in self.targets:
                # target.x+=10
                x = target.x + rand.uniform(-20, 20)
                y = target.y + rand.uniform(-20, 20)
                target.position = Point(x, y)
        
        self.timer.timeout.connect(update)
        self.timer.start(1000/6)
        
    @pyqtSlot()
    def advance(self):
        super().advance()
        
        # rearrange labels in the scene, note that all label positions should be updated
