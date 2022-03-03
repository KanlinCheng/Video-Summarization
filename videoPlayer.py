from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import playerUI
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import imageProcessTool as readrgb
import time
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import traceback, sys
import json
import os
import sys

class Img_Thread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, fn):
        QThread.__init__(self)
        self.fn = fn
        self.n = 0
        self.kill = 0

    def run(self):
        for i in range(self.n):
            #print("i= "+str(i))
            if self.kill == 1:
                break
            try:
                self.fn()
            except Exception as e:
                print(e)
                continue
            if i == self.n-1:
                self.signal.emit(0)
            #self.msleep(32)

class MyQtApp(playerUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Multimedia Project")

        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.play_button.setEnabled(False)
        # self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        
        #read metadata
        # file_meta = open('result.json',"r")
        # file_meta = open('soccer_origin.json', "r")
        file_meta = open(sys.argv[1], "r")
        self.metadata = json.load(file_meta)
        self.num_img = len(self.metadata)
        file_meta.close()

        
        self.synopsis.mousePressEvent = self.getPos
        # self.getPos
        
        self.sound = QVideoWidget()
        self.sound.setGeometry(QtCore.QRect(859, 10, 111, 21))
        self.sound.setObjectName("sound")

        self.soundPlayer = QMediaPlayer(None, QMediaPlayer.LowLatency)
        self.soundPlayer.setAudioRole(2)

        self.v_thread = Img_Thread(self.updateframe)
        self.v_thread.signal.connect(self.stop)
        self.v_thread.n = 0
        self.v_thread.start()

        self.sound_delay = 0.3
        
       
    def play(self):
        #print("play")
        #if self.soundPlayer.state() != QMediaPlayer.PlayingState:
        #print(self.soundPlayer.position()/1000)
        #time.sleep(0.05)
        #print(self.v_thread.isFinished())
        self.thistimestart_frame = self.current_frame -1
        self.soundPlayer.play()
        time.sleep(self.sound_delay) # wait for the sound track to play
        # while self.soundPlayer.position() <= 1:
        #     pass
        self.tic = time.perf_counter()
        self.image_thread()
        #self.soundPlayer.play()
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        # self.stop_btn.setEnabled(True)


    def stop(self):
        if self.soundPlayer.state() != QMediaPlayer.StoppedState:
            self.soundPlayer.stop()
        self.v_thread.kill = 1

    def updateframe(self):
        #print(self.current_frame)
        fileName = "frame"+str(self.current_frame)+".rgb"
        video = readrgb.readrgbtoQImage(self.folderName+fileName)
        pixmap_vdo = QPixmap.fromImage(video)
        ontime = (self.current_frame - self.thistimestart_frame )/30
        delay = time.perf_counter() - self.tic
        if delay < ontime:
            #if (ontime-delay) > 0.033:
            #    print("long wait", ontime-delay)
            time.sleep(ontime - delay)
        else:
            print("too late", delay-ontime)
            
        
        self.video.setPixmap(pixmap_vdo)
        #print(self.current_frame)
        self.current_frame += 1
        
    def image_thread(self):
        self.v_thread.n = self.end_frame - self.current_frame +1
        self.v_thread.kill = 0
        self.v_thread.start()

    def pause(self):
        #print("pause")

        #if self.soundPlayer.state() == QMediaPlayer.PlayingState:
        self.soundPlayer.pause()
        self.v_thread.kill = 1
        
        time.sleep(0.04)
        #print(self.v_thread.isFinished())
        print(self.current_frame)
        self.current_frame = self.soundPlayer.position()*30//1000
        print(self.current_frame)

        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        
   

    def play_video(self):
        self.current_frame = self.start_frame
        self.soundPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.audio_file)))) # mac
        # self.soundPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))
        self.soundPlayer.setPosition(self.start_time)
        fileName = "frame"+str(self.start_frame)+".rgb"
        video = readrgb.readrgbtoQImage(self.folderName+fileName)
        pixmap_vdo = QPixmap.fromImage(video)
        
        self.video.setPixmap(pixmap_vdo)
        self.Displaying.setText("Displaying Video: " + self.folderName)
        self.current_frame += 1
        self.play()

    def getfiles(self, idx):
        #print(idx)
        if idx >= self.num_img:
            idx = self.num_img-1
        tp = self.metadata[idx]["type"] 
        if tp == 1:
            # for video
            self.folderName = self.metadata[idx]["video"] 
            self.start_frame = self.metadata[idx]["start"] 
            print("start frame", self.start_frame)
            self.end_frame = self.metadata[self.num_img-1]["end"] 
            print("end frame", self.end_frame)
            self.start_time = self.start_frame/30*1000
            print("start_time",self.start_time)
            self.audio_file = self.metadata[idx]["audio"] 

        else:
            # for image
            self.fileName = self.metadata[idx]["path"] 
        return tp 

    def getPos(self, event):
        x = event.pos().x()
        tp = self.getfiles(x//180) # x//(width of an image = 180)
        if self.soundPlayer.state() == QMediaPlayer.PlayingState:
            self.v_thread.kill = 1
            time.sleep(0.04) # for racing
        if tp:
            self.play_video()
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    qt_app = MyQtApp()
    qt_app.show()
    sys.exit(app.exec_())

