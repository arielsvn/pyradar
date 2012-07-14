
import sys
from view import RadarView
from PyQt4 import QtCore, QtGui

app=QtGui.QApplication(sys.argv)

# Radar is the scene that we want to display
radar=RadarView()
# create a QGraphicsView to display the scene
view=QtGui.QGraphicsView(radar)

view.setRenderHint(QtGui.QPainter.Antialiasing)

view.setWindowTitle('JM Radar')
view.resize(400,300)
view.show()

sys.exit(app.exec_())
