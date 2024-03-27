# This file is distributed under the terms of the GNU General Public License v3.0

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QMainWindow
import matplotlib as plt


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

        px = 1/plt.rcParams['figure.dpi']
        self.previous_xlim = None
        self.previous_ylim = None
        self.parent = parent
        self.original_xlim = (0,width/px)
        self.original_ylim = (0,height/px)

        self.mpl_connect('draw_event', self.on_draw)

    def on_draw(self, event):
        current_xlim = self.axes.get_xlim()
        current_ylim = self.axes.get_ylim()
        if (current_xlim != self.previous_xlim) or (current_ylim != self.previous_ylim):
            all_canvases = self.parent.findChildren(MplCanvas)
            for canvas in all_canvases:
                if canvas != self:
                    canvas.axes.set_xlim(current_xlim)
                    canvas.axes.set_ylim(current_ylim)
                    canvas.draw_idle()
                canvas.previous_xlim = current_xlim
                canvas.previous_ylim = current_ylim
    