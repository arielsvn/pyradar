
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem
from PyQt4.QtCore import QObject, QPointF as Point, pyqtSignal, pyqtSlot, pyqtProperty

class Target(QObject):
    location_changed = pyqtSignal()
    dropped = pyqtSignal() # the radar is no longuer following this target
    
    def __init__(self, targetId, position=Point()):
        super().__init__()
        self.targetId = targetId
        self._position=position
    
    @pyqtProperty(float)
    def x(self): return self.position.x()
    @x.setter
    def x(self, value):
        self._position=Point(value, self.y)
        self.location_changed.emit()
    
    @pyqtProperty(float)
    def y(self): return self.position.y()
    @y.setter
    def y(self, value):
        self._position=Point(self.x, value)
        self.location_changed.emit()
    
    @pyqtProperty(Point)
    def position(self): return self._position
    @position.setter
    def position(self, value):
        self._position=value
        self.location_changed.emit()
                
class Message(QObject): pass

class TargetPositionMessage(Message):
    def __init__(self, targetId, coord):
        self.targetId = targetId
        self.coord=coord
    
class Network(QObject):
    message_arrived = pyqtSignal(Message)

class NetworkSimulator(QObject):
    """ generates random target positions messages """
    pass
    
class Radar(QObject):
    target_droped=pyqtSignal(Target) # the radar is no longuer following this target
    target_detected=pyqtSignal(Target) # raised when a new target is found and need is added...
    
    def __init__(self, network, *targets):
        # receives messages from the network ('antena')
        self.network = network
        network.message_arrived.connect(self.message_arrived)
        
        self.targets=list(targets)
    
    @pyqtSlot(Message)
    def message_arrived(self, message):
        if isinstance(message, TargetPositionMessage):
            lst = [target for target in self.targets if target.targetId==message.targetId]
            if lst:
                # the target exist, update it's position
                target = lst[0]
                target.position = message.coord
            else:
                # a new target has been detected, send the proper signals
                target=Target(message.targetId, message.coord)
                self.targets.append(target)
                target_detected.emit(target)
                
        # proccess other types of messages






