from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt, QObject, Signal
import sys
import threading
import cv2

app = QApplication(sys.argv)

with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())

class WebcamFeed(QObject):
    frame_ready = Signal(object)
    def __init__(self):
        super().__init__()
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Controls how many frames OpenCV buffers (stores in memory)
        self.running = True
        thread = threading.Thread(target=self.update_frame, daemon=True)
        thread.start()  

    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
                self.frame_ready.emit(frame)
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encounter Tracker")
        self.webcam_stream = WebcamFeed()
        
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_container.setLayout(main_layout)

        # Header
        header_widget = QWidget()          
        header_widget.setMaximumHeight(80)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(4)
        header_widget.setLayout(header_layout)
        header_layout.setAlignment(Qt.AlignLeft)
        header_widget.setProperty("class", "container")
        header_widget.setStyleSheet("border: 1px solid red;")
        header_heading = QLabel("Encounter Tracker") # Header label
        header_heading.setProperty("class", "header")
        header_icon = QLabel() # Header icon
        header_icon.setProperty("class", "header")
        header_icon.setPixmap(QIcon("icons/sparkle.svg").pixmap(32, 32))
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_heading)

        # Live feed (left) and statistics (right)
        feed_and_stats_widget = QWidget()
        feed_and_stats_layout = QHBoxLayout()
        feed_and_stats_layout.setContentsMargins(0, 0, 0, 0)
        feed_and_stats_widget.setStyleSheet("border: 1px solid blue;")
        feed_and_stats_widget.setLayout(feed_and_stats_layout)

        # Live feed
        live_feed_widget = QWidget()
        live_feed_widget.setProperty("class", "container")
        live_feed_layout = QVBoxLayout()
        live_feed_layout.setAlignment(Qt.AlignTop)
        live_feed_header = QLabel("Live Feed")
        live_feed_header.setProperty("class", "header")
        live_feed_layout.addWidget(live_feed_header)

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(True)
        print(self.video_label.size())
        live_feed_layout.addWidget(self.video_label)
        live_feed_widget.setLayout(live_feed_layout)

        # Statistics
        statistics_widget = QWidget()
        statistics_widget.setProperty("class", "container")
        statistics_layout = QVBoxLayout()
        statistics_layout.setAlignment(Qt.AlignTop)
        statistics_header = QLabel("Statistics")
        statistics_header.setProperty("class", "header")
        statistics_layout.addWidget(statistics_header)
        statistics_widget.setLayout(statistics_layout)


        feed_and_stats_layout.addWidget(live_feed_widget)
        feed_and_stats_layout.addWidget(statistics_widget)

        main_layout.addWidget(header_widget)
        main_layout.addWidget(feed_and_stats_widget)

        self.webcam_stream.frame_ready.connect(self.update_video_feed)
        self.webcam_stream.start()

    def update_video_feed(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        #print(h, w, ch)
        bytes_per_line = ch * w # 3 colors (1 byte each) * width for RGB
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888) 
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation)
        self.video_label.setPixmap(scaled_pixmap)
        #print(self.video_label.size())
window = MainWindow()
window.show()


app.exec()