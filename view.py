from random import Random
import math
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
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        
    @pyqtProperty(float)
    def center(self): return self.rect().center()
        
class TargetView(QGraphicsItem):
    def __init__(self, target, tail_length = 3):
        # super params (x, y, width, height)
        QGraphicsItem.__init__(self)
        
        self.history = History() # used to store the previous points where the target has been
        self.tail_length = tail_length
        self.target = target
        
        self.plane = QGraphicsEllipseItem(-2, -2, 4, 4, self)
        # self.speed_vector = LineItem(parent = self.plane)
        self.label=TargetLabel(parent = self.plane)
        self.box_line = LineItem(parent = self.plane)
        #self.history_marks = [QGraphicsEllipseItem(-1, -1, 2, 2, self) for i in range(tail_length)]
    
    def advance(self, phase):
        super().advance(phase)
#        print('advance phase', phase)
        if phase == 0:
            self._new_label_pos = self.calculate_label_forces()
        else:
            # any coordinate transformation must be here
            self.plane.setPos(self.target.position)
            self.label.setPos(self._new_label_pos)
            self.box_line.end = self.plane.mapFromItem(self.label, self.label.center)
    
            
    def calculate_label_forces(self):
        # calculates the forces applied to the label and returns the new position
        # in the label coordinate system
        
        def length(point): return math.sqrt(point.x()**2 + point.y()**2)
        
        radar = self.scene()
        
        k=math.sqrt(radar.area/len(radar.radar.targets))
        
        def attractive_force(distance): return (distance**3) / k
        def repulsive_force(distance): return k**2 / (distance)
        
        disp = Point()
        def repulse(item, point):
            
        
        # calculate repulsive forces
        for view in radar.target_views():
            if view != self: # for each other targets
            
                other_pos = self.label.mapFromItem(view.label, view.label.center)
                d = self.label.center - other_pos
                distance = length(d)
                disp += (d/distance) * repulsive_force(distance)
        
        # TODO calculate attractive forces, only for the target
        other_pos = self.label.mapFromItem(self.plane, Point(0,0)) # the plane is in (0; 0)
        d = self.label.center - other_pos
        distance = length(d)
        disp -= (d/distance) * attractive_force(distance)

        pos=self.label.pos()
        
        if not (disp.x()<0.1 and disp.y()<0.1):
            pos += (disp / length(disp))
        
        return pos
    
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
    def __init__(self, radar, height=600, width=600):
        super().__init__(- height/2,- width/2, height, width)
        
        self.radar=radar
        for target in radar.targets:
            self.addItem(TargetView(target))
            
        radar.target_detected.connect(self.target_detected)
        
    width = pyqtProperty(float, QtGui.QGraphicsScene.width)
    height = pyqtProperty(float, QtGui.QGraphicsScene.height)
    area = pyqtProperty(float, lambda self: self.width * self.height)
    
    def target_views(self):
        return (view for view in self.items() if isinstance(view, TargetView))
        
    @pyqtSlot(Target)
    def target_detected(self, target):
        view = TargetView(target)
        self.addItem(view)
        
    @pyqtSlot()
    def advance(self):
        super().advance()
        
        # rearrange labels in the scene, note that all label positions should be updated
        if self.radar.targets:
            k=math.sqrt(self.area/len(self.radar.targets))
            
            def attractive_force(distance): distance**2 / k
            def repulsive_force(distance): k**2 / distance
            
            # calculate repulsive forces
            for view in self.target_views():
                view.disp=0
                
                for other in self.target_views():
                    if view != other:
                        #other_pos = view.label.mapFromItem(other.label, other.label.center)
                        #d = view.label.center - other_pos
                        pass
                
                
                
                
                
                
                
                
                
