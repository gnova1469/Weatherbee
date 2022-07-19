# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 11:07:13 2022

@author: Gnova
"""
import requests
import json
import datetime
import matplotlib
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from urllib.parse import urlencode
from geopy.geocoders import Nominatim
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from MainWindow import Ui_MainWindow

"""
Tasks:
    Add matplotlib canvas to Qt window
    Plot points onto graph
    add API calls for other APIs
    clean up GUI
"""


"""TODO: encrypt this"""
api_key = "0e793179069f4a4bbfe2ea9794424078"

'''Defines the signals available from a working thread'''
class WorkerSignals(QObject):
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(dict)

'''Worker thread for OpenWeatherMapUpdates'''    
class OpenWeatherMapWorker(QRunnable):

    signals = WorkerSignals()
    is_interrupted = False
    
    def __init__(self, location):
        super(OpenWeatherMapWorker, self).__init__()
        self.location = location
    
    @pyqtSlot()
    def run(self):
        try:
            locationCoords = geolocator.geocode(self.location)
            #this string is unholy long
            url = 'http://api.openweathermap.org/data/3.0/onecall?lat='+str(locationCoords.latitude)+'&lon='+str(locationCoords.longitude)+'&appid='+api_key+'&exclude=minutely,hourly,alerts&units=metric'
            r = requests.get(url)
            forecast = json.loads(r.text)
            '''
            maybe store result in a db
            '''
            #print(forecast)
            
            self.signals.result.emit(forecast)
        
        except Exception as e:
            self.signals.error.emit(str(e))
        
        self.signals.finished.emit()

'''GUI'''
class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.setupUi(self)
        self.pushButton.pressed.connect(self.update_openweather)
        self.threadpool = QThreadPool()
        self.show()
        
    '''alert message'''    
    def alert(self, message):
        alert = QMessageBox.warning(self, "Error", message)
    
    '''get the weather data'''
    def update_openweather(self):
        worker = OpenWeatherMapWorker(self.lineEdit.text())
        worker.signals.result.connect(self.post_results)
        worker.signals.error.connect(self.alert)
        self.threadpool.start(worker)
        
    '''update the gui with data'''
    def post_results(self, forecast):
        forecast_list = self.parse_forecast(forecast)
        self.update_OWMlabels(forecast_list)
        sc.axes.plot(forecast_list[0],forecast_list[1])
    
    '''updates labels'''
    def update_OWMlabels(self, forecast_list):
        #zzz - too lazy to rename labels
        self.label_2.setText(forecast_list[0][0])
        self.label_3.setText(forecast_list[1][0])
        self.label_4.setText(forecast_list[2][0])
        self.label_5.setText(forecast_list[3][0])
        self.label_6.setText(forecast_list[4][0])
        self.label_7.setText(forecast_list[5][0])
        self.label_8.setText(forecast_list[6][0])
        self.label_11.setText(forecast_list[0][1])
        self.label_12.setText(forecast_list[1][1])
        self.label_13.setText(forecast_list[2][1])
        self.label_14.setText(forecast_list[3][1])
        self.label_15.setText(forecast_list[4][1])
        self.label_16.setText(forecast_list[5][1])
        self.label_17.setText(forecast_list[6][1])
            
    '''parse the data so its useful'''
    def parse_forecast(self, forecast):
        forecast_list = list()
        for day in forecast['daily']:
            '''
            gets a tuple of date and day temp
            '''
            forecast_list.append((self.convert_timestamp(day['dt']), str(day['temp']['day'])))
        return forecast_list

    '''get date from unix timestamp'''  
    def convert_timestamp(self,unix):
        dmy = datetime.date.fromtimestamp(unix)
        dm = dmy.strftime('%d/%y')
        return dm
 
'''matplotlib canvas'''
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


if __name__ == '__main__':
    geolocator = Nominatim(user_agent="MyApp")
    app = QApplication([])
    window = MainWindow()
    app.exec_()