
import sys
from view import RadarView, RadarWidget
from PyQt4 import QtCore, QtGui
from core import Radar, NetworkSimulator

app=QtGui.QApplication(sys.argv)

network=NetworkSimulator(number_of_targets = 10)
radar=Radar(network)

# create a QGraphicsView to display the scene
view=RadarWidget(radar, frames_per_second = 24)

view.setWindowTitle('JM Radar')
view.resize(400,300)
view.show()

sys.exit(app.exec_())
