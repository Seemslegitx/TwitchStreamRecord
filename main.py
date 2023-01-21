from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
import PyQt5.QtCore

from streamlink import Streamlink
import os
import qdarktheme
import threading
import time
import subprocess
class StreamDownloader(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Streamlink Downloader")
        width = 600
         
        # setting  the fixed width of window
        self.setFixedWidth(width)
        self.statusbar = self.statusBar()
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setText("https://www.twitch.tv/shroud")
        self.url_input.setPlaceholderText("Enter the stream URL")
        
        self.download_button = QtWidgets.QPushButton("Download", self)
        self.download_button.clicked.connect(self.start_download)
        self.stop_button = QtWidgets.QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setEnabled(False)
        
        
        self.log_area = QtWidgets.QTextEdit(self)
        self.log_area.setReadOnly(True)
        

        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.log_area)

        
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.download_thread = None
        self.download_event = threading.Event()
        self.download_url = None
        self.download_speed = 0
        
    def start_download(self):
        self.download_event.clear()
        self.download_url = self.url_input.text()
        self.download_thread = threading.Thread(target=self.download, args=(self.download_event,))
        self.download_thread.start()
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Add a new row to the download table

        
    def stop_download(self):
        self.download_event.set()
        self.download_thread.join()
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().setStyleSheet("color: red; font-size: 11px;")
        self.statusBar().showMessage("Stopped download of {}".format(self.download_url))
    def download(self, event):
        url = self.url_input.text()
        try:
            session = Streamlink()
            session.set_option("--twitch-disable-ads", True)
            session.set_option("--debug-level", "all")
            streams_ = session.streams(url)
        except Streamlink.exceptions.StreamlinkError as e:
            self.log_area.append("Invalid URL or stream not found: {}".format(e))
            return
        try:
            stream = streams_["best"]
        except KeyError:
            self.log_area.append("720p quality stream not found")
            return
        filename = os.path.basename(url) + ".mp4"
        self.log_area.append("Starting download of {}".format(url))
        start_time = time.time()
        self.statusBar().setStyleSheet("color: green; font-size: 11px;")
        bytes_read = 0
        with stream.open() as f:
            with open(filename, 'wb') as out_file:
                while True:
                    if event.is_set():
                        self.log_area.append("Download cancelled by user.")
                        return
                    data = f.read(1024)
                    if not data:
                        break
                    out_file.write(data)
                    bytes_read += len(data)
                    
                    # Update the speed in the download table
                    elapsed_time = time.time() - start_time
                    self.download_speed = (bytes_read / elapsed_time) / (1024 * 1024)
                    self.statusBar().showMessage("Downloading... Speed: {:.2f} Mbit/s".format(self.download_speed))
                    
        self.log_area.append("Download of {} completed!".format(self.download_url))
        self.download_button.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    qdarktheme.setup_theme("dark")
    window = StreamDownloader()
    window.show()
    app.exec_()
