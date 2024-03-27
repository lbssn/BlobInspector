# This file is distributed under the terms of the GNU General Public License v3.0

from skimage import io
import numpy as np
from PySide6.QtWidgets import QFileDialog, QGroupBox, QDialog, QPushButton, QLabel, QVBoxLayout, QCheckBox, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
import matplotlib.pyplot as plt
from gui.MplCanvas import MplCanvas
from gui.MplCanvasHistogram import MplCanvasHistogram
from gui.app_ui import Ui_MainWindow
from gui.save_analysis_window import SaveAnalysisWindow
from gui.batch_analysis_window import BatchAnalysisWindow
from gui.custom_toolbar import CustomToolbar
from model.app_model import AppModel
from logic.algorithms import *
import random
import re
import csv
from datetime import datetime
from joblib import dump, load


def resize_main_window(window : Ui_MainWindow):
    '''Resizes the images when the main window is resized
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number,focus=window.focus)

def remove_all_images(window : Ui_MainWindow):
    '''Removes all the loaded images
    window : an instance of the app'''
    window.combob_FileName.clear()
    window.appMod = AppModel()
    window.wi_OriginalText.hide()
    window.wi_Image1Text.hide()
    window.wi_Image2Text.hide()
    window.tabWidget.hide()
    window.gb_ResultsChoice.hide()
    window.wi_Image1Canvas.hide()
    window.wi_Image2Canvas.hide()
    window.wi_OriginalImage.hide()
    window.frame_4.hide()

def remove_current_image(window : Ui_MainWindow):
    '''Removes the current image from the comobox
    window : an instance of the app'''
    appMod=window.appMod
    if len(appMod.stacks.keys()) == 1:
        remove_all_images(window)
    else:
        filename = window.combob_FileName.currentText()
        appMod.stack_names.remove(filename)
        del appMod.stacks[filename]
        del appMod.included_images[filename]
        del appMod.corrected_images[filename]
        del appMod.rolling_ball_param[filename]
        del appMod.rolling_ball_background[filename]
        del appMod.threshold_algo[filename]
        del appMod.first_threshold[filename]
        del appMod.second_threshold[filename]
        del appMod.thresholded_images[filename]
        del appMod.blobs_detection_algo[filename]
        del appMod.blobs_radius[filename]
        del appMod.blobs_thresholded_images[filename]
        del appMod.labeling_option[filename]
        del appMod.labeling_sieve_size[filename]
        del appMod.labeling_coordinates[filename]
        del appMod.labeling_labels[filename]
        del appMod.labeling_images_with_labels[filename]
        del appMod.labeling_images_conserved_blobs[filename]
        del appMod.contours_algo[filename]
        del appMod.contours_background[filename]
        del appMod.contours_mask[filename]
        del appMod.contours_centroids[filename]
        del appMod.contours_main_slice[filename]
        del appMod.density_target_layers[filename]
        del appMod.density_map_kernel_size[filename]
        del appMod.density_target_heatmap[filename]
        del appMod.density_map_heatmap[filename]
        del appMod.results_count[filename]
        del appMod.results_density[filename]
        del appMod.results_distance[filename]
        del appMod.stack_infos[filename]
        index = window.combob_FileName.findText(filename)
        window.combob_FileName.removeItem(index)
        display_original_image(window,window.combob_FileName.itemText(0),0)

def show_error_message(message):
    """Displays a QDialog window with a warning message
    Parameters:
    message : the message to display"""
    dialog = QDialog()
    dialog.setWindowTitle("Error")
    dialog.setModal(True)
    label = QLabel(message)
    label.setAlignment(Qt.AlignCenter)    
    button_ok = QPushButton("OK")
    button_ok.clicked.connect(dialog.accept)
    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(button_ok)
    dialog.setLayout(layout)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
    dialog.show()
    dialog.exec()

def empty_layout(layout):
    '''Removes all the items in a layout
    layout: the name of the layout to empty'''
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
        else:
            layout.removeItem(item)

def hide_text_layout_content(window : Ui_MainWindow, frame):
    '''Hides the chosen content of the QWidgets when displaying secondary images
    window : an instance of the app
    frame: the number of the frame to hide'''
    if frame == 1:
        window.lb_TargetStats.hide()
        window.lb_MapStats.hide()
        window.combob_DensityDisplay.hide()
        window.combob_cmap.hide()

    else:
        window.lb_CentroidCoordinates.hide()
        window.lb_X.hide()
        window.le_CentroidX.hide()
        window.lb_Y.hide()
        window.le_CentroidY.hide()
        window.pb_CentroidAuto.hide()
        window.cb_MainSlice.hide()

def show_text_layout_content(window : Ui_MainWindow, frame):
    '''Shows the chosen content of the QWidgets whendisplaying secondary images
    window : an instance of the app
    frame: the number of the frame to show'''
    if frame == 1:
        window.lb_TargetStats.show()
        window.lb_MapStats.show()
        window.combob_DensityDisplay.show()
        window.combob_cmap.show()

    else:
        window.lb_CentroidCoordinates.show()
        window.lb_X.show()
        window.le_CentroidX.show()
        window.lb_Y.show()
        window.le_CentroidY.show()
        window.pb_CentroidAuto.show()
        window.cb_MainSlice.show()

def get_filename_slice_number(window : Ui_MainWindow):
    '''Gets the file name and the slice number of the currently displayed image
    Parameters:
    window : an instance of the app
    Return:
    filename: the absolute path to the name
    slice_number: the index of the slice in the stack'''
    filename = window.combob_FileName.currentText()
    slice_number = int(window.hs_SliceNumber.value())
    return filename, slice_number

def get_histogram(window : Ui_MainWindow, appMod : AppModel,image,title):
    '''Creates an instance of the class MplCanvasHistogram
    Parameters:
    window : an instance of the app
    image: an image whose histogram will be created
    title: a string indicating the title to display on the histogram
    Return:
    canvas_hist: an instance of the class MplCanvasHistogram'''
    canvas_hist = MplCanvasHistogram(window,8,4,100)
    canvas_hist.axes.hist(image.ravel(),bins=256)
    canvas_hist.axes.tick_params(axis='x', labelsize=8)
    canvas_hist.axes.tick_params(axis='y', labelsize=8)
    canvas_hist.axes.set_title(title, fontsize=10)
    return canvas_hist

def draw_histograms(window : Ui_MainWindow):
    '''Places an histogram in the histogram window
    Parameters:
    window : an instance of the app'''
    appMod=window.appMod
    layout = window.histogram_window.layout_Histogram
    empty_layout(layout)
    filename,slice_number = get_filename_slice_number(window)
    image = appMod.stacks[filename][slice_number]
    layout.addWidget(get_histogram(window,appMod,image,"8-bits normalised original histogram"))
    if appMod.corrected_images[filename][slice_number] is not None:
        image = appMod.corrected_images[filename][slice_number]
        layout.addWidget(get_histogram(window,appMod,image,"Corrected 8-bits normalised histogram"))
        window.histogram_window.wi_Histogram.adjustSize()

def display_original_image(window : Ui_MainWindow, filename, slice_number,focus = None):
    ''' Displays the original or the corrected image in the left part of the app
    Parameters:
    window : an instance of the app
    filename : name of the image file
    slice_number : number of the slice in the image file'''
    window.setCursor(QCursor(Qt.WaitCursor))
    appMod=window.appMod
    window.sw_Data.setCurrentIndex(0)
    existingCanvas = window.wi_OriginalImage.findChildren(MplCanvas)
    if len(existingCanvas)>0:
        current_xlim = existingCanvas[0].axes.get_xlim()
        current_ylim = existingCanvas[0].axes.get_ylim()
    if appMod.corrected_images[filename][slice_number] is not None and window.focus != "illumination":
        image = appMod.corrected_images[filename][slice_number]
        title = f"Corrected image width: {image.shape[1]} height: {image.shape[0]}"
    else:
        image = appMod.stacks[filename][slice_number]
        title = f"Original image width: {image.shape[1]} height: {image.shape[0]}"
    px = 1/plt.rcParams['figure.dpi']
    canvas_original = MplCanvas(window,image.shape[1]*px,image.shape[0]*px,100)
    toolbar = CustomToolbar(canvas_original, window)
    toolbar.font_size = 6
    if not window.cb_IncludeImage.isChecked():
        canvas_original.axes.plot([0,image.shape[1]-1],[0,image.shape[0]-1],color='red',linewidth=2)
        canvas_original.axes.plot([image.shape[0]-1,0],[0,image.shape[1]-1],color='red',linewidth=2)
    if focus == "segmentation" and appMod.thresholded_images[filename][slice_number] is not None:
        if appMod.blobs_thresholded_images[filename][slice_number] is not None:
            mask = appMod.blobs_thresholded_images[filename][slice_number]
        else:
            mask = appMod.thresholded_images[filename][slice_number]
        image_rgb = np.empty((image.shape[0], image.shape[1], 3), dtype=np.uint8)
        for i in range (3):
            image_rgb[:,:,i] = image
        coordinates = np.where(mask)
        for y,x in zip(coordinates[0],coordinates[1]):
            image_rgb[y,x] = [255,255,0]
        image = image_rgb
    if focus == "density":
        heatmap = canvas_original.axes.imshow(image, cmap=window.combob_cmap.currentText(), interpolation='nearest')
        cbar = plt.colorbar(heatmap)
        cbar.ax.set_visible(False)
    canvas_original.fig.set_frameon(False)
    canvas_original.fig.subplots_adjust(0, 0, 1, 1, 0, 0)
    canvas_original.axes.set_axis_off()
    canvas_original.fig.suptitle(title)
    canvas_original.fig.tight_layout()
    canvas_original.axes.imshow(image, cmap='gray')
    empty_layout(window.layout_Original)
    window.layout_Original.addWidget(canvas_original)
    window.layout_Original.addWidget(toolbar)
    window.wi_OriginalText.setFixedWidth(int(window.size().width()/3))
    window.wi_OriginalText.show()
    window.wi_OriginalImage.setFixedWidth(int(window.size().width()/3))
    window.wi_OriginalImage.show()
    if len(existingCanvas)>0:
        canvas_original.axes.set_xlim(current_xlim)
        canvas_original.axes.set_ylim(current_ylim)
        canvas_original.draw_idle()
    display_secondary_image(1,window,focus = focus)
    display_secondary_image(2,window,focus = focus)
    if window.cb_IncludeImage.isChecked():
        draw_histograms(window)
    else:
        empty_layout(window.histogram_window.layout_Histogram)
    window.setCursor(QCursor(Qt.ArrowCursor))

def update_image_slider_range(window : Ui_MainWindow, filename):
    """ Update the range of the slider depending on the image file
    Parameters:
    window : an instance of the app
    filename : a string with the name of the file"""
    window.hs_SliceNumber.setValue(0)
    window.hs_SliceNumber.setMinimum(0)
    window.hs_SliceNumber.setMaximum(len(window.appMod.stacks[filename])-1)
    window.lb_SliceNumber.setText(f"{int(window.hs_SliceNumber.value())+1} / {len(window.appMod.stacks[filename])}")

def load_files(window : Ui_MainWindow):
    """ Loads the image files
    Parameters:
    window : an instance of the app"""
    filenames, _ = QFileDialog.getOpenFileNames(window,
        "Choose files",
        "/",
        "Image files (*.*)"
    )
    for filename in filenames:
        stack = io.ImageCollection(filename)
        window.appMod.stacks[filename] = [convert_to_8_bits(frame) for frame in stack]
        length = len(window.appMod.stacks[filename])
        window.appMod.included_images[filename] = [True]*length
        window.appMod.corrected_images[filename] = [None]*length
        window.appMod.rolling_ball_param[filename] = [None]*length
        window.appMod.rolling_ball_background[filename] = [None]*length
        window.appMod.threshold_algo[filename] = [None]*length
        window.appMod.first_threshold[filename] = [None]*length
        window.appMod.second_threshold[filename] = [None]*length
        window.appMod.thresholded_images[filename] = [None]*length
        window.appMod.blobs_detection_algo[filename] = [None]*length
        window.appMod.blobs_radius[filename] = [None]*length
        window.appMod.blobs_thresholded_images[filename] = [None]*length
        window.appMod.labeling_option[filename] = [None]*length
        window.appMod.labeling_sieve_size[filename] = [None]*length
        window.appMod.labeling_coordinates[filename] = [None]*length
        window.appMod.labeling_labels[filename] = [None]*length
        window.appMod.labeling_images_with_labels[filename] = [None]*length
        window.appMod.labeling_images_conserved_blobs[filename] = [None]*length
        window.appMod.contours_algo[filename] = [None]*length
        window.appMod.contours_background[filename] = [None]*length
        window.appMod.contours_mask[filename] = [None]*length
        window.appMod.contours_centroids[filename] = [None]*length
        window.appMod.contours_main_slice[filename] = [False]*length
        window.appMod.density_target_layers[filename] = [None]*length
        window.appMod.density_map_kernel_size[filename] = [None]*length
        window.appMod.density_target_heatmap[filename] = [None]*length
        window.appMod.density_map_heatmap[filename] = [None]*length
        window.appMod.density_taget_centroid_heatmap[filename] = [None]*length
        window.appMod.density_map_centroid_heatmap[filename] = [None]*length
        window.appMod.results_count[filename] = None
        window.appMod.results_density[filename] = None
        window.appMod.results_distance[filename] = None
        window.appMod.stack_infos[filename] = [None, None, None]

    window.appMod.stack_names = list(window.appMod.stacks.keys())
    if window.appMod.stack_names:
        window.combob_FileName.clear()
        window.combob_FileName.addItems(window.appMod.stack_names)
        highlight_groupbox(window,None)
        window.combob_FileName.setCurrentIndex(0)
        if window.appMod.included_images[window.appMod.stack_names[0]][0]:
            window.cb_IncludeImage.setCheckState(Qt.CheckState.Checked)
        else:
            window.cb_IncludeImage.setCheckState(Qt.CheckState.Unchecked)
        set_current_image_options(window,window.appMod.stack_names[0],0)
        display_original_image(window,window.appMod.stack_names[0],0)
        update_image_slider_range(window,window.appMod.stack_names[0])

def close_app(window : Ui_MainWindow):
    '''Closes the main window and all the children windows
    Parameters:
    window : an instance of the app'''
    window.histogram_window.close()
    window.save_analysis_window.close()
    window.batch_analysis_window.close()
    window.close()

def open_batch_analysis_window(window : Ui_MainWindow):
    '''Opens the window to choose the options for a batch analysis
    Parameters:
    window : an instance of the app'''
    window.batch_analysis_window = BatchAnalysisWindow(window)
    window.batch_analysis_window.le_RollingBallRadius.editingFinished.connect(lambda : input_positive_integer(window.batch_analysis_window.le_RollingBallRadius))
    window.batch_analysis_window.le_DensityTargetLayers.editingFinished.connect(lambda : input_positive_integer(window.batch_analysis_window.le_DensityTargetLayers))
    window.batch_analysis_window.le_ZThickness.editingFinished.connect(lambda : input_float(window.batch_analysis_window.le_ZThickness))
    window.batch_analysis_window.le_InterZ.editingFinished.connect(lambda : input_float(window.batch_analysis_window.le_InterZ))
    window.batch_analysis_window.le_PixelSize.editingFinished.connect(lambda : input_float(window.batch_analysis_window.le_PixelSize))
    window.batch_analysis_window.le_SieveSize.editingFinished.connect(lambda : input_integer_over_value(window.batch_analysis_window.le_SieveSize,0,False))
    window.batch_analysis_window.le_BackgroundThreshold.editingFinished.connect(lambda : input_integer_over_value(window.batch_analysis_window.le_BackgroundThreshold,0,False))
    window.batch_analysis_window.le_DensityMapKernelSize.editingFinished.connect(lambda : input_integer_over_value(window.batch_analysis_window.le_DensityMapKernelSize,3,True))
    window.batch_analysis_window.combob_BlobsDetection.addItems(return_blobs_algorithms())
    window.batch_analysis_window.combob_LabelingOption.addItems(return_labeling_algorithms())
    window.batch_analysis_window.combob_Contours.addItems(return_contouring_algorithms())
    window.batch_analysis_window.le_BlobsDetectionMinimumRadius.editingFinished.connect(lambda : input_blobs_radius(window.batch_analysis_window.le_BlobsDetectionMinimumRadius,window.batch_analysis_window.le_BlobsDetectionMaximumRadius,1))
    window.batch_analysis_window.le_BlobsDetectionMaximumRadius.editingFinished.connect(lambda : input_blobs_radius(window.batch_analysis_window.le_BlobsDetectionMaximumRadius,window.batch_analysis_window.le_BlobsDetectionMinimumRadius,1))
    window.batch_analysis_window.le_ThresholdOne.editingFinished.connect(lambda : input_thresholds(window.batch_analysis_window,\
                                                window.batch_analysis_window.le_ThresholdOne,window.batch_analysis_window.le_ThresholdTwo,0,255,"I"))
    window.batch_analysis_window.le_ThresholdTwo.editingFinished.connect(lambda : input_thresholds(window.batch_analysis_window,\
                                                window.batch_analysis_window.le_ThresholdTwo,window.batch_analysis_window.le_ThresholdOne,0,255,"II"))
    window.batch_analysis_window.combob_Threshold.activated.connect(lambda : change_threshold_combobox(window.batch_analysis_window.combob_Threshold,window.batch_analysis_window.le_ThresholdTwo))
    window.batch_analysis_window.pb_StartAnalysis.clicked.connect(lambda : start_batch_analysis(window.batch_analysis_window,window))
    window.batch_analysis_window.show()


def start_batch_analysis(batchWindow : BatchAnalysisWindow, window : Ui_MainWindow):
    '''Processes the batch analysis and saves the results in the /temp directory
    Parameters:
    batchWindow : an instance of the class BatchAnalysisWindow
    window : an instance of the app'''
    filenames = list(window.appMod.stacks.keys())
    if not len(filenames) == 0:
        batchWindow.setCursor(QCursor(Qt.WaitCursor))
        if batchWindow.le_RollingBallRadius.text() != "":
            for filename in filenames:
                index = window.combob_FileName.findText(filename)
                window.combob_FileName.setCurrentIndex(index)
                window.le_RollingBallRadius.setText(batchWindow.le_RollingBallRadius.text())
                rolling_ball_to_stack(window,False)
        if batchWindow.le_ThresholdOne.text() != "I":
            for filename in filenames:
                index = window.combob_FileName.findText(filename)
                window.combob_FileName.setCurrentIndex(index)
                window.combob_Threshold.setCurrentIndex(batchWindow.combob_Threshold.currentIndex())
                window.combob_BlobsDetection.setCurrentIndex(batchWindow.combob_BlobsDetection.currentIndex())
                window.le_ThresholdOne.setText(batchWindow.le_ThresholdOne.text())
                window.le_ThresholdTwo.setEnabled(batchWindow.le_ThresholdTwo.isEnabled())
                window.le_ThresholdTwo.setText(batchWindow.le_ThresholdTwo.text())
                window.le_BlobsDetectionMinimumRadius.setText(batchWindow.le_BlobsDetectionMinimumRadius.text())
                window.le_BlobsDetectionMaximumRadius.setText(batchWindow.le_BlobsDetectionMaximumRadius.text())
                segmentation_to_stack(window,False)
        if batchWindow.le_SieveSize.text() != "":
            for filename in filenames:
                index = window.combob_FileName.findText(filename)
                window.combob_FileName.setCurrentIndex(index)
                window.combob_LabelingOption.setCurrentIndex(batchWindow.combob_LabelingOption.currentIndex())
                window.le_SieveSize.setText(batchWindow.le_SieveSize.text())
                apply_labeling_to_stack(window,False)
                compute_count_results(window,filename,len(window.appMod.stacks[filename]))
        if batchWindow.le_BackgroundThreshold.text() != "":
            infos_applied = False
            for filename in filenames:
                index = window.combob_FileName.findText(filename)
                window.combob_FileName.setCurrentIndex(index)
                window.combob_Contours.setCurrentIndex(batchWindow.combob_Contours.currentIndex())
                window.le_BackgroundThreshold.setText(batchWindow.le_BackgroundThreshold.text())
                apply_contours_to_stack(window,False)
                compute_distance = False
                for i in range(len(window.appMod.labeling_labels[filename])):
                    if window.appMod.labeling_labels[filename][i] is not None:
                        compute_distance = True
                        break
                if compute_distance == True:
                    if infos_applied == False:
                        window.le_ZThickness.setText(batchWindow.le_ZThickness.text())
                        window.le_InterZ.setText(batchWindow.le_InterZ.text())
                        window.le_PixelSize.setText(batchWindow.le_PixelSize.text())
                        apply_infos_to_stacks(window)
                        infos_applied = True
                    compute_distance_results(window,filename,len(window.appMod.stacks[filename]))
        if batchWindow.le_DensityMapKernelSize.text() != "" and batchWindow.le_DensityTargetLayers.text() != "":
            for filename in filenames:
                index = window.combob_FileName.findText(filename)
                window.combob_FileName.setCurrentIndex(index)
                window.le_DensityTargetLayers.setText(batchWindow.le_DensityTargetLayers.text())
                window.le_DensityMapKernelSize.setText(batchWindow.le_DensityMapKernelSize.text())
                apply_density_to_stack(window,False)
                compute_density = False
                for i in range(len(window.appMod.contours_mask[filename])):
                    if window.appMod.contours_mask[filename][i] is not None:
                        compute_density = True
                        break
                if compute_density == True:
                    compute_density_results(window,filename,len(window.appMod.stacks[filename]))
        now = datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M-%S")
        dump(window.appMod,"./temp/"+filename+"_analysis.joblib",compress= True)
        show_save_message("The batch analysis has been successfully performed.\nThe file has been saved in the /temp repertory with a time stamp and will be kept for 7 days.")
        set_current_image_options(window,filenames[0],0)
        display_original_image(window,filenames[0],0,focus=window.focus)
        batchWindow.close()
    else:
        show_error_message("Please choose some images to process.")

def show_version(window : Ui_MainWindow):
    """Displays a QDialog window with information about the software version"""
    dialog = QDialog()
    dialog.setWindowTitle("Version information")
    dialog.setModal(True)
    label = QLabel("Blob inspector v0.9 (March 2024)\n\
                   Blob Inspector was developped by Laurent Busson as a final project for a Master's degree in Bioinformatics at the University of Bordeaux\n\
                   under the supervision of Marie Beurton-Aymar (LaBRI) and Lucie Brisson (BRIC).\n\
                   Blob Inspector is under GNU GPL license.")
    label.setAlignment(Qt.AlignCenter)
    button_ok = QPushButton("OK")
    button_ok.clicked.connect(dialog.accept)
    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(button_ok)
    dialog.setLayout(layout)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
    dialog.show()
    dialog.exec()

def input_positive_integer(widget):
    '''Controls that the input in a widget is a positive integer
    Parameters:
    widget: the widget in which the input is made'''
    if not widget.text().isdigit() or int(widget.text()) <=0:
        if widget.text() != "":
            show_error_message("Please insert a positive integer.")
            widget.clear()

def input_float(widget):
    '''Controls that the input in a widget is a positive float
    Parameters:
    widget: the widget in which the input is made'''
    if not is_float(widget.text()) or float(widget.text())<=0:
        if widget.text() != "":
            show_error_message("Please insert a positive value.")
            widget.clear()

def input_integer_over_value(widget,value,odd):
    '''Controls that the input in a widget is a positive integer equal or greater than a given value
    Parameters:
    widget: the widget in which the input is made
    value: the value to which the input must be at least equal
    odd: if True, the input must be an odd integer'''
    if not widget.text().isdigit() or int(widget.text()) < value:
        if widget.text() != "":
            show_error_message(f"Please insert an integer superior or equal to {value}.")
            widget.clear()
            return False
    else:
        if odd == True and int(widget.text())%2==0:
            show_error_message(f"Please insert an odd integer superior or equal to {value}.")
            widget.clear()
            return False
    return True

def input_blobs_radius(widget1, widget2, value):
    '''Controls the inputs in two widgets
    Parameters:
    widget1: the first widget
    widget2: the second widget
    value: a value above which the inputs must be'''
    if widget1.text() !="min" and widget1.text() !="max":
        if input_integer_over_value(widget1,value,False):
            if widget1.objectName() == "le_BlobsDetectionMinimumRadius":
                if widget2.text() == "max" or int(widget2.text()) < int(widget1.text()):
                    widget2.setText(widget1.text())
            elif widget1.objectName() == "le_BlobsDetectionMaximumRadius":
                if widget2.text() == "min" or int(widget1.text()) < int(widget2.text()):
                    widget2.setText(widget1.text())
        else:
            widget1.editingFinished.disconnect()
            if widget1.objectName() == "le_BlobsDetectionMinimumRadius":
                widget1.setText("min")
            elif widget1.objectName() == "le_BlobsDetectionMaximumRadius":
                widget1.setText("max")
            widget1.clearFocus()
            widget1.editingFinished.connect(lambda : input_blobs_radius(widget1,widget2,value))

def check_value_range(value,min_value,max_value):
    '''Controls that a value is in a given range
    Parameters:
    value: the value to control
    min_value: the minimum range value (included)
    max_value: the maximum range value (included)'''
    if is_float(value) and float(value)>=min_value and float(value)<=max_value:
        return True
    return False

def input_thresholds(window : SaveAnalysisWindow, widget1, widget2, min_value, max_value, original_text):
    '''Controls the input values in two widgets
    Parameters:
    window: an instance of the class SaveAnalysisWindow
    widget1: the first widget in which a value is input
    widget2: the second widget in which a value is input
    min_value: the minimum range value (included)
    max_value: the maximum range value (included)
    original_text: a string with the original text of the first widget'''
    if widget1.text() !="I" and widget1.text() !="II":
        if check_value_range(widget1.text(),min_value,max_value):
            if window.combob_Threshold.currentText() == "One threshold":
                if widget1.objectName() == "le_ThresholdOne":
                    if float(widget1.text()) >=1:
                        widget1.setText(str(int(widget1.text())))
                    else:
                        widget1.setText(str(float(widget1.text())))
            else:
                if widget1.objectName() == "le_ThresholdOne":
                    if float(widget1.text()) >=1:
                        widget1.setText(str(int(widget1.text())))
                        if widget2.text() != "II" and float(widget2.text()) < 1:
                            widget2.setText(str(int(widget1.text())))
                    else:
                        widget1.setText(str(float(widget1.text())))
                        if widget2.text() != "II" and float(widget2.text())>=1:
                            widget2.setText(str(float(widget1.text())))
                    if widget2.text() == "II" or float(widget2.text())>float(widget1.text()):
                        if float(widget1.text()) >=1:
                            widget2.setText(str(int(widget1.text())))
                        else:
                            widget2.setText(str(float(widget1.text())))
                else:
                    if float(widget1.text()) >=1:
                        widget1.setText(str(int(widget1.text())))
                        if widget2.text() != "I" and float(widget2.text()) < 1:
                            widget2.setText(str(int(widget1.text())))
                    else:
                        widget1.setText(str(float(widget1.text())))
                        if widget2.text() != "I" and float(widget2.text())>=1:
                            widget2.setText(str(float(widget1.text())))
                    if widget2.text() == "I" or float(widget2.text())<float(widget1.text()):
                        if float(widget1.text()) >=1:
                            widget2.setText(str(int(widget1.text())))
                        else:
                            widget2.setText(str(float(widget1.text()))) 
        else:
            show_error_message(f"Please choose a value between {min_value} and {max_value} included.")
            widget1.setText(original_text)
            widget1.clearFocus()                   

def change_threshold_combobox(combobox, lineedit):
    '''Changes the display of a QLineEdit depending on the text in a QCombobox
    combobox: the QCombobox
    lineedit: the QLineEdit'''
    if combobox.currentText() == "One threshold":
        lineedit.setText("II")
        lineedit.setEnabled(False)
    else:
        lineedit.setEnabled(True)


def slider_value_changed(window : Ui_MainWindow):
    """Triggers the change of image display when the slider value changes
    Parameters:
    window : an instance of the app"""
    filename, slice_number = get_filename_slice_number(window)
    window.lb_SliceNumber.setText(f"{slice_number+1} / {len(window.appMod.stacks[filename])}")
    if window.appMod.included_images[filename][slice_number]:
        window.cb_IncludeImage.setCheckState(Qt.CheckState.Checked)
    else:
        window.cb_IncludeImage.setCheckState(Qt.CheckState.Unchecked)
    set_current_image_options(window,filename,slice_number)
    display_original_image(window,filename,slice_number,focus=window.focus)

def checkbox_state_changed(window : Ui_MainWindow):
    """Updates the checkbox determining if the image will be included in the analysis and updates the image display
    Parameters:
    window : an instance of the app"""
    filename, slice_number = get_filename_slice_number(window)
    if window.cb_IncludeImage.isChecked():
        window.appMod.included_images[filename][slice_number] = True
    else:
        window.appMod.included_images[filename][slice_number] = False
        clear_results(window,filename,slice_number,"rtblcd")
    display_original_image(window,filename,slice_number)

def call_histogram_window(window : Ui_MainWindow):
    if window.combob_FileName.currentText() and window.cb_IncludeImage.isChecked():
            draw_histograms(window)
            window.histogram_window.show()
            window.histogram_window.activateWindow()
    else:
        show_error_message("Please choose an image to show its histogram.")


def combobox_changed(window : Ui_MainWindow):
    """Updates the image display on the first image of the new stack when the image file changes
    Parameters:
    window : an instance of the app"""
    filename = window.combob_FileName.currentText()
    update_image_slider_range(window,filename)
    set_current_image_options(window,filename,0)
    if window.appMod.included_images[filename][0]:
        window.cb_IncludeImage.setCheckState(Qt.CheckState.Checked)
    else:
        window.cb_IncludeImage.setCheckState(Qt.CheckState.Unchecked)
    display_original_image(window,filename,0,focus=window.focus)

def highlight_groupbox(window : Ui_MainWindow, option):
    """Highlight the tools being used
    Parameters:
    window : an instance of the app
    option: a string with the name of the tool to be highlighted"""
    window.focus = option
    for child in window.frame.findChildren(QGroupBox):
        child.setStyleSheet("")
    if window.focus == "illumination":
        window.gb_Illumination.setStyleSheet("background-color:rgb(85,170,255);")
        hide_text_layout_content(window,1)
        hide_text_layout_content(window,2)
    elif window.focus == "segmentation":
        window.gb_Segmentation.setStyleSheet("background-color:rgb(85,170,255);")
        hide_text_layout_content(window,1)
        hide_text_layout_content(window,2)
    elif window.focus == "labeling":
        window.gb_Labeling.setStyleSheet("background-color:rgb(85,170,255);")
        hide_text_layout_content(window,1)
        hide_text_layout_content(window,2)
    elif window.focus == "contours":
        window.gb_Contours.setStyleSheet("background-color:rgb(85,170,255);")
        hide_text_layout_content(window,1)
    elif window.focus == "density":
        window.gb_Density.setStyleSheet("background-color:rgb(85,170,255);")
        hide_text_layout_content(window,2)
    elif window.focus == "results":
        window.gb_Results.setStyleSheet("background-color:rgb(85,170,255);")
        hide_text_layout_content(window,1)
        hide_text_layout_content(window,2)

def set_current_image_options(window : Ui_MainWindow,filename,slice_number):
    """Displays the chosen parameters for the processing of the current image
    Parameters:
    window : an instance of the app
    filename: name of the image file
    slice_number : index of the image in the file"""
    appMod = window.appMod
    if appMod.corrected_images[filename][slice_number] is not None:
        window.le_RollingBallRadius.setText(str(appMod.rolling_ball_param[filename][slice_number]))
    else:
        window.le_RollingBallRadius.clear()
    if appMod.first_threshold[filename][slice_number] is not None:
        window.le_ThresholdOne.setText(str(appMod.first_threshold[filename][slice_number]))
    else:
        window.le_ThresholdOne.blockSignals(True)
        window.le_ThresholdOne.setText("I")
        window.le_ThresholdOne.blockSignals(False)
    if appMod.second_threshold[filename][slice_number] is not None:
        window.le_ThresholdTwo.setText(str(appMod.second_threshold[filename][slice_number]))
    else:
        window.le_ThresholdTwo.blockSignals(True)
        window.le_ThresholdTwo.setText("II")
        window.le_ThresholdTwo.blockSignals(False)
    if appMod.threshold_algo[filename][slice_number] is not None and appMod.threshold_algo[filename][slice_number] == "Two thresholds":
        window.combob_Threshold.setCurrentIndex(1)
        window.le_ThresholdTwo.setDisabled(False)
    else:
        window.combob_Threshold.setCurrentIndex(0)
        window.le_ThresholdTwo.setDisabled(True)
    if appMod.blobs_detection_algo[filename][slice_number] is not None:
        blobs_algo = return_blobs_algorithms()
        index = blobs_algo.index(appMod.blobs_detection_algo[filename][slice_number])
        window.combob_BlobsDetection.setCurrentIndex(index)
        window.le_BlobsDetectionMinimumRadius.setText(str(appMod.blobs_radius[filename][slice_number][0]))
        window.le_BlobsDetectionMaximumRadius.setText(str(appMod.blobs_radius[filename][slice_number][1]))
    else:
        window.combob_BlobsDetection.setCurrentIndex(0)
        window.le_BlobsDetectionMinimumRadius.blockSignals(True)
        window.le_BlobsDetectionMinimumRadius.setText("min")
        window.le_BlobsDetectionMinimumRadius.blockSignals(False)
        window.le_BlobsDetectionMaximumRadius.blockSignals(True)
        window.le_BlobsDetectionMaximumRadius.setText("max")
        window.le_BlobsDetectionMaximumRadius.blockSignals(False)
    if appMod.labeling_sieve_size[filename][slice_number] is not None:
        window.le_SieveSize.setText(str(appMod.labeling_sieve_size[filename][slice_number]))
        window.combob_LabelingOption.setCurrentText(appMod.labeling_option[filename][slice_number])
    else:
        window.le_SieveSize.clear()
    if appMod.contours_background[filename][slice_number] is not None:
        window.le_BackgroundThreshold.setText(str(appMod.contours_background[filename][slice_number]))
        contouring_algo = return_contouring_algorithms()
        contouring_algo_index = contouring_algo.index(appMod.contours_algo[filename][slice_number])
        window.combob_Contours.setCurrentIndex(contouring_algo_index)
    else:
        window.combob_Contours.setCurrentIndex(0)
        window.le_BackgroundThreshold.clear()
    if appMod.density_map_kernel_size[filename][slice_number] is not None:
        window.le_DensityMapKernelSize.setText(str(appMod.density_map_kernel_size[filename][slice_number]))
    else:
        window.le_DensityMapKernelSize.clear()
    if appMod.density_target_layers[filename][slice_number] is not None:
        window.le_DensityTargetLayers.setText(str(appMod.density_target_layers[filename][slice_number]))
    else:
        window.le_DensityTargetLayers.clear()
    if appMod.stack_infos[filename][0] is not None:
        window.le_ZThickness.setText(str(appMod.stack_infos[filename][0]))
    else:
        window.le_ZThickness.clear()
    if appMod.stack_infos[filename][1] is not None:
        window.le_InterZ.setText(str(appMod.stack_infos[filename][1]))
    else:
        window.le_InterZ.clear()
    if appMod.stack_infos[filename][2] is not None:
        window.le_PixelSize.setText(str(appMod.stack_infos[filename][2]))
    else:
        window.le_PixelSize.clear()

def display_secondary_image(frame, window : Ui_MainWindow, image = None, focus = None, title = None):
    """Displays the secondary images resulting from the processing of the original image
    Parameters:
    window : an instance of the app
    image : the image to be displayed
    focus : the tools being used
    title : the title of the image"""
    window.setCursor(QCursor(Qt.WaitCursor))
    appMod=window.appMod
    if (image is None and focus is None) or not window.cb_IncludeImage.isChecked():
        if frame == 1:
            window.wi_Image1Text.setFixedWidth(int(window.size().width()/3))
            window.wi_Image1Text.show()
            hide_text_layout_content(window,1)
            empty_layout(window.layout_Image1)
            window.wi_Image1Canvas.setFixedWidth(int(window.size().width()/3))
            window.wi_Image1Canvas.show()
        else:
            window.wi_Image2Text.setFixedWidth(int(window.size().width()/3))
            window.wi_Image2Text.show()
            hide_text_layout_content(window,2)
            empty_layout(window.layout_Image2)
            window.wi_Image2Canvas.setFixedWidth(int(window.size().width()/3))
            window.wi_Image2Canvas.show()
    elif window.cb_IncludeImage.isChecked() and image is not None:
        existingCanvas = window.wi_OriginalImage.findChildren(MplCanvas)
        if len(existingCanvas)>0:
            current_xlim = existingCanvas[0].axes.get_xlim()
            current_ylim = existingCanvas[0].axes.get_ylim()
        px = 1/plt.rcParams['figure.dpi']
        canvas = MplCanvas(window,image.shape[1]*px,image.shape[0]*px,100)
        toolbar = CustomToolbar(canvas, window)
        toolbar.font_size = 6
        canvas.fig.set_frameon(False)
        canvas.fig.subplots_adjust(0, 0, 1, 1, 0, 0)
        canvas.axes.set_axis_off()
        if focus == "contours" and frame == 2:
            filename,slice_number = get_filename_slice_number(window)
            centroid_y,centroid_x = appMod.contours_centroids[filename][slice_number]
            centroid_y=int(centroid_y)
            centroid_x=int(centroid_x)
            canvas.axes.plot([centroid_x, centroid_x],[int(max(0,centroid_y-15)), int(min(image.shape[0]-1,centroid_y+15))], color='red', linewidth=2)
            canvas.axes.plot([int(max(0,centroid_x-15)), int(min(image.shape[1]-1,centroid_x+15))],[centroid_y, centroid_y],  color='red', linewidth=2)
            window.le_CentroidX.setText(str(centroid_x))
            window.le_CentroidY.setText(str(centroid_y))
            window.cb_MainSlice.stateChanged.disconnect()
            if appMod.contours_main_slice[filename][slice_number] is True:
                window.cb_MainSlice.setChecked(True)
                window.cb_MainSlice.setEnabled(False)
            else:
                window.cb_MainSlice.setChecked(False)
                window.cb_MainSlice.setEnabled(True)
            window.cb_MainSlice.stateChanged.connect(lambda : change_main_slice(window))
            show_text_layout_content(window,2)
        if focus == "density":
            filename,slice_number = get_filename_slice_number(window)
            heatmap = canvas.axes.imshow(image, cmap=window.combob_cmap.currentText(), interpolation='nearest')
            plt.colorbar(heatmap)
            contoured_image = appMod.contours_mask[filename][slice_number]
            if frame == 1:
                min_m,max_m,mean_m,median_m = min_max_mean_median_density(image,contoured_image)
                window.lb_MapStats.setText(f"Heatmap\nmean={mean_m:.1f}/median={median_m:.1f}\nmin={min_m:.1f}/max={max_m:.1f}")
                show_text_layout_content(window,1)
            if frame == 2:
                min_t,max_t,mean_t,median_t = min_max_mean_median_density(image,contoured_image)
                window.lb_TargetStats.setText(f"Target\nmean={mean_t:.1f}/median={median_t:.1f}\nmin={min_t:.1f}/max={max_t:.1f}")
        else:
            canvas.axes.imshow(image, cmap='gray')
        if title:
            canvas.fig.suptitle(title)
        canvas.fig.tight_layout()
        if frame == 1:
            layout = window.layout_Image1
        else:
            layout = window.layout_Image2
        empty_layout(layout)
        layout.addWidget(canvas)
        layout.addWidget(toolbar)
        if frame == 1:
            window.wi_Image1Canvas.setFixedWidth(int(window.size().width()/3))
            window.wi_Image1Canvas.show()
            window.frame_3.show()
            if len(existingCanvas)>0:
                canvas.axes.set_xlim(current_xlim)
                canvas.axes.set_ylim(current_ylim)
                canvas.draw_idle()        
        else:
            window.wi_Image2Canvas.setFixedWidth(int(window.size().width()/3))
            window.wi_Image2Canvas.show()
            window.frame_3.show()
            if len(existingCanvas)>0:
                canvas.axes.set_xlim(current_xlim)
                canvas.axes.set_ylim(current_ylim)
                canvas.draw_idle()  
    elif window.cb_IncludeImage.isChecked() and focus is not None:
        filename, slice_number = get_filename_slice_number(window)
        if focus == "illumination" and appMod.rolling_ball_param[filename][slice_number] is not None:
            if frame == 1:
                display_secondary_image(1,window,  image = appMod.corrected_images[filename][slice_number], focus = "illumination",title="Corrected image")
            if frame == 2:
                display_secondary_image(2,window,  image = appMod.rolling_ball_background[filename][slice_number], focus = "illumination",title="Background")
        elif focus == "segmentation" and appMod.thresholded_images[filename][slice_number] is not None:
            if frame == 1:
                display_secondary_image(1,window, image = appMod.thresholded_images[filename][slice_number], focus = "segmentation",title="Thresholded image")
            if frame == 2:
                if appMod.blobs_thresholded_images[filename][slice_number] is not None:
                    display_secondary_image(2,window, image = appMod.blobs_thresholded_images[filename][slice_number],title="Blobs thresholded image")
                else:
                    display_secondary_image(2,window)
        elif focus == "labeling" and appMod.labeling_images_with_labels[filename][slice_number] is not None:
            if frame == 1:
                image = appMod.labeling_images_conserved_blobs[filename][slice_number]
                if appMod.blobs_thresholded_images[filename][slice_number] is not None:
                    title = "Blobs thresholded image : conserved blobs"
                else:
                    title = "Thresholded image : conserved blobs"
                display_secondary_image(1,window,image,title = title)
            if frame == 2:
                labels = appMod.labeling_labels[filename][slice_number]
                if labels != []:
                    count = np.max(labels) + 1
                    mean, SD = mean_SD_size(labels)
                else:
                    count,mean,SD = 0,0,0
                display_secondary_image(2,window,appMod.labeling_images_with_labels[filename][slice_number],title = f"Count:{count}, mean size:{mean}, SD:{SD}")
        elif focus == "contours" and appMod.contours_mask[filename][slice_number] is not None:
            if frame == 1:
                if appMod.labeling_coordinates[filename][slice_number] is not None:
                    image = dots_to_binary(appMod.stacks[filename][slice_number],appMod.labeling_coordinates[filename][slice_number])
                    title = "Conserved blobs after labeling"
                else: 
                    if appMod.blobs_thresholded_images[filename][slice_number] is not None:
                        image = appMod.blobs_thresholded_images[filename][slice_number]
                        title = "Blobs thresholded image"
                    else:
                        image = appMod.thresholded_images[filename][slice_number]
                        title = "Thresholded image"
                display_secondary_image(1,window,image,title = title)
            if frame == 2:
                display_secondary_image(2,window,appMod.contours_mask[filename][slice_number],focus="contours",title = "Contoured image")
        elif focus == "density" and appMod.density_map_heatmap[filename][slice_number] is not None:
            if window.combob_DensityDisplay.currentText() == "Percentage":
                if frame == 1:
                    display_secondary_image(1,window,appMod.density_map_heatmap[filename][slice_number],focus="density",title="Convoluted density heatmap (percentage)")
                if frame == 2:
                    display_secondary_image(2,window,appMod.density_target_heatmap[filename][slice_number],focus = "density", title = "Target density heatmap (percentage)")
            if window.combob_DensityDisplay.currentText() == "Count":
                if frame == 1:
                    display_secondary_image(1,window,appMod.density_map_centroid_heatmap[filename][slice_number],focus="density",title="Convoluted density heatmap (Count)")
                if frame == 2:
                    display_secondary_image(2,window,appMod.density_taget_centroid_heatmap[filename][slice_number],focus = "density", title = "Target density heatmap (Count)")      
        else:
            if frame == 1:
                window.wi_Image1Text.setFixedWidth(int(window.size().width()/3))
                window.wi_Image1Text.show()
                hide_text_layout_content(window,1)
                empty_layout(window.layout_Image1)
                window.wi_Image1Canvas.setFixedWidth(int(window.size().width()/3))
                window.wi_Image1Canvas.show()
            else:
                window.wi_Image2Text.setFixedWidth(int(window.size().width()/3))
                window.wi_Image2Text.show()
                hide_text_layout_content(window,2)
                empty_layout(window.layout_Image2)
                window.wi_Image2Canvas.setFixedWidth(int(window.size().width()/3))
                window.wi_Image2Canvas.show()
    window.setCursor(QCursor(Qt.ArrowCursor))

def clear_results(window : Ui_MainWindow,filename,slice_number,results):
    """Clears the chosen parameters and results
    Parameters:
    window : an instance of the app
    filename: name of the image file
    slice_number : index of the image in the file
    results : a string composed of the results to clear (r:rolling-ball,t:threshold,b:blobs,l:labeling,c:contours,d:density)"""
    appMod=window.appMod
    if "r" in results:
        appMod.corrected_images[filename][slice_number] = None
        appMod.rolling_ball_background[filename][slice_number] = None
        appMod.rolling_ball_param[filename][slice_number] = None
        appMod.results_count[filename] = None
        appMod.results_density[filename] = None
        appMod.results_distance[filename] = None
    if "t" in results:
        appMod.threshold_algo[filename][slice_number] = None
        appMod.first_threshold[filename][slice_number] = None
        appMod.second_threshold[filename][slice_number] = None
        appMod.thresholded_images[filename][slice_number] = None
        appMod.results_count[filename] = None
        appMod.results_density[filename] = None
        appMod.results_distance[filename] = None
    if "b" in results:
        appMod.blobs_detection_algo[filename][slice_number] = None
        appMod.blobs_radius[filename][slice_number] = None
        appMod.blobs_thresholded_images[filename][slice_number] = None
        appMod.results_count[filename] = None
        appMod.results_density[filename] = None
        appMod.results_distance[filename] = None
    if "l" in results:
        appMod.labeling_option[filename][slice_number] = None
        appMod.labeling_sieve_size[filename][slice_number] = None
        appMod.labeling_coordinates[filename][slice_number] = None
        appMod.labeling_labels[filename][slice_number] = None
        appMod.labeling_images_with_labels [filename][slice_number] = None
        appMod.labeling_images_conserved_blobs[filename][slice_number] = None
        appMod.results_count[filename] = None
        appMod.results_distance[filename] = None
    if "c" in results:
        appMod.contours_algo[filename][slice_number] = None
        appMod.contours_background[filename][slice_number] = None
        appMod.contours_mask[filename][slice_number] = None
        appMod.contours_centroids[filename][slice_number] = None
        appMod.results_density[filename] = None
        appMod.results_distance[filename] = None
        appMod.contours_main_slice[filename][slice_number] = False
    if "d" in results:
        appMod.density_target_layers[filename][slice_number] = None
        appMod.density_map_kernel_size[filename][slice_number] = None
        appMod.density_target_heatmap[filename][slice_number] = None
        appMod.density_map_heatmap[filename][slice_number] = None
        appMod.density_taget_centroid_heatmap[filename][slice_number] = None
        appMod.density_map_centroid_heatmap[filename][slice_number] = None
        appMod.results_density[filename] = None

def input_rolling_ball_radius(window :Ui_MainWindow):
    '''Controls the proper input of the rolling ball radius
    Parameters:
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"illumination")
        if not window.le_RollingBallRadius.text().isdigit() or int(window.le_RollingBallRadius.text()) <=0:     
            if window.le_RollingBallRadius.text() != "":
                show_error_message("Please insert a positive integer as rolling ball radius.")
                window.le_RollingBallRadius.clear()         
    else:
        show_error_message("Please choose an image to process.")
        window.le_RollingBallRadius.clear() 
 
def rolling_ball_to_image(window : Ui_MainWindow,slice_number = None):
    """Applies the rolling ball algorithm to the displayed image
    Parameters:
    window : an instance of the app
    slice_number : the number of the slice in the stack"""
    appMod=window.appMod
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"illumination")
        filename = window.combob_FileName.currentText()
        single_image = False
        if slice_number is None:
            slice_number = int(window.hs_SliceNumber.value())
            single_image = True
        if appMod.included_images[filename][slice_number]:
            if window.le_RollingBallRadius.text() == "":
                    clear_results(window,filename,slice_number,"rtblcd")
                    if single_image == True:
                        set_current_image_options(window,filename,slice_number)
                        display_original_image(window,filename,slice_number)
            elif window.le_RollingBallRadius.text().isdigit() and int(window.le_RollingBallRadius.text()) > 0:
                appMod.labeling_sieve_size[filename][slice_number] =  int(window.le_RollingBallRadius.text())
                raw_image = appMod.stacks[filename][slice_number]
                window.setCursor(QCursor(Qt.WaitCursor))
                background, corrected_image = rolling_ball(raw_image,int(window.le_RollingBallRadius.text()))
                window.setCursor(QCursor(Qt.ArrowCursor))
                appMod.corrected_images[filename][slice_number] = corrected_image
                appMod.rolling_ball_background[filename][slice_number] = background
                appMod.rolling_ball_param[filename][slice_number] = int(window.le_RollingBallRadius.text())
                clear_results(window,filename,slice_number,"tblcd")
                if single_image == True:
                    set_current_image_options(window,filename,slice_number)
                    display_original_image(window,filename,slice_number,focus = "illumination")  
            else:
                show_error_message("Please choose a positive integer")
        else:
            if single_image == True:
                show_error_message("Please choose an image to process.")
    else:
        show_error_message("Please choose an image to process.")
     

def rolling_ball_to_stack(window : Ui_MainWindow,display=True):
    """Applies the rolling ball algorithm to all the checked images in the stack
    Parameters:
    window : an instance of the app
    display: if True, the images will be displayed"""
    if window.combob_FileName.currentText():
        filename, original_slice_number = get_filename_slice_number(window)
        if window.le_RollingBallRadius.text() == "" or (window.le_RollingBallRadius.text().isdigit() and int(window.le_RollingBallRadius.text()) > 0):
            for i in range(len(window.appMod.stacks[filename])):
                if window.appMod.included_images[filename][i]:
                    rolling_ball_to_image(window,i)
            if display == True:
                set_current_image_options(window,filename,original_slice_number)
                display_original_image(window,filename,original_slice_number,focus = "illumination")
        else:
            show_error_message("Please choose a positive integer or 0 as sieve size.")
    else:
        show_error_message("Please choose an image to process.") 
    

def view_illumination(window : Ui_MainWindow):
    """Highlights the tool 'illumination' and updates the image display
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"illumination")
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number,focus="illumination")
        window.le_RollingBallRadius.setFocus()
    else:
        show_error_message("Please choose an image to process.")
      

def input_threshold_one(window : Ui_MainWindow, slice_number=None):
    """Triggers several actions when the first threshold is set
    Parameters:
    window : an instance of the app
    appMod : an instance of the class AppModel containing the app variables
    slice_number : the index of the image in the stack"""
    appMod=window.appMod
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"segmentation")
        filename = window.combob_FileName.currentText()
        single_image = False
        if slice_number is None:
            slice_number = int(window.hs_SliceNumber.value())
            single_image = True
        if window.appMod.included_images[filename][slice_number]:
            if window.le_ThresholdOne.text() != "I":
                try:
                    float_var = float(window.le_ThresholdOne.text())
                    if float_var >=0 and float_var <=255:
                        if appMod.corrected_images[filename][slice_number] is not None:
                                image = appMod.corrected_images[filename][slice_number]
                        else:
                            image = appMod.stacks[filename][slice_number]
                        max_im = np.max(image)
                        if float_var < 1:
                            threshold_one = float_var * max_im
                            appMod.first_threshold[filename][slice_number] = float_var
                        else:
                            float_var = int(float_var)
                            threshold_one = float_var
                            appMod.first_threshold[filename][slice_number] = int(float_var)
                        if window.combob_Threshold.currentText() == "Two thresholds":
                            if window.le_ThresholdTwo.text() == "II" or float(window.le_ThresholdTwo.text()) > float_var:
                                window.le_ThresholdTwo.setText(str(float_var))
                                appMod.second_threshold[filename][slice_number] = float_var
                            if float(window.le_ThresholdTwo.text()) < 1:
                                if float_var >=1:
                                    window.le_ThresholdTwo.setText(str(float_var))
                                    threshold_two = threshold_one
                                    appMod.second_threshold[filename][slice_number] = threshold_two
                                else:
                                    threshold_two = float(window.le_ThresholdTwo.text()) * max_im
                                    appMod.second_threshold[filename][slice_number] = float(window.le_ThresholdTwo.text())
                            else:
                                threshold_two = int(window.le_ThresholdTwo.text())
                                appMod.second_threshold[filename][slice_number] = threshold_two
                            window.setCursor(QCursor(Qt.WaitCursor))
                            mask = segmentation_two_thresholds(image,threshold_one,threshold_two)
                            appMod.threshold_algo[filename][slice_number] = "Two thresholds"
                            appMod.thresholded_images[filename][slice_number] = mask
                            window.setCursor(QCursor(Qt.ArrowCursor))
                        else:
                            mask = image >= threshold_one
                            appMod.threshold_algo[filename][slice_number] = "One threshold"
                            appMod.thresholded_images[filename][slice_number] = mask
                            appMod.second_threshold[filename][slice_number] = None
                        clear_results(window,filename,slice_number,"blcd")
                        if single_image == True:
                            set_current_image_options(window,filename,slice_number)
                            display_original_image(window,filename,slice_number,focus = "segmentation")
                        
                    else:
                        raise ValueError("Please choose a number between 0 and 255 included as first threshold.")
                except ValueError as e:
                    show_error_message(f"Please choose a number between 0 and 255 included as first threshold.\n{e}")
                    window.le_ThresholdOne.blockSignals(True)
                    window.le_ThresholdOne.setText("I")
                    window.le_ThresholdOne.blockSignals(False)
    else:
        show_error_message("Please choose an image to process.")

def input_threshold_two(window : Ui_MainWindow):
    """Triggers several actions when the second threshold is set
     Parameters:
    window : an instance of the app"""
    appMod=window.appMod
    if window.combob_FileName.currentText() and window.cb_IncludeImage.isChecked():
        highlight_groupbox(window,"segmentation")
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number)
        if window.le_ThresholdTwo.text() != "II":
            try:
                float_var = float(window.le_ThresholdTwo.text())
                if float_var >=0 and float_var <=255:
                    filename = window.combob_FileName.currentText()
                    slice_number = int(window.hs_SliceNumber.value())
                    if appMod.corrected_images[filename][slice_number] is not None:
                            image = appMod.corrected_images[filename][slice_number]
                    else:
                        image = appMod.stacks[filename][slice_number]
                    max_im = np.max(image)
                    if window.le_ThresholdOne.text() == "I" or float(window.le_ThresholdOne.text()) < float_var:
                        if float_var >= 1:
                            float_var = int(float_var)
                        window.le_ThresholdOne.setText(str(float_var))
                    if float_var < 1:
                        threshold_two = float_var * max_im
                        appMod.second_threshold[filename][slice_number] = float_var
                        if float(window.le_ThresholdOne.text()) >= 1:
                            window.le_ThresholdOne.setText(str(float_var))
                    else:
                        threshold_two = float_var
                        appMod.second_threshold[filename][slice_number] = int(float_var)
                    if float(window.le_ThresholdOne.text()) < 1:
                        threshold_one = float(window.le_ThresholdTwo.text()) * max_im
                        appMod.first_threshold[filename][slice_number] = float(window.le_ThresholdTwo.text())
                    else:
                        threshold_one = int(window.le_ThresholdOne.text())
                        appMod.first_threshold[filename][slice_number] = threshold_one
                    window.setCursor(QCursor(Qt.WaitCursor))
                    mask = segmentation_two_thresholds(image,threshold_one,threshold_two)
                    window.setCursor(QCursor(Qt.ArrowCursor))
                    appMod.thresholded_images[filename][slice_number] = mask
                    appMod.blobs_detection_algo[filename][slice_number] = None
                    appMod.blobs_radius[filename][slice_number] = None
                    appMod.blobs_thresholded_images[filename][slice_number] = None
                    display_original_image(window,filename,slice_number,focus = "segmentation")
                    window.combob_BlobsDetection.setCurrentIndex(0)
                    window.le_BlobsDetectionMinimumRadius.setText("min")
                    window.le_BlobsDetectionMaximumRadius.setText("max")
                else:
                    raise ValueError("Please choose a number between 0 and 255 included as second threshold.")
            except ValueError as e:
                show_error_message(f"Please choose a number between 0 and 255 included as second threshold.\n{e}")
                window.le_ThresholdTwo.blockSignals(True)
                window.le_ThresholdTwo.setText("II")
                window.le_ThresholdTwo.blockSignals(False) 
    else:
        show_error_message("Please choose an image to process.")
        window.le_ThresholdTwo.blockSignals(True)
        window.le_ThresholdTwo.setText("II")
        window.le_ThresholdTwo.blockSignals(False)

def threshold_option_changed(window : Ui_MainWindow):
    """Triggers several action when the combobox for threshold option is activated
    Parameters:
    window : an instance of the app"""
    highlight_groupbox(window,"segmentation")
    if window.combob_Threshold.currentText() == "One threshold":
        window.le_ThresholdTwo.blockSignals(True)
        window.le_ThresholdTwo.setText("II")
        window.le_ThresholdTwo.blockSignals(False)
        window.le_ThresholdTwo.setDisabled(True)
        if window.le_ThresholdOne.text() != "I":
            input_threshold_one(window)
    else:
        window.le_ThresholdTwo.setDisabled(False)
        if window.le_ThresholdOne.text() != "I" and window.le_ThresholdTwo.text() != "II":
            input_threshold_two(window)

def combobox_blobs_changed(window : Ui_MainWindow):
    """Highlights the box 'segmentation' when the combobox for blobs detection is activated
    Parameters:
    window : an instance of the app"""
    highlight_groupbox(window,"segmentation")
     

def set_blobs_minimum_radius(window : Ui_MainWindow):
    """Triggers several actions when a value for minimum radius of blob detection is set
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText() and window.cb_IncludeImage.isChecked():
        highlight_groupbox(window,"segmentation")
        try:
            if window.le_BlobsDetectionMinimumRadius.text() != "min":
                if not window.le_BlobsDetectionMinimumRadius.text().isdigit() or int(window.le_BlobsDetectionMinimumRadius.text()) <0:
                    raise ValueError("The value must be a positive integer")
                if window.le_BlobsDetectionMaximumRadius.text() != "max" and int(window.le_BlobsDetectionMaximumRadius.text()) < int(window.le_BlobsDetectionMinimumRadius.text()):
                    raise ValueError("Minimum radius value must be less than the maximum radius value.")
        except ValueError as e:
            show_error_message(str(e))
            window.le_BlobsDetectionMinimumRadius.blockSignals(True)
            window.le_BlobsDetectionMinimumRadius.setText("min")
            window.le_BlobsDetectionMinimumRadius.blockSignals(False)
    else:
        show_error_message("Please choose an image to process")
        window.le_BlobsDetectionMinimumRadius.blockSignals(True)
        window.le_BlobsDetectionMinimumRadius.setText("min")
        window.le_BlobsDetectionMinimumRadius.blockSignals(False)

def set_blobs_maximum_radius(window : Ui_MainWindow):
    """Triggers several actions when a value for maximum radius of blob detection is set
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText() and window.cb_IncludeImage.isChecked():
        highlight_groupbox(window,"segmentation")
        try:
            if window.le_BlobsDetectionMaximumRadius.text() != "max":
                if not window.le_BlobsDetectionMaximumRadius.text().isdigit() or int(window.le_BlobsDetectionMaximumRadius.text()) < 0:
                    raise ValueError("The value must be a positive integer")
                if window.le_BlobsDetectionMinimumRadius.text() != "min" and int(window.le_BlobsDetectionMaximumRadius.text()) < int(window.le_BlobsDetectionMinimumRadius.text()):
                    raise ValueError("Maximum radius value must be greater than the minimum radius value.")
        except ValueError as e:
            show_error_message(str(e))
            window.le_BlobsDetectionMaximumRadius.blockSignals(True)
            window.le_BlobsDetectionMaximumRadius.setText("max")
            window.le_BlobsDetectionMaximumRadius.blockSignals(False)
    else:
        show_error_message("Please choose an image to process")
        window.le_BlobsDetectionMaximumRadius.blockSignals(True)
        window.le_BlobsDetectionMaximumRadius.setText("max")
        window.le_BlobsDetectionMaximumRadius.blockSignals(False)


def segmentation_to_image(window : Ui_MainWindow, slice_number=None):
    """Applies the segmentation with the chosen options to an image
    Parameters:
    window: an instance of the app
    slice_number: the index of the image in the stack"""
    appMod=window.appMod
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"segmentation")
        filename = window.combob_FileName.currentText()
        single_image = False
        if slice_number is None:
            slice_number = int(window.hs_SliceNumber.value())
            single_image = True
        if appMod.included_images[filename][slice_number]:
            if window.le_ThresholdOne.text() != "I":
                if window.combob_BlobsDetection.currentIndex() == 0:
                    input_threshold_one(window,slice_number)
                elif window.le_BlobsDetectionMinimumRadius.text() != "min" and window.le_BlobsDetectionMaximumRadius.text() != "max":
                    algo_index = int(window.combob_BlobsDetection.currentIndex())
                    min_radius = int(window.le_BlobsDetectionMinimumRadius.text())
                    max_radius = int(window.le_BlobsDetectionMaximumRadius.text())
                    input_threshold_one(window,slice_number)
                    image = appMod.thresholded_images[filename][slice_number]
                    window.setCursor(QCursor(Qt.WaitCursor))
                    blobs_list = blobs_detection(image,algo_index,min_radius,max_radius)
                    bl_mask = blobs_mask(image,blobs_list)
                    window.setCursor(QCursor(Qt.ArrowCursor))
                    appMod.blobs_detection_algo[filename][slice_number] = window.combob_BlobsDetection.itemText(algo_index)
                    appMod.blobs_radius[filename][slice_number] = (min_radius,max_radius)
                    blobs_thres_im = image & bl_mask
                    appMod.blobs_thresholded_images[filename][slice_number] = blobs_thres_im
                    if single_image == True:
                        set_current_image_options(window,filename,slice_number)
                        display_original_image(window,filename,slice_number,focus = "segmentation")                        
                else:
                    show_error_message("Please choose a minimum and maximum radius for blobs detection.")
            else:
                if single_image == True:
                    show_error_message("Please segment image with a thresholding option first.")
                else:
                    show_error_message(f"Please segment image {filename} slice {slice_number+1} with a thresholding option first.")
        else:
            if single_image == True:
                show_error_message("Please choose an image to process.")
    else:
        show_error_message("Please choose an image to process.")

def segmentation_to_stack(window : Ui_MainWindow, display=True):
    """Applies the segmentation with the chosen options to all the images in the stack
     Parameters:
    window : an instance of the app
    display: if True, the images will be displayed"""
    if window.combob_FileName.currentText():
        filename, original_slice_number = get_filename_slice_number(window)
        for i in range(len(window.appMod.stacks[filename])):
            if window.appMod.included_images[filename][i]:
                segmentation_to_image(window,i)
        if display == True:
            set_current_image_options(window,filename,original_slice_number)
            display_original_image(window,filename,original_slice_number,focus = "segmentation")
    else:
        show_error_message("Please choose an image to process.")

def view_segmentation(window : Ui_MainWindow):
    """Highlights the tool 'segmentation' and updates the image display
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"segmentation")
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number,focus="segmentation")
        window.combob_Threshold.setFocus()
    else:
        show_error_message("Please choose an image to process.")

def input_sieve_size(window :Ui_MainWindow):
    '''Controls the input of the sieve size which must be a positive integer or zero
    Parameters:
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"labeling")
        if not window.le_SieveSize.text().isdigit() or  int(window.le_SieveSize.text()) < 0:
                if window.le_SieveSize.text() != "":
                    show_error_message("Please insert a positive integer or zero.")
                    window.le_SieveSize.clear()         
    else:
        show_error_message("Please choose an image to process.")
        window.le_SieveSize.clear()


def apply_labeling_to_image(window :Ui_MainWindow, slice_number = None):
    '''Applies the labeling options to the current image
    Parameters:
    window : an instance of the app
    slice_number: the number of the slice in the stack'''
    appMod=window.appMod
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"labeling")
        filename = window.combob_FileName.currentText()
        single_image = False
        if slice_number is None:
            slice_number = int(window.hs_SliceNumber.value())
            single_image = True
        if appMod.included_images[filename][slice_number] == True:
            clear_results(window,filename,slice_number,"ld")
            if window.le_SieveSize.text() == "":
                if single_image == True:
                    set_current_image_options(window,filename,slice_number) 
            elif window.le_SieveSize.text().isdigit() and int(window.le_SieveSize.text()) >= 0:
                if appMod.included_images[filename][slice_number]:
                    if appMod.first_threshold[filename][slice_number]:
                        if appMod.blobs_thresholded_images[filename][slice_number] is not None:
                                image = appMod.blobs_thresholded_images[filename][slice_number]
                        else:
                            image = appMod.thresholded_images[filename][slice_number]
                        if int(window.le_SieveSize.text()) != appMod.labeling_sieve_size[filename][slice_number] or appMod.labeling_option[filename][slice_number] != window.combob_LabelingOption.currentText():
                            appMod.labeling_option[filename][slice_number] = window.combob_LabelingOption.currentText()
                            window.setCursor(QCursor(Qt.WaitCursor))
                            appMod.labeling_sieve_size[filename][slice_number] = int(window.le_SieveSize.text())
                            dots = binary_to_dots(image)
                            if dots != []:
                                if appMod.labeling_option[filename][slice_number] == window.combob_LabelingOption.itemText(1):
                                    dots, labels = watershed_custom(image,dots)
                                else:
                                    labels = labeling_custom(image,dots)
                                if window.le_SieveSize.text() != "0":
                                    dots,labels = sieve_labels(dots,labels,int(window.le_SieveSize.text()))  
                            else:
                                labels = []
                            appMod.labeling_sieve_size[filename][slice_number] = int(window.le_SieveSize.text())
                            appMod.labeling_coordinates[filename][slice_number] = dots if dots != [] else []
                            appMod.labeling_labels[filename][slice_number] = labels if labels != [] else []
                            image_8_bits = image.astype(np.uint8) * 255
                            image_with_conserved_blobs = np.stack((image_8_bits,image_8_bits,image_8_bits),axis = -1)
                            image_with_labels = np.stack((image_8_bits,image_8_bits,image_8_bits),axis = -1)
                            if labels != []:
                                unique_labels = set(labels)
                                for i, label in enumerate(unique_labels):
                                    random_color = [random.randint(0,255),random.randint(0,255),random.randint(0,255)]
                                    cluster_points = np.array([point for point, l in zip(dots, labels) if l == label])
                                    for y,x in cluster_points:
                                        image_with_conserved_blobs[y,x] = [0,255,0]
                                        image_with_labels[y,x] = random_color
                            appMod.labeling_images_with_labels[filename][slice_number] = image_with_labels
                            appMod.labeling_images_conserved_blobs[filename][slice_number] = image_with_conserved_blobs
                            if single_image == True:
                                set_current_image_options(window,filename,slice_number)
                                display_original_image(window,filename,slice_number,focus = "labeling")
                            window.setCursor(QCursor(Qt.ArrowCursor))    
                        else:
                            if single_image == True:
                                set_current_image_options(window,filename,slice_number)
                                display_original_image(window,filename,slice_number,focus = "labeling")
                    else:
                        if single_image == True:
                            show_error_message("Please segment image with a thresholding option first.")
                        else:
                            show_error_message(f"Please segment image {filename} slice {slice_number+1} with a thresholding option first.")
            else:
                show_error_message("Please choose a positive integer or 0.")
        else:
            if single_image == True:
                show_error_message("Please choose an image to process.")
    else:
        show_error_message("Please choose an image to process.")


def apply_labeling_to_stack(window :Ui_MainWindow, display=True):
    """Applies the labeling with the chosen options to all the images in the stack
     Parameters:
    window : an instance of the app
    display: if True, the images will be displayed"""
    if window.combob_FileName.currentText():
        filename, original_slice_number = get_filename_slice_number(window)
        if window.le_SieveSize.text() == "" or (window.le_SieveSize.text().isdigit() and int(window.le_SieveSize.text()) >= 0):
            for i in range(len(window.appMod.stacks[filename])):
                if window.appMod.included_images[filename][i]:
                    apply_labeling_to_image(window,i)
            if display == True:
                set_current_image_options(window,filename,original_slice_number)
                display_original_image(window,filename,original_slice_number,focus = "labeling")
        else:
            show_error_message("Please choose a positive interger or 0 as sieve size.")
    else:
        show_error_message("Please choose an image to process.")

def view_labeling(window :Ui_MainWindow):
    """Highlights the tool 'labeling' and updates the image display
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"labeling")
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number,focus="labeling")
        window.le_SieveSize.setFocus()
    else:
        show_error_message("Please choose an image to process.")

def input_background_threshold(window :Ui_MainWindow):
    """Controls that the value of the threshold is correct
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"contours")
        if not window.le_BackgroundThreshold.text().isdigit() or int(window.le_BackgroundThreshold.text()) < 0:
            if window.le_BackgroundThreshold.text() != "":
                show_error_message("Please choose an integer between 0 and 255 included.")
                window.le_BackgroundThreshold.clear()
    else:
        show_error_message("Please choose an image to process.")
        window.le_BackgroundThreshold.clear()

def combobox_contours_changed(window :Ui_MainWindow):
    """Triggers several actrions when the combox with the contouring option is activated
    Parameters:
    window : an instance of the app"""
    highlight_groupbox(window,"contours")
    if window.combob_FileName.currentText():
        filename, slice_number = get_filename_slice_number(window)
        if window.appMod.contours_algo[filename][slice_number] is not None:
            clear_results(window,filename,slice_number,"cd")
            display_original_image(window,filename,slice_number,focus="contours")
    else:
        show_error_message("Please choose an image to process.")

def determine_main_slice(appMod : AppModel, filename):
    '''Determines the slice with the largest contour in a stack
    appMod: an instance of the class AppModel
    filename: the name of the file with the stack of images'''
    max_contours = 0
    main_slice_index = 0
    for i in range(len(appMod.stacks[filename])):
        if appMod.included_images[filename][i] and appMod.contours_mask[filename][i] is not None:
            sum_contours = np.sum(appMod.contours_mask[filename][i])
            if  sum_contours >= max_contours:
                appMod.contours_main_slice[filename][main_slice_index] = False
                appMod.contours_main_slice[filename][i] = True
                main_slice_index = i
                max_contours = sum_contours

def apply_contours_to_image(window :Ui_MainWindow, slice_number=None):
    """Applies the chosen contouring algorithm to the image
    Parameters:
    window : an instance of the app
    slice_number: the index of the image in the stack"""
    appMod=window.appMod
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"contours")
        filename = window.combob_FileName.currentText()
        single_image = False
        if slice_number is None:
            slice_number = int(window.hs_SliceNumber.value())
            single_image = True
        if appMod.included_images[filename][slice_number]:
            if appMod.first_threshold[filename][slice_number] is not None:
                if window.le_BackgroundThreshold.text() != "":
                    clear_results(window,filename,slice_number,"d")
                    appMod.results_density[filename] = None
                    algo_index = window.combob_Contours.currentIndex()
                    threshold_value = int(window.le_BackgroundThreshold.text())
                    if appMod.corrected_images[filename][slice_number] is not None:
                        image_to_contour = appMod.corrected_images[filename][slice_number]
                    else:
                        image_to_contour = appMod.stacks[filename][slice_number]
                    window.setCursor(QCursor(Qt.WaitCursor))
                    if algo_index == 0:
                        contour_mask = contour_scan(image_to_contour,threshold_value)
                    elif algo_index == 1:
                        contour_mask = contour_spreading_4(image_to_contour,threshold_value)
                    elif algo_index == 2:
                        contour_mask = contour_spreading_8(image_to_contour,threshold_value)
                    elif algo_index == 3:
                        contour_mask = contour_shrinking_box(image_to_contour,threshold_value)
                    else:
                        contour_mask = image_to_contour > threshold_value
                    window.setCursor(QCursor(Qt.ArrowCursor))
                    contour_centroid_y_x = calculate_contours_centroid(contour_mask)
                    appMod.contours_centroids[filename][slice_number] = contour_centroid_y_x
                    appMod.contours_algo[filename][slice_number] = window.combob_Contours.currentText()
                    appMod.contours_background[filename][slice_number] = threshold_value
                    appMod.contours_mask[filename][slice_number] = contour_mask
                    if single_image == True:
                        determine_main_slice(appMod,filename)
                        set_current_image_options(window,filename,slice_number)
                        display_original_image(window,filename,slice_number,focus = "contours")                        
                else:
                    show_error_message("Please choose a background value.")
            else:
                if single_image == True:
                    show_error_message("Please segment image with a thresholding option first.")
                else:
                    show_error_message(f"Please segment image {filename} slice {slice_number+1} with a thresholding option first.")
    else:
        show_error_message("Please choose an image to process.")

def apply_contours_to_stack(window :Ui_MainWindow, display = True):
    """Applies the chosen contouring algorithm to the current stack of images
    Parameters:
    window : an instance of the app
    display: if True, the images will be displayed"""
    if window.combob_FileName.currentText():
        filename, original_slice_number = get_filename_slice_number(window)
        if window.le_BackgroundThreshold.text() != "":
            for i in range(len(window.appMod.stacks[filename])):
                if window.appMod.included_images[filename][i]:
                    apply_contours_to_image(window,i)
            determine_main_slice(window.appMod,filename)
            if display == True:
                set_current_image_options(window,filename,original_slice_number)
                display_original_image(window,filename,original_slice_number,focus = "contours")
        else:
            show_error_message("Please choose a background threshold value.")
    else:
        show_error_message("Please choose an image to process.")

def view_contours(window :Ui_MainWindow):
    """Highlights the tool 'contours' and updates the image display
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"contours")
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number,focus="contours")
        window.combob_Contours.setFocus()
    else:
        show_error_message("Please choose an image to process.")

def edit_centroid_x(window :Ui_MainWindow):
    '''Controls the input of the x coordinate for the centroid and draws the new location on the image
    Parameters:
    window : an instance of the app'''
    if window.focus == "contours":
        appMod=window.appMod
        filename,slice_number = get_filename_slice_number(window)
        image = appMod.contours_mask[filename][slice_number]
        if window.le_CentroidX.text().isdigit() and int(window.le_CentroidX.text()) >= 0 \
        and int(window.le_CentroidX.text()) < image.shape[1]:
            appMod.contours_centroids[filename][slice_number][1] = int(window.le_CentroidX.text())
            appMod.density_target_heatmap[filename][slice_number] = None
            appMod.density_target_layers[filename][slice_number] = None
            set_current_image_options(window,filename,slice_number)
            display_secondary_image(2,window,image,focus="contours",title="Contoured image")    
        else:
            show_error_message("Please enter an pixel value in the range of the x image shape")
            window.le_CentroidX.setText(str(appMod.contours_centroids[filename][slice_number][1]))

def edit_centroid_y(window :Ui_MainWindow):
    '''Controls the input of the y coordinate for the centroid and draws the new location on the image
    Parameters:
    window : an instance of the app'''
    if window.focus == "contours":
        appMod=window.appMod
        filename,slice_number = get_filename_slice_number(window)
        image = appMod.contours_mask[filename][slice_number]
        if window.le_CentroidY.text().isdigit() and int(window.le_CentroidY.text()) >= 0 \
        and int(window.le_CentroidY.text()) < image.shape[0]:
            appMod.contours_centroids[filename][slice_number][0] = int(window.le_CentroidY.text())
            appMod.density_target_heatmap[filename][slice_number] = None
            appMod.density_target_layers[filename][slice_number] = None
            set_current_image_options(window,filename,slice_number)
            display_secondary_image(2,window,image,focus="contours",title="Contoured image")    
        else:
            show_error_message("Please enter an pixel value in the range of the x image shape")
            window.le_CentroidY.setText(str(appMod.contours_centroids[filename][slice_number][0]))

def set_centroid_auto(window :Ui_MainWindow):
    '''Automatically computes the coordinates of the centroid of a contoured image and places it on the image
    Parameters:
    window : an instance of the app'''
    if window.focus == "contours":
        appMod=window.appMod
        filename,slice_number = get_filename_slice_number(window)
        image = appMod.contours_mask[filename][slice_number]
        centroid_y_x = calculate_contours_centroid(image)
        appMod.contours_centroids[filename][slice_number] = centroid_y_x
        appMod.density_target_heatmap[filename][slice_number] = None
        appMod.density_target_layers[filename][slice_number] = None
        set_current_image_options(window,filename,slice_number)
        display_secondary_image(2,window,image,focus="contours",title="Contoured image")

def change_main_slice(window :Ui_MainWindow):
    '''Changes the check in the combobox when manually selecting a main slice
    Parameters:
    window : an instance of the app'''
    appMod=window.appMod
    filename,slice_number = get_filename_slice_number(window)
    length = len(appMod.stacks[filename])
    appMod.contours_main_slice[filename] = [False]*length
    appMod.contours_main_slice[filename][slice_number] = True
    appMod.results_distance[filename] = None
    display_secondary_image(2,window,focus = "contours")


def input_target_layers(window :Ui_MainWindow):
    '''Controls the input of the number of layers
    Parameters:
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"density")
        if not window.le_DensityTargetLayers.text().isdigit() or int(window.le_DensityTargetLayers.text()) <=0:
            if window.le_DensityTargetLayers.text() != "":
                show_error_message("Please insert a positive integer.")
                window.le_DensityTargetLayers.clear()
    else:
        show_error_message("Please choose an image to process.")
        window.le_DensityTargetLayers.clear()

def input_kernel_size(window :Ui_MainWindow):
    '''Controls the input for the kernel size
    Parameters:
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        filename,slice_number = get_filename_slice_number(window)
        if window.appMod.included_images[filename][slice_number] == True:
            image = window.appMod.stacks[filename][slice_number]
            highlight_groupbox(window,"density")
            if not window.le_DensityMapKernelSize.text().isdigit() or int(window.le_DensityMapKernelSize.text()) <3 \
            or int(window.le_DensityMapKernelSize.text()) %2 ==0 or int(window.le_DensityMapKernelSize.text()) >= min(image.shape[0],image.shape[1]):
                    if window.le_DensityMapKernelSize.text() != "":
                        show_error_message("Please insert a positive integer at least equal to 3 and smaller than the image shape.")
                        window.le_DensityMapKernelSize.clear()
        else:
            show_error_message("Please choose an image to process.")
            window.le_DensityMapKernelSize.clear()
    else:
        show_error_message("Please choose an image to process.")
        window.le_DensityMapKernelSize.clear()

def apply_density_to_image(window :Ui_MainWindow, slice_number=None):
    """Applies the density algorithms to the image
    Parameters:
    window : an instance of the app
    slice_number: the index of the image in the stack"""
    if window.combob_FileName.currentText():
        appMod=window.appMod
        highlight_groupbox(window,"density")
        filename = window.combob_FileName.currentText()
        single_image = False
        if slice_number is None:
            slice_number = int(window.hs_SliceNumber.value())
            single_image = True
        if appMod.included_images[filename][slice_number]:
            if appMod.first_threshold[filename][slice_number] is not None:
                if appMod.labeling_labels[filename][slice_number] is not None:
                    if appMod.contours_mask[filename][slice_number] is not None:
                        if window.le_DensityTargetLayers.text() != "" and window.le_DensityMapKernelSize.text() != "":
                            thresholded_image = dots_to_binary(appMod.stacks[filename][slice_number],appMod.labeling_coordinates[filename][slice_number])
                            contoured_image = appMod.contours_mask[filename][slice_number]
                            centroids_image = dots_to_binary(appMod.stacks[filename][slice_number],calculate_centroids(appMod.labeling_coordinates[filename][slice_number],appMod.labeling_labels[filename][slice_number]))
                            window.setCursor(QCursor(Qt.WaitCursor))
                            if appMod.density_target_layers[filename][slice_number] != int(window.le_DensityTargetLayers.text()) or appMod.density_target_heatmap[filename][slice_number] is None:
                                appMod.density_target_layers[filename][slice_number] = int(window.le_DensityTargetLayers.text())
                                layers = appMod.density_target_layers[filename][slice_number]
                                centroid_y = appMod.contours_centroids[filename][slice_number][0]
                                centroid_x = appMod.contours_centroids[filename][slice_number][1]
                                target_map, target_count = get_targets(thresholded_image,contoured_image,centroids_image,layers,centroid_y,centroid_x)
                                appMod.density_target_heatmap[filename][slice_number] = target_map
                                appMod.density_taget_centroid_heatmap[filename][slice_number] = target_count
                                appMod.results_density[filename] = None  
                            if appMod.density_map_kernel_size[filename][slice_number] != int(window.le_DensityMapKernelSize.text()) or appMod.density_map_heatmap[filename][slice_number] is None:
                                appMod.density_map_kernel_size[filename][slice_number] = int(window.le_DensityMapKernelSize.text())
                                d_map_percentage, d_map_count = density_maps(thresholded_image,contoured_image,centroids_image,appMod.density_map_kernel_size[filename][slice_number])
                                appMod.density_map_heatmap[filename][slice_number] = d_map_percentage
                                appMod.density_map_centroid_heatmap[filename][slice_number] = d_map_count
                                appMod.results_density[filename] = None
                            if single_image == True:
                                display_original_image(window,filename,slice_number,focus = "density")
                            window.setCursor(QCursor(Qt.ArrowCursor))
                        else:
                            show_error_message("Please choose target layers and a kernel size.")                    
                    else:
                        if single_image == True:
                            show_error_message("Please choose contouring option first.")
                        else:
                            show_error_message(f"Please process image {filename} slice {slice_number+1} with a contouring option first.")
                else:
                    if single_image == True:
                        show_error_message("Please label the image first.")
                    else:
                        show_error_message(f"Please label image {filename} slice {slice_number+1} first.")
            else:
                if single_image == True:
                    show_error_message("Please segment image with a thresholding option first.")
                else:
                    show_error_message(f"Please segment image {filename} slice {slice_number+1} with a thresholding option first.")
        else:
            if single_image == True:
                show_error_message("Please choose an image to process.")
    else:
        show_error_message("Please choose an image to process.")

def apply_density_to_stack(window :Ui_MainWindow, display = True):
    """Applies the density algorithms to the current stack of images
    Parameters:
    window : an instance of the app
    display: if True, the images will be displayed"""
    if window.combob_FileName.currentText():
        filename, original_slice_number = get_filename_slice_number(window)
        if window.le_DensityTargetLayers.text() != "" and window.le_DensityMapKernelSize.text() !="":
            for i in range(len(window.appMod.stacks[filename])):
                if window.appMod.included_images[filename][i]:
                    apply_density_to_image(window,i)
            if display == True:
                set_current_image_options(window,filename,original_slice_number)
                display_original_image(window,filename,original_slice_number,focus = "density")
        else:
            show_error_message("Please choose target layers and a kernel size.")
    else:
        show_error_message("Please choose an image to process.")

def view_density(window :Ui_MainWindow):
    """Highlights the tool 'density' and updates the image display
    Parameters:
    window : an instance of the app
    appMod : an instance of the class AppModel containing the app variables"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"density")
        filename, slice_number = get_filename_slice_number(window)
        display_original_image(window,filename,slice_number,focus="density")
    else:
        show_error_message("Please choose an image to process.")

def combobox_density_changed(window :Ui_MainWindow):
    '''Changes the diplay of the images when the combobox for the density is changed
    Parameters:
    window : an instance of the app'''
    filename,slice_number=get_filename_slice_number(window)
    if window.combob_DensityDisplay.currentText() == "Percentage":
        display_secondary_image(1,window,window.appMod.density_map_heatmap[filename][slice_number],focus="density",title="Convoluted density heatmap (percentage)")
        display_secondary_image(2,window,window.appMod.density_target_heatmap[filename][slice_number],focus = "density", title = "Target density heatmap (percentage)")
    if window.combob_DensityDisplay.currentText() == "Count":
        display_secondary_image(1,window,window.appMod.density_map_centroid_heatmap[filename][slice_number],focus="density",title="Convoluted density heatmap (Count)")
        display_secondary_image(2,window,window.appMod.density_taget_centroid_heatmap[filename][slice_number],focus = "density", title = "Target density heatmap (Count)")      

def input_z_thickness(window :Ui_MainWindow):
    '''Controls the input of the thickness of the slices
    Parameters:
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"results")
        if window.le_ZThickness.text() == "" or is_float(window.le_ZThickness.text()):
            filename = window.combob_FileName.currentText()
            if window.le_ZThickness.text() == "":
                window.appMod.stack_infos[filename][0] = None
            else:
                window.appMod.stack_infos[filename][0] = float(window.le_ZThickness.text())
            window.appMod.results_distance[filename] = None
        else:
            show_error_message("Please input a floating number.")
    else:
        show_error_message("Please choose a stack of images to process.")
        window.le_ZThickness.clear()

def input_inter_z(window :Ui_MainWindow):
    """Controls the input of the space between slices
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"results")
        if window.le_InterZ.text() == "" or is_float(window.le_InterZ.text()):
            filename = window.combob_FileName.currentText()
            if window.le_InterZ.text() == "":
                window.appMod.stack_infos[filename][1] = None
            else:
                window.appMod.stack_infos[filename][1] = float(window.le_InterZ.text())
            window.appMod.results_distance[filename] = None
        else:
            show_error_message("Please input a floating number.")
    else:
        show_error_message("Please choose a stack of images to process.")
        window.le_InterZ.clear()

def input_pixel_size(window :Ui_MainWindow):
    """Controls the input of the pixel size
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        highlight_groupbox(window,"results")
        if window.le_PixelSize.text() == "" or is_float(window.le_PixelSize.text()):
            filename = window.combob_FileName.currentText()
            if window.le_PixelSize.text() == "":
                window.appMod.stack_infos[filename][2] = None
            else:
                window.appMod.stack_infos[filename][2] = float(window.le_PixelSize.text())
            window.appMod.results_distance[filename] = None
        else:
            show_error_message("Please input a floating number.")
    else:
        show_error_message("Please choose a stack of images to process.")
        window.le_PixelSize.clear()

def apply_infos_to_stacks(window :Ui_MainWindow):
    """Applies the input data to all the stacks
    Parameters:
    window : an instance of the app"""
    if window.combob_FileName.currentText():
        appMod=window.appMod
        highlight_groupbox(window,"results")
        stack_names = list(appMod.stacks.keys())
        for filename in stack_names:
            if window.le_ZThickness.text() == "":
                appMod.stack_infos[filename][0] = None
            else:
                appMod.stack_infos[filename][0] = float(window.le_ZThickness.text())
            if window.le_InterZ.text() == "":
                appMod.stack_infos[filename][1] = None
            else:
                appMod.stack_infos[filename][1] = float(window.le_InterZ.text())
            if window.le_PixelSize.text() == "":
                appMod.stack_infos[filename][2] = None
            else:
                appMod.stack_infos[filename][2] = float(window.le_PixelSize.text())
            appMod.results_distance[filename] = None
    else:
        show_error_message("Please choose a stack of images to process.")

def disable_results_checkboxes(window :Ui_MainWindow):
    '''Disables checkboxes in the result section
    Parameters:
    window : an instance of the app'''
    for widget in window.gb_ResultsChoice.findChildren(QCheckBox):
        widget.setChecked(False)
        widget.setEnabled(False)

def enable_count_results(window :Ui_MainWindow):
    '''Enables the checkboxes for count results
    Parameters:
    window : an instance of the app'''
    window.cb_ResultsCount.setEnabled(True)
    window.cb_ResultsCount.setChecked(True)

def enable_density_results(window :Ui_MainWindow):
    '''Enables the checkboxes for density results
    Parameters:
    window : an instance of the app'''
    window.cb_ResultsDensityCount.setEnabled(True)
    window.cb_ResultsDensityPercentage.setEnabled(True)
    window.cb_ResultsDensityCount.setChecked(True)
    window.cb_ResultsDensityPercentage.setChecked(True)

def enable_distance_results(window :Ui_MainWindow,filename):
    '''Enables the checkboxes for distance results
    Parameters:
    window : an instance of the app'''
    window.cb_ResultsDistanceOwnCentroid.setEnabled(True)
    window.cb_ResultsDistanceOwnCentroid.setChecked(True)
    if window.appMod.stack_infos[filename][1] is not None and window.appMod.stack_infos[filename][2] is not None:
        window.cb_ResultsDistanceSpecificCentroid.setEnabled(True)
        window.cb_ResultsDistanceSpecificCentroid.setChecked(True)

def compute_count_results(window : Ui_MainWindow,filename,nb_slices):
    '''Computes the count results
    Parameters:
    window : an instance of the app
    filename: the name of the file
    nb_slices: the number of slices in the stack'''
    relative_path = get_filename(filename)
    count_results = [[relative_path,"Blobs count","Mean size"," Median size","Segmentation threshold(s)",\
                      "Blobs detection","Blobs min/max radius","Rolling ball radius","Watershed","Sieve size"]]
    total = 0
    all_labels = []
    appMod=window.appMod
    for i in range(nb_slices):
        if appMod.included_images[filename][i]:
            slice = f"slice_{i+1:02d}/{nb_slices}"
            if appMod.labeling_coordinates[filename][i] is not None:
                if appMod.labeling_labels[filename][i] == []:
                    count = 0
                else:
                    count = np.max(appMod.labeling_labels[filename][i])+1
                if all_labels == []:
                    all_labels = appMod.labeling_labels[filename][i].copy()
                else:
                    value = max(all_labels)+1
                    all_labels.extend([x + value for x in appMod.labeling_labels[filename][i]])
                total += count
                if count == 0:
                    median, SD = 0,0
                else:
                    median, SD = mean_median_size(appMod.labeling_labels[filename][i])
                if appMod.threshold_algo[filename][i] == window.combob_Threshold.itemText(0):
                    thresholds = str(appMod.first_threshold[filename][i])
                else:
                    thresholds = f"{appMod.first_threshold[filename][i]}_{appMod.second_threshold[filename][i]}"
                if appMod.blobs_detection_algo[filename][i] is not None:
                    blobs_algo = appMod.blobs_detection_algo[filename][i]
                    blobs_radius = f"{appMod.blobs_radius[filename][i][0]}_{appMod.blobs_radius[filename][i][1]}"
                else:
                    blobs_algo = "-"
                    blobs_radius = "-"
                if appMod.rolling_ball_param[filename][i] is not None:
                    rbr = appMod.rolling_ball_param[filename][i]
                else:
                    rbr = "-"
                if appMod.labeling_option[filename][i] == window.combob_LabelingOption.itemText(1):
                    ws = "yes"
                else:
                    ws = "no"
                sieve_size = appMod.labeling_sieve_size[filename][i]
            else:
                count,median,SD,thresholds,blobs_algo,blobs_radius,rbr,ws,sieve_size = "-","-","-","-","-","-","-","-","-"
            count_results.append([slice,count,median,SD,thresholds,blobs_algo,blobs_radius,rbr,ws,sieve_size])
    tot_median, tot_SD = mean_median_size(all_labels)
    count_results.append(["Total",total,tot_median,tot_SD,"-","-","-","-","-","-"])    
    appMod.results_count[filename] = count_results

def input_count_results(window : Ui_MainWindow, filename):
    '''Input the count results in the QTableWidget
    Parameters:
    window : an instance of the app
    filename: the name of the file'''
    count_results = window.appMod.results_count[filename]
    window.tw_Count.clear()
    window.tw_Count.setRowCount(len(count_results))
    window.tw_Count.setColumnCount(len(count_results[0]))
    for i in range(len(count_results)):
        for j in range(len(count_results[0])):
            item = QTableWidgetItem(str(count_results[i][j]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            window.tw_Count.setItem(i,j,item)
    window.tw_Count.resizeColumnsToContents()

def compute_density_results(window : Ui_MainWindow,filename,nb_slices):
    '''Computes the density results
    Parameters:
    window : an instance of the app
    filename: the name of the file
    nb_slices: the number of slices in the stack'''
    appMod=window.appMod
    relative_path = get_filename(filename)
    density_results = [[relative_path,"Mean density %","Blobs area","Contours area","Target % median","Target % min","Target % max",\
                        "Heatmap % median","Heatmap % min","Heatmap % max",\
                        "Target count mean","Target count median","Target count min","Target count max",\
                        "Heatmap count mean","Heatmap count median","Heatmap count min","Heatmap count max",\
                            "Contours algorithm","Contours threshold","Target layers","Kernel size"]]
    all_densities_targets_percentage = []
    all_densities_maps_percentage = []
    all_densities_targets_count = []
    all_densities_maps_count = []
    total_blobs_area = 0
    total_area = 0
    for i in range(nb_slices):
        if appMod.included_images[filename][i]:
            slice = f"slice_{i+1:02d}/{nb_slices}"
            if appMod.density_target_heatmap[filename][i] is not None:
                d_target = appMod.density_target_heatmap[filename][i]
                d_map = appMod.density_map_heatmap[filename][i]
                d_target_count = appMod.density_taget_centroid_heatmap[filename][i]
                d_map_count = appMod.density_map_centroid_heatmap[filename][i]
                mask_contour = appMod.contours_mask[filename][i]
                if all_densities_targets_percentage == []:
                    all_densities_targets_percentage = d_target[mask_contour].tolist()
                    all_densities_maps_percentage = d_map[mask_contour].tolist()
                    all_densities_targets_count = d_target_count[mask_contour].tolist()
                    all_densities_maps_count = d_map_count[mask_contour].tolist()
                else:
                    all_densities_targets_percentage.extend(d_target[mask_contour].tolist())
                    all_densities_maps_percentage.extend(d_map[mask_contour].tolist())
                    all_densities_targets_count.extend(d_target_count[mask_contour].tolist())
                    all_densities_maps_count.extend(d_map_count[mask_contour].tolist())
                area = np.sum(mask_contour)
                blobs_area = len(appMod.labeling_coordinates[filename][i])
                total_area +=area
                total_blobs_area += blobs_area
                min_t,max_t,mean_t,median_t = min_max_mean_median_density(d_target,mask_contour)
                min_m,max_m,_,median_m = min_max_mean_median_density(d_map,mask_contour)
                min_t_count,max_t_count,mean_t_count,median_t_count= min_max_mean_median_density(d_target_count,mask_contour)
                min_m_count,max_m_count,mean_m_count,median_m_count = min_max_mean_median_density(d_map_count,mask_contour)
                contours_algo = appMod.contours_algo[filename][i]
                contours_threshold = appMod.contours_background[filename][i]
                layers = appMod.density_target_layers[filename][i]
                kernel_size = appMod.density_map_kernel_size[filename][i]
                density_results.append([slice,mean_t,blobs_area,area,median_t,min_t,max_t,median_m,min_m,max_m,\
                                        mean_t_count,round(median_t_count),round(min_t_count),round(max_t_count),\
                                        mean_m_count,round(median_m_count),round(min_m_count),round(max_m_count),\
                                        contours_algo,contours_threshold,layers,kernel_size])
            else:
                density_results.append([slice,"-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-"])
    if len(all_densities_targets_percentage) >0:
        min_tot_t,max_tot_t,mean_tot_t,median_tot_t = round(min(all_densities_targets_percentage),3),round(max(all_densities_targets_percentage),3),\
            round(np.mean(all_densities_targets_percentage),3),round(np.median(all_densities_targets_percentage),3)
    else:
        min_tot_t,max_tot_t,mean_tot_t,median_tot_t = "-","-","-","-"
    if len(all_densities_maps_percentage) >0:
        min_tot_m,max_tot_m,median_tot_m = round(min(all_densities_maps_percentage),3),round(max(all_densities_maps_percentage),3),round(np.median(all_densities_maps_percentage),3)
    else:
        min_tot_m,max_tot_m,median_tot_m = "-","-","-"
    if len(all_densities_targets_count) >0:
        min_tot_t_count,max_tot_t_count,mean_tot_t_count,median_tot_t_count = round(min(all_densities_targets_count)),round(max(all_densities_targets_count)),\
            round(np.mean(all_densities_targets_count),3),round(np.median(all_densities_targets_count))
    else:
        min_tot_t_count,max_tot_t_count,mean_tot_t_count,median_tot_t_count = "-","-","-","-"
    if len(all_densities_maps_count) >0:
        min_tot_m_count,max_tot_m_count,mean_tot_m_count,median_tot_m_count = round(min(all_densities_maps_count)),round(max(all_densities_maps_count)),\
            round(np.mean(all_densities_maps_count),3),round(np.median(all_densities_maps_count))
    else:
        min_tot_m_count,max_tot_m_count,mean_tot_m_count,median_tot_m_count = "-","-","-","-"
    density_results.append(["Total",mean_tot_t,total_blobs_area,total_area,median_tot_t,min_tot_t,max_tot_t,median_tot_m,min_tot_m,max_tot_m,\
                            mean_tot_t_count,median_tot_t_count,min_tot_t_count,max_tot_t_count,mean_tot_m_count,median_tot_m_count,min_tot_m_count,max_tot_m_count,"-","-","-","-"])    
    appMod.results_density[filename] = density_results

def input_density_results(window : Ui_MainWindow, filename):
    '''Input the density results in the QTableWidget
    Parameters:
    window : an instance of the app
    filename: the name of the file'''
    density_results = window.appMod.results_density[filename]
    window.tw_Density.clear()
    window.tw_Density.setRowCount(len(density_results))
    window.tw_Density.setColumnCount(len(density_results[0]))
    for i in range(len(density_results)):
        for j in range(len(density_results[0])):
            item = QTableWidgetItem(str(density_results[i][j]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            window.tw_Density.setItem(i,j,item)
    window.tw_Density.resizeColumnsToContents()

def compute_distance_results(window : Ui_MainWindow,filename,nb_slices):
    '''Computes the distance results
    Parameters:
    window : an instance of the app
    filename: the name of the file
    nb_slices: the number of slices in the stack'''
    appMod=window.appMod
    relative_path = get_filename(filename)
    if not any(appMod.contours_main_slice[filename]):
        determine_main_slice(appMod,filename)
    for i, value in enumerate(appMod.contours_main_slice[filename]):
        if value:
            main_slice = i
            break
    distance_results = [[relative_path,"Centroid X","Centroid Y","Centroid Z","Mean distance to own centroid","median DTOC","min DTOC","max DTOC",\
                         f"Mean distance to centroid of slice {main_slice+1}",f"median DTCOS{main_slice+1}",f"min DTCOS{main_slice+1}",f"max DTCOS{main_slice+1}",\
                            "Slice thickness","Interslice space","Pixel size"]]
    all_DTOC = []
    all_DTCOS = []
    if appMod.stack_infos[filename][1] is not None and appMod.stack_infos[filename][2] is not None:
        if appMod.stack_infos[filename][0] is None:
            slice_thickness = 0
        else:
            slice_thickness = appMod.stack_infos[filename][0]
        interslice_space = appMod.stack_infos[filename][1]
        pixel_size = appMod.stack_infos[filename][2]
        main_slice_y_coordinate, main_slice_x_coordinate = appMod.contours_centroids[filename][main_slice]
        main_slice_z_coordinate = round((main_slice * ((slice_thickness+interslice_space) / pixel_size)),1)
    else:
        slice_thickness = "-"
        interslice_space = "-"
        pixel_size = "-"
    for i in range(nb_slices):
        if appMod.included_images[filename][i]:
            slice = f"slice_{i+1:02d}/{nb_slices}"
            if appMod.labeling_labels[filename][i] is not None and appMod.contours_centroids[filename][i] is not None:
                labels = appMod.labeling_labels[filename][i]
                dots = appMod.labeling_coordinates[filename][i]
                centroid_y,centroid_x = appMod.contours_centroids[filename][i]
                centroid_y=round(centroid_y,1)
                centroid_x=round(centroid_x,1)
                blobs_centroids_list, DTOC = calculate_blobs_centroids_and_DTOC(dots,labels,centroid_x,centroid_y)
                if DTOC != []:
                    if all_DTOC == []:
                        all_DTOC = DTOC
                    else:
                        all_DTOC.extend(DTOC)
                    DTOC_mean,DTOC_median,DTOC_min,DTOC_max = round(np.mean(DTOC),1),round(np.median(DTOC),1),round(min(DTOC),1),round(max(DTOC),1)
                else:
                    DTOC_mean,DTOC_median,DTOC_min,DTOC_max = "-","-","-","-"
                if appMod.stack_infos[filename][1] is not None and appMod.stack_infos[filename][2] is not None:
                    z_coordinate = round((i * ((slice_thickness+interslice_space) / pixel_size)),1)
                    if len(blobs_centroids_list) != 0:
                        if i != main_slice:
                            z_difference_square = (z_coordinate - main_slice_z_coordinate)**2
                            DTCOS = np.sqrt((blobs_centroids_list[:,0]-main_slice_y_coordinate)**2 + (blobs_centroids_list[:,1]-main_slice_x_coordinate)**2 + z_difference_square)
                            DTCOS = DTCOS.tolist()
                            DTCOS_mean,DTCOS_median,DTCOS_min,DTCOS_max = round(np.mean(DTCOS),1),round(np.median(DTCOS),1),round(min(DTCOS),1),round(max(DTCOS),1)
                        else:
                            DTCOS = DTOC
                            DTCOS_mean,DTCOS_median,DTCOS_min,DTCOS_max = DTOC_mean,DTOC_median,DTOC_min,DTOC_max
                        if all_DTCOS == []:
                            all_DTCOS = DTCOS
                        else:
                            all_DTCOS.extend(DTCOS)
                    else:
                        DTCOS_mean,DTCOS_median,DTCOS_min,DTCOS_max = "-","-","-","-"
                else:
                    z_coordinate = f"z{i+1}"
                    DTCOS_mean,DTCOS_median,DTCOS_min,DTCOS_max = "-","-","-","-"
                distance_results.append([slice,centroid_x,centroid_y,z_coordinate,DTOC_mean,DTOC_median,DTOC_min,DTOC_max,DTCOS_mean,DTCOS_median,DTCOS_min,DTCOS_max,slice_thickness,interslice_space,pixel_size])
            else:
                distance_results.append([slice,"-","-","-","-","-","-","-","-","-","-","-",slice_thickness,interslice_space,pixel_size])
    if len(all_DTOC) != 0:
        min_tot_DTOC,max_tot_DTOC,mean_tot_DTOC,median_tot_DTOC = round(min(all_DTOC),1),round(max(all_DTOC),1), round(np.mean(all_DTOC),1),round(np.median(all_DTOC),1)
    else:
        min_tot_DTOC,max_tot_DTOC,mean_tot_DTOC,median_tot_DTOC = "-","-","-","-"
    if DTCOS_mean != "-":
        min_tot_DTCOS,max_tot_DTCOS,mean_tot_DTCOS,median_tot_DTCOS = round(min(all_DTCOS),1),round(max(all_DTCOS),1), round(np.mean(all_DTCOS),1),round(np.median(all_DTCOS),1)
    else:
        min_tot_DTCOS,max_tot_DTCOS,mean_tot_DTCOS,median_tot_DTCOS = "-","-","-","-"
    distance_results.append(["Total","-","-","-",mean_tot_DTOC,median_tot_DTOC,min_tot_DTOC,max_tot_DTOC,mean_tot_DTCOS,median_tot_DTCOS,min_tot_DTCOS,max_tot_DTCOS,slice_thickness,interslice_space,pixel_size])    
    appMod.results_distance[filename] = distance_results

def input_distance_results(window : Ui_MainWindow, filename):
    '''Input the distance results in the QTableWidget
    Parameters:
    window : an instance of the app
    filename: the name of the file'''
    distance_results = window.appMod.results_distance[filename]
    window.tw_Distance.clear()
    window.tw_Distance.setRowCount(len(distance_results))
    window.tw_Distance.setColumnCount(len(distance_results[0]))
    for i in range(len(distance_results)):
        for j in range(len(distance_results[0])):
            item = QTableWidgetItem(str(distance_results[i][j]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            window.tw_Distance.setItem(i,j,item)
    window.tw_Distance.resizeColumnsToContents()
    
def view_results_page(window :Ui_MainWindow):
    '''Displays the result page
    Parameters:
    window : an instance of the app'''
    if window.combob_FileName.currentText():
        appMod=window.appMod
        window.setCursor(QCursor(Qt.WaitCursor))
        highlight_groupbox(window,"results")
        filename = window.combob_FileName.currentText()
        nb_slices = len(appMod.stacks[filename])
        count = False
        density = False
        distance = False
        at_least_one_slice = False
        window.tw_Count.setEnabled(False)
        window.tw_Density.setEnabled(False)
        window.tw_Distance.setEnabled(False)
        disable_results_checkboxes(window)
        for i in range(nb_slices):
            if appMod.included_images[filename][i]:
                at_least_one_slice = True
                if appMod.labeling_labels[filename][i] is not None:
                    count = True
                    window.tw_Count.setEnabled(True)
                if appMod.density_target_heatmap[filename][i] is not None:
                    density = True
                    window.tw_Density.setEnabled(True)
                if appMod.contours_mask[filename][i] is not None and appMod.labeling_labels[filename][i] is not None:
                    distance = True
                    window.tw_Distance.setEnabled(True)
        if at_least_one_slice == False:
            show_error_message("Please select at least one slice to get some results.")
        if count == False and density == False and distance == False:
            show_error_message("Please process the images to get results.")
        else:
            if count == True:
                if appMod.results_count[filename] is None:
                    compute_count_results(window,filename,nb_slices)
                input_count_results(window,filename)
            if density == True:
                if appMod.results_density[filename] is None:
                    compute_density_results(window,filename,nb_slices)
                input_density_results(window,filename)
            if distance == True:
                if appMod.results_distance[filename] is None:
                    compute_distance_results(window,filename,nb_slices)
                input_distance_results(window,filename)
            if appMod.results_count[filename] is not None:
                enable_count_results(window)
            if appMod.results_density[filename] is not None:
                enable_density_results(window)
            if appMod.results_distance[filename] is not None:
                enable_distance_results(window,filename)
            if window.lb_ResultsDestinationFolder.text() == "":
                window.lb_ResultsDestinationFolder.setText("./results/")
            window.le_ResultsCSVFileName.setText(get_filename_without_extension(filename)+"_results")
            window.sw_Data.setCurrentIndex(1)
            window.tabWidget.show()
            window.gb_ResultsChoice.show()
            window.frame_4.show()
        window.setCursor(QCursor(Qt.ArrowCursor))
    else:
        show_error_message("Please choose a stack of images to process.")

def select_all(window :Ui_MainWindow):
    '''Checks the checkboxes for all results
    Parameters:
    window : an instance of the app'''
    widget = window.gb_ResultsChoice
    for checkbox in widget.findChildren(QCheckBox):
        if checkbox.isEnabled():
            checkbox.setChecked(True)

def select_none(window :Ui_MainWindow):
    '''Unchecks the checkboxes for all results
    Parameters:
    window : an instance of the app'''
    widget = window.gb_ResultsChoice
    for checkbox in widget.findChildren(QCheckBox):
        if checkbox.isEnabled():
            checkbox.setChecked(False)

def select_folder(window :Ui_MainWindow,widget):
    """Selects a folder and displays it in a widget
    Parameters:
    window : an instance of the app
    widget: the widget in which to display the chosen folder name"""
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    dialog = QFileDialog(window, "Select Folder", options=options)
    dialog.setFileMode(QFileDialog.FileMode.Directory)
    folder_path = QFileDialog.getExistingDirectory()
    widget.setText(folder_path)

def return_to_images_screen(window :Ui_MainWindow):
    """Goes back from the result display to the image display
    Parameters:
    window : an instance of the app"""
    highlight_groupbox(window,None)
    filename, slice_number = get_filename_slice_number(window)
    display_original_image(window,filename,slice_number,focus=None)

def check_file_name(window : Ui_MainWindow, widget):
    """Checks that an input file name only contains allowed characters and displays the name in a widget
    Parameters:
    window : an instance of the app
    widget: the widget in which to display the chosen folder name"""
    filename = widget.text()
    allowed_characters = re.compile(r'^[a-zA-Z0-9_\- µ]*$')
    if not allowed_characters.match(filename):
        show_error_message("Invalid file name. Please use only letters, numbers, underscore, hyphen, space and µ.")
        filename = window.combob_FileName.currentText()
        if widget.objectName() == "le_ResultsCSVFileName":
            widget.setText(get_filename_without_extension(filename)+"_results")
        else:
            now = datetime.now()
            now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
            widget.setText(now_string+"_analysis")

def check_checkboxes(groupbox):
    """Checks if an any checkbox is checked in a widget
    Parameters:
    groupbox: the widget in which checking all the checkboxes
    Return:
    True if any checkbox is checked"""
    for widget in groupbox.findChildren(QCheckBox):
        if widget.isChecked():
            return True
    return False

def show_save_message(message):
    """Displays a QDialog window with a warning message
    Parameters:
    message : the message to display"""
    dialog = QDialog()
    dialog.setWindowTitle("Save successful")
    dialog.setModal(True)
    label = QLabel(message)
    label.setAlignment(Qt.AlignCenter)
    button_ok = QPushButton("OK")
    button_ok.clicked.connect(dialog.accept)
    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(button_ok)
    dialog.setLayout(layout)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
    dialog.show()
    dialog.exec()

def save_results(window :Ui_MainWindow):
    """Save the results in two csv files; a summary and a file with the details of each blob per slice
    Parameters:
    window : an instance of the app"""
    if check_checkboxes(window.gb_ResultsChoice):
        try:
            appMod=window.appMod
            filename = window.combob_FileName.currentText()
            folder = window.lb_ResultsDestinationFolder.text()
            if not folder.endswith("/") and not folder.endswith("\\"):
                folder+="/"
            csv_filename = folder+window.le_ResultsCSVFileName.text()+"_summary.csv"
            csv_filename_per_slice = folder+window.le_ResultsCSVFileName.text()+"_per_slice.csv"
            table_first_row = False
            results = []
            if window.cb_ResultsCount.isChecked():
                results = np.array(appMod.results_count[filename],dtype=str)
                table_first_row = True
            if window.cb_ResultsDensityPercentage.isChecked() or window.cb_ResultsDensityCount.isChecked():
                density_results = np.array(appMod.results_density[filename], dtype=str)
                columns_to_add = set()
                if window.cb_ResultsDensityPercentage.isChecked():
                    columns_to_add.update([1,2,3,4,5,6,7,8,9,18,19,20,21])
                if window.cb_ResultsDensityCount.isChecked():
                    columns_to_add.update([1,2,3,10,11,12,13,14,15,16,17,18,19,20,21])
                columns_to_add = list(columns_to_add)
                if table_first_row == True:
                    results = np.concatenate((results,density_results[:,columns_to_add]),axis=1)
                else:
                    results = density_results[:,0][:, np.newaxis]
                    results = np.concatenate((results,density_results[:,columns_to_add]),axis=1)
                    table_first_row = True
            if window.cb_ResultsDistanceOwnCentroid.isChecked() or window.cb_ResultsDistanceOwnCentroid.isChecked():
                distance_results = np.array(appMod.results_distance[filename],dtype=str)
                columns_to_add = set()
                if window.cb_ResultsDistanceOwnCentroid.isChecked():
                    columns_to_add.update([1,2,3,4,5,6,7,12,13,14])
                if window.cb_ResultsDistanceSpecificCentroid.isChecked():
                    columns_to_add.update([1,2,3,8,9,10,11,12,13,14])
                columns_to_add = list(columns_to_add)
                if table_first_row == True:
                    results = np.concatenate((results,distance_results[:,columns_to_add]),axis=1)
                else:
                    results = distance_results[:,0][:, np.newaxis]
                    results = np.concatenate((results,distance_results[:,columns_to_add]),axis=1)
            np.savetxt(csv_filename,results,delimiter=";",fmt='%s')
            results = []
            if appMod.results_count[filename] is not None: 
                for i, value in enumerate(appMod.contours_main_slice[filename]):
                    if value:
                        main_slice = i
                        break
                for i in range(len(appMod.stacks[filename])):
                    if appMod.included_images[filename][i] and appMod.labeling_coordinates[filename][i] is not None:
                        dots = appMod.labeling_coordinates[filename][i]
                        labels = appMod.labeling_labels[filename][i]
                        centroidsAndSizes = calculate_centroids_sizes(dots,labels)
                        length = len(centroidsAndSizes)
                        if appMod.results_density[filename] is not None or appMod.results_distance[filename] is not None:
                            centroid_y , centroid_x = appMod.contours_centroids[filename][i]
                            DTOC = np.sqrt((centroidsAndSizes[:, 0] - centroid_y) ** 2 + (centroidsAndSizes[:, 1] - centroid_x) ** 2)
                            if appMod.stack_infos[filename][1] is not None and appMod.stack_infos[filename][2] is not None:
                                if appMod.stack_infos[filename][0] is None:
                                    slice_thickness = 0
                                else:
                                    slice_thickness = appMod.stack_infos[filename][0]
                                interslice_space = appMod.stack_infos[filename][1]
                                pixel_size = appMod.stack_infos[filename][2]
                                main_slice_y_coordinate, main_slice_x_coordinate = appMod.contours_centroids[filename][main_slice]
                                main_slice_z_coordinate = round((main_slice * ((slice_thickness+interslice_space) / pixel_size)),1)
                                z_coordinate = round((i * ((slice_thickness+interslice_space) / pixel_size)),1)
                                z_difference_square = (z_coordinate - main_slice_z_coordinate)**2
                                DTCOS = np.sqrt((centroidsAndSizes[:,0]-main_slice_y_coordinate)**2 + (centroidsAndSizes[:,1]-main_slice_x_coordinate)**2 + z_difference_square)
                            else:
                                z_coordinate = f"z{i+1}"
                                DTCOS = None
                        else:
                            DTOC = None
                            DTCOS = None
                        centroidsAndSizes[:,[0,1]]=centroidsAndSizes[:,[1,0]]
                        header = [f"x slice {i+1}",f"y slice {i+1}",f"size slice {i+1}"]
                        if DTOC is not None:
                            DTOC = np.array(DTOC)[:, np.newaxis]
                            centroidsAndSizes = np.concatenate((centroidsAndSizes,DTOC),axis=1)
                            header.append(f"DTOC slice {i+1}")
                        if DTCOS is not None:
                            DTCOS = np.array(DTCOS)[:, np.newaxis]
                            centroidsAndSizes = np.concatenate((centroidsAndSizes,DTCOS),axis=1)
                            z_coordinate_list = [z_coordinate]*length
                            z_coordinate_array = np.array([z_coordinate_list])
                            centroidsAndSizes = np.insert(centroidsAndSizes,2,z_coordinate_array,axis=1)
                            header.insert(2,f"z slice {i+1}")
                            header.append(f"DTCOS{main_slice+1} slice {i+1}")
                        centroidsAndSizes = np.round(centroidsAndSizes,decimals=1)
                        header = np.array([header])
                        centroidsAndSizes = np.vstack((header,centroidsAndSizes))
                        if len(results) == 0:
                            results = centroidsAndSizes
                        else:
                            results = np.array(results)
                            centroidsAndSizes = np.array(centroidsAndSizes)
                            max_rows = max(results.shape[0], centroidsAndSizes.shape[0])
                            results_padded = np.pad(results, ((0, max_rows - results.shape[0]), (0, 0)), mode='constant', constant_values='')
                            centroidsAndSizes_padded = np.pad(centroidsAndSizes, ((0, max_rows - centroidsAndSizes.shape[0]), (0, 0)), mode='constant', constant_values='')
                            results = np.concatenate((results_padded,centroidsAndSizes_padded),axis=1)
                first_column = np.empty(results.shape[0], dtype="str")
                first_column[:] = ""
                title = get_filename(filename)
                results = np.insert(results,0,first_column,axis=1)
                results[0,0] = title
                with open(csv_filename_per_slice, "w", newline='',) as file:
                    writer = csv.writer(file,delimiter=";")
                    for line in results:
                        writer.writerow(line)
                show_save_message(f"The file has been successfully saved in {folder} .")                  
        except (ValueError, TypeError, PermissionError, IndexError) as e:
            show_error_message(f"An error occured while saving the results:\n{e}")
    else:
        show_error_message("Please choose at least one result or image to save.")
    
def open_save_analysis_window(window : Ui_MainWindow):
    """Opens a window to choose the folder and the file name to save an analysis
    Parameters:
    window : an instance of the app"""
    window.save_analysis_window = SaveAnalysisWindow(window)
    window.save_analysis_window.pb_ChooseDestinationFolder.clicked.connect(lambda : select_folder(window.save_analysis_window,window.save_analysis_window.lb_DestinationFolder))
    window.save_analysis_window.lb_DestinationFolder.setText("./analysis/")
    window.save_analysis_window.le_FileName.editingFinished.connect(lambda : check_file_name(window.save_analysis_window,window.save_analysis_window.le_FileName))
    window.save_analysis_window.pb_SaveAnalysis.clicked.connect(lambda : save_analysis(window.save_analysis_window))
    window.save_analysis_window.show()

def save_analysis(window : SaveAnalysisWindow):
    '''Saves the analysis in a file as a joblib object
    Parameters:
    window: an instance of the class SaveAnalysisWindow'''
    window.setCursor(QCursor(Qt.WaitCursor))
    try:
        filename = window.le_FileName.text()
        if filename == "":
            now = datetime.now()
            filename = now.strftime("%Y-%m-%d_%H-%M-%S")
        folder = window.lb_DestinationFolder.text()
        if folder == "":
            folder = "./"
        if not folder.endswith("/") and not folder.endswith("\\"):
            folder+="/"
        appMod = window.main_window.appMod
        dump(appMod,folder+filename+"_analysis.joblib",compress= True)
        show_save_message(f"The analysis has been successfully saved in {folder}.")
        window.close()
    except (AttributeError, FileNotFoundError, PermissionError, TypeError, IOError, KeyError) as e:
        show_error_message(f"An error occured during while saving the analysis:\n{e}")
    window.setCursor(QCursor(Qt.ArrowCursor))

def load_analysis(window : Ui_MainWindow):
    """Load an analysis from a joblib file
    Parameters:
    window : an instance of the app"""
    filename, _ = QFileDialog.getOpenFileName(window,
        "Choose files",
        "./analysis/",
        "Analysis files (*.joblib)"
    )
    if filename:
        window.appMod = load(filename)
        if hasattr(window.appMod, "stacks"):
            if len(window.appMod.stacks) > 0:
                window.appMod.stack_names = list(window.appMod.stacks.keys())
                if window.appMod.stack_names:
                    window.combob_FileName.clear()
                    window.combob_FileName.addItems(window.appMod.stack_names)
                    highlight_groupbox(window,None)
                    window.combob_FileName.setCurrentIndex(0)
                    if window.appMod.included_images[window.appMod.stack_names[0]][0]:
                        window.cb_IncludeImage.setCheckState(Qt.CheckState.Checked)
                    else:
                        window.cb_IncludeImage.setCheckState(Qt.CheckState.Unchecked)
                    set_current_image_options(window,window.appMod.stack_names[0],0)
                    display_original_image(window,window.appMod.stack_names[0],0)
                    update_image_slider_range(window,window.appMod.stack_names[0])
            else:
                window.wi_OriginalText.hide()
                window.wi_Image1Text.hide()
                window.wi_Image2Text.hide()
                window.tabWidget.hide()
                window.gb_ResultsChoice.hide()
                window.wi_Image1Canvas.hide()
                window.wi_Image2Canvas.hide()
                window.wi_OriginalImage.hide()
                window.frame_4.hide()
        else:
            show_error_message("Incorrect file format.")
            window.appMod = AppModel()
            window.wi_OriginalText.hide()
            window.wi_Image1Text.hide()
            window.wi_Image2Text.hide()
            window.tabWidget.hide()
            window.gb_ResultsChoice.hide()
            window.wi_Image1Canvas.hide()
            window.wi_Image2Canvas.hide()
            window.wi_OriginalImage.hide()
            window.frame_4.hide()