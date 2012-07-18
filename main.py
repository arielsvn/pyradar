
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
timer.start(1000/24)

# create a QGraphicsView to display the scene
view=QtGui.QGraphicsView(scene)

view.setRenderHint(QtGui.QPainter.Antialiasing)

view.setWindowTitle('JM Radar')
view.resize(400,300)
view.show()

sys.exit(app.exec_())
