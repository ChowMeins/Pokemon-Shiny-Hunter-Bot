from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QPushButton, QDialog, QListWidget, QListWidgetItem, QMessageBox, QSizePolicy
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt, QObject, Signal
import serial
import serial.tools.list_ports
import sys
import threading
import cv2

class PortSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Arduino Port")
        self.selected_port = None
        self.serial_connection = None
        self.port_list = QListWidget()
        self.port_list.setFocusPolicy(Qt.NoFocus) # removes white border when selected
        self.port_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.port_list.setContentsMargins(0, 0, 0, 0)
        self.port_list.setStyleSheet("""
                                     QListWidget {
                                        padding: 0px; 
                                        margin: 0px; 
                                        border: 2px solid red;
                                        background-color: rgb(31, 41, 55);
                                     }
                                     QListWidget::item {
                                        padding: 4px;
                                        margin: 0px;
                                        border: none;
                                        outline: none; 
                                     }
                                     QListWidget::item:selected {
                                        background-color: rgb(75, 85, 99);
                                        border: none;
                                        outline: none; 
                                     }
                                     """)
        self.port_list
        self.initialize_list_ports()

        title = QLabel("Select Available Ports")
        title.setStyleSheet("font-size: 18px; font-weight: bold")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        label = QLabel("Available Ports:")
        connect_button = QPushButton("Connect")
        connect_button.setStyleSheet("padding: 6px; font-weight: bold; background-color: green")
        connect_button.clicked.connect(self.connect_to_port)

        layout.addWidget(title)
        layout.addWidget(label)
        layout.addWidget(self.port_list, stretch=0)
        layout.addStretch()
        layout.addWidget(connect_button)

        self.setLayout(layout)
        self.resize(400, 300)

    def initialize_list_ports(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_list.addItem(f"{port.device}-{port.description}")
        self.port_list.clearSelection()

    def connect_to_port(self):
        current_item = self.port_list.currentItem()
        print(current_item.text())
        if not current_item or not self.port_list.selectedItems() or current_item.text() == "No ports found":
            QMessageBox.warning(self, "No Selection", "Please select a port")
            return
        
        port_name = current_item.text().split('-')[0]
        try:
            self.serial_connection = serial.Serial(port_name, 9600, timeout=1)
            self.selected_port = port_name
            
            QMessageBox.information(self, "Success", f"Connected to {port_name}")
            self.accept()  # Close dialog with success
            
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")

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
        header_heading = QLabel("Encounter Tracker") # Header label
        header_heading.setProperty("class", "header")
        header_icon = QLabel() # Header icon
        header_icon.setProperty("class", "header")
        header_icon.setPixmap(QIcon("icons/sparkle.svg").pixmap(32, 32))
        connect_arduino_button = QPushButton("Connect Arduino")
        connect_arduino_button.setStyleSheet("padding: 6px;font-weight: bold; background-color: green")
        connect_arduino_button.clicked.connect(self.open_port_dialog)
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_heading)
        header_layout.addStretch()
        header_layout.addWidget(connect_arduino_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Live feed (left) and statistics (right)
        feed_and_stats_widget = QWidget()
        feed_and_stats_layout = QHBoxLayout()
        feed_and_stats_layout.setContentsMargins(0, 0, 0, 0)
        feed_and_stats_widget.setLayout(feed_and_stats_layout)

        # Live feed
        live_feed_widget = QWidget()
        live_feed_widget.setProperty("class", "container")
        live_feed_layout = QVBoxLayout()
        live_feed_layout.setAlignment(Qt.AlignTop)
        live_feed_header = QLabel("Live Feed")
        live_feed_header.setProperty("class", "header")
        live_feed_layout.addWidget(live_feed_header)

        # Webcam Feed
        self.webcam_container = QWidget()
        self.webcam_container_layout = QStackedLayout()
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(True)
        live_feed_layout.addWidget(self.video_label)
        live_feed_widget.setLayout(live_feed_layout)

        # Crop buttons
        crop_region_widget = QWidget()
        crop_region_widget.setProperty("class", "container")
        crop_region_layout = QHBoxLayout()
        crop_region_layout.setContentsMargins(0, 0, 0, 0)
        crop_region_layout.setSpacing(10)
        set_crop_region_button = QPushButton("Set Crop Region")
        set_crop_region_button.setMinimumHeight(24)
        set_crop_region_button.setStyleSheet("font-weight: bold; background-color: blue")
        reset_crop_button = QPushButton("Reset Crop")
        reset_crop_button.setMinimumHeight(24)
        reset_crop_button.setStyleSheet("font-weight: bold; background-color: #888888")
        crop_region_layout.addWidget(set_crop_region_button)
        crop_region_layout.addWidget(reset_crop_button)
        crop_region_widget.setLayout(crop_region_layout)
        live_feed_layout.addWidget(crop_region_widget)

        # Statistics 
        statistics_widget = QWidget()
        statistics_widget.setProperty("class", "container")
        statistics_layout = QVBoxLayout()
        statistics_layout.setAlignment(Qt.AlignTop)
        statistics_header = QLabel("Statistics")
        statistics_header.setProperty("class", "header")
        statistics_layout.addWidget(statistics_header)

        # Encounter box (1st row of statistics)
        encounter_box = QWidget()
        encounter_box_layout = QVBoxLayout()
        encounter_header = QLabel("Total Encounters")
        encounter_header.setStyleSheet("font-size: 12px; color: #AAAAAA")
        encounter_count_label = QLabel("0")
        encounter_count_label.setStyleSheet("font-size: 24px; color: rgb(96, 165, 250); font-weight: bold;")
        encounter_box_layout.addWidget(encounter_header)
        encounter_box_layout.addWidget(encounter_count_label)
        encounter_box.setLayout(encounter_box_layout)

        # Total Time Elapsed
        time_elapsed_box = QWidget()
        time_elapsed_box_layout = QVBoxLayout()
        time_elapsed_header = QLabel("Time Elapsed")
        time_elapsed_header.setStyleSheet("font-size: 12px; color: #AAAAAA")
        time_elapsed_count_label = QLabel("0 minutes ago")
        time_elapsed_count_label.setStyleSheet("font-size: 16px; color: rgb(96, 165, 250); font-weight: bold;")
        time_elapsed_box_layout.addWidget(time_elapsed_header)
        time_elapsed_box_layout.addWidget(time_elapsed_count_label)
        time_elapsed_box.setLayout(time_elapsed_box_layout)

        statistics_layout.addWidget(encounter_box)
        statistics_layout.addWidget(time_elapsed_box)
        statistics_widget.setLayout(statistics_layout)
        
        feed_and_stats_layout.addWidget(live_feed_widget)
        feed_and_stats_layout.addWidget(statistics_widget)

        main_layout.addWidget(header_widget)
        main_layout.addWidget(feed_and_stats_widget)

        self.webcam_stream.frame_ready.connect(self.update_video_feed)
        self.webcam_stream.start()

    def open_port_dialog(self):
        dialog = PortSelectionDialog()
        dialog.exec()

    def update_video_feed(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        #print(h, w, ch)
        bytes_per_line = ch * w # 3 colors (1 byte each) * width for RGB
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888) 
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)
        #print(self.video_label.size())
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    app.exec()