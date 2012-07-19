
import sys
from view import RadarView
from PyQt4 import QtCore, QtGui
from core import Radar, NetworkSimulator

app=QtGui.QApplication(sys.argv)

network=NetworkSimulator()
radar=Radar(network)

# Radar is the scene that we want to display
scene=RadarView(radar)

timer=QtCore.QTimer()
timer.timeout.connect(scene.advance)
timer.start(1000/33)

# create a QGraphicsView to display the scene
view=QtGui.QGraphicsView(scene)

view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
view.setRenderHint(QtGui.QPainter.Antialiasing)
view.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
view.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

view.setWindowTitle('JM Radar')
view.resize(400,300)
view.show()

sys.exit(app.exec_())
