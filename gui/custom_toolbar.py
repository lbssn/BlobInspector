# This file is distributed under the terms of the GNU General Public License v3.0

from PySide6.QtWidgets import QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as plt
import os

class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, coordinates=True):
        super().__init__(canvas, parent, coordinates)
        self.canvas = canvas
        self.canvas.custom_home_function = self.custom_home_function
        self.parent = parent
        
    def home(self, *args, **kwargs):
        self.custom_home_function()

    def custom_home_function(self):
        self.canvas.axes.set_xlim(self.canvas.original_xlim[0]-0.5,self.canvas.original_xlim[1]-0.5)
        self.canvas.axes.set_ylim(self.canvas.original_ylim[0]-0.5,self.canvas.original_ylim[1]-0.5)
        self.canvas.draw_idle()

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = sorted(filetypes.items())
        default_filetype = self.canvas.get_default_filetype()

        startpath = os.path.expanduser(plt.rcParams['savefig.directory'])
        start = os.path.join(startpath, self.canvas.get_default_filename())
        filters = []
        selectedFilter = None
        for name, exts in sorted_filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = f'{name} ({exts_list})'
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)
        filters = ';;'.join(filters)

        fname, filter = QFileDialog.getSaveFileName(
            self.parent, "Choose a filename to save to", start,
            filters, selectedFilter)
        if fname:
            if startpath != "":
                plt.rcParams['savefig.directory'] = os.path.dirname(fname)
            try:
                self.canvas.figure.savefig(fname)
            except Exception as e:
                QMessageBox.critical(
                    self.parent, "Error saving file", str(e),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.NoButton)
    
