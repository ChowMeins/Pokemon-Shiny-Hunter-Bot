from enum import Enum
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QPushButton, QDialog, QListWidget, QListWidgetItem, QMessageBox, QSizePolicy, QComboBox, QSpinBox
from PySide6.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen
from PySide6.QtCore import Qt, QObject, QThread, Signal, QRect, QPoint, QPointF, QSize
import serial
import serial.tools.list_ports
import sys
import threading
import cv2
from arduino_controller import ArduinoController

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
                self.frame_ready.emit(frame) # Emit signal for frame updated in webcam feed (runs update_video_feed)


class Drag(Enum):
    NONE = 0
    MOVE = 1
    RESIZE_TL = 2  # Top-left corner
    RESIZE_TR = 3  # Top-right corner
    RESIZE_BL = 4  # Bottom-left corner
    RESIZE_BR = 5  # Bottom-right corner
    RESIZE_T = 6   # Top edge
    RESIZE_B = 7   # Bottom edge
    RESIZE_L = 8   # Left edge
    RESIZE_R = 9   # Right edge
    NEW_REGION = 10  # Creating a new region


class VideoWithCropOverlay(QLabel):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.resize(640, 480)
        self.top_left_corner = QPointF(self.size().width() * 0.1, self.size().height() * 0.1)
        self.crop_region = QRect(self.top_left_corner.toPoint(), QSize(self.size().width() - self.top_left_corner.x() * 2, self.size().height() - self.top_left_corner.y() * 2))
        self.top_right_corner = self.crop_region.topRight()
        self.bottom_left_corner = self.crop_region.bottomLeft()
        self.bottom_right_corner = self.crop_region.bottomRight().toPointF()
        # For creating new crop region
        self.start_point = None
        self.end_point = None

        self.video_feed = QLabel()
        self.dragging = False
        self.drag_mode = Drag.NONE
        # Handles for diagonally resizing crop region
        self.handle_size = QSize(8, 8)
        self.top_left_handle = QRect(QPoint(self.top_left_corner.toPoint() - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        self.top_right_handle = QRect(QPoint(self.top_right_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        self.bottom_left_handle = QRect(QPoint(self.bottom_left_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        self.bottom_right_handle = QRect(QPoint(self.bottom_right_corner.toPoint() - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        # Edges for vertically/horizontally resizing crop region
        self.top_edge = QRect(self.top_left_handle.topRight(), self.top_right_handle.bottomLeft())
        self.bottom_edge = QRect(self.bottom_left_handle.topRight(), self.bottom_right_handle.bottomLeft())
        self.left_edge = QRect(self.top_left_handle.bottomLeft(), self.bottom_left_handle.topRight())
        self.right_edge = QRect(self.top_right_handle.bottomLeft(), self.bottom_right_handle.topRight())

    def get_drag_mode(self, pos):
        if self.crop_region is None or self.crop_region.isNull():
            return Drag.NONE
        if self.top_left_handle.contains(pos): 
            print("Top-left handle clicked")
            return Drag.RESIZE_TL
        elif self.top_right_handle.contains(pos):
            print("Top-right handle clicked")
            return Drag.RESIZE_TR
        elif self.bottom_left_handle.contains(pos):
            print("Bottom-left handle clicked")
            return Drag.RESIZE_BL
        elif self.bottom_right_handle.contains(pos):
            print("Bottom-right handle clicked")
            return Drag.RESIZE_BR
        elif self.top_edge.contains(pos):
            print("Top edge clicked")
            return Drag.RESIZE_T
        elif self.bottom_edge.contains(pos):
            print("Bottom edge clicked")
            return Drag.RESIZE_B
        elif self.left_edge.contains(pos):
            print("Left edge clicked")
            return Drag.RESIZE_L
        elif self.right_edge.contains(pos):
            print("Right edge clicked")
            return Drag.RESIZE_R
        elif self.crop_region.contains(pos):
            print("Inside crop region")
            return Drag.MOVE
        print("Creating new region")
        return Drag.NEW_REGION
    
    def mousePressEvent(self, event):
        mouse_pos = event.position()
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_mode = self.get_drag_mode(mouse_pos.toPoint())
            if self.drag_mode == Drag.NEW_REGION:
                self.start_point = mouse_pos
                self.end_point = mouse_pos
            elif self.drag_mode == Drag.MOVE:
                self.move_start_point = mouse_pos
            self.update_handles_and_edges()
            self.update()

    def mouseMoveEvent(self, event):
        mouse_pos = event.position()
        mouse_pos_rounded = mouse_pos.toPoint()
        # Set cursor type based on hover location
        if self.drag_mode == Drag.NEW_REGION:
            self.setCursor(Qt.CrossCursor)
        elif self.top_left_handle.contains(mouse_pos_rounded) or self.bottom_right_handle.contains(mouse_pos_rounded):
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.top_right_handle.contains(mouse_pos_rounded) or self.bottom_left_handle.contains(mouse_pos_rounded):
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.top_edge.contains(mouse_pos_rounded) or self.bottom_edge.contains(mouse_pos_rounded):
            self.setCursor(Qt.SizeVerCursor)
        elif self.left_edge.contains(mouse_pos_rounded) or self.right_edge.contains(mouse_pos_rounded):
            self.setCursor(Qt.SizeHorCursor)
        elif self.crop_region.contains(mouse_pos_rounded):
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        if self.dragging:
            # Create new crop region
            if self.drag_mode == Drag.NEW_REGION:
                self.end_point = mouse_pos
            # Resizing corners
            elif self.drag_mode == Drag.RESIZE_TL:
                self.top_left_corner = mouse_pos
            elif self.drag_mode == Drag.RESIZE_TR:
                self.top_left_corner.setY(mouse_pos.y())
                self.bottom_right_corner.setX(mouse_pos.x())
            elif self.drag_mode == Drag.RESIZE_BL:
                self.top_left_corner.setX(mouse_pos.x())
                self.bottom_right_corner.setY(mouse_pos.y())
            elif self.drag_mode == Drag.RESIZE_BR:
                self.bottom_right_corner = mouse_pos
            # Resizing edges
            elif self.drag_mode == Drag.RESIZE_T:
                self.top_left_corner.setY(mouse_pos.y())
            elif self.drag_mode == Drag.RESIZE_B:
                self.bottom_right_corner.setY(mouse_pos.y())
            elif self.drag_mode == Drag.RESIZE_L:
                self.top_left_corner.setX(mouse_pos.x())
            elif self.drag_mode == Drag.RESIZE_R:
                self.bottom_right_corner.setX(mouse_pos.x())
            # Moving crop region
            elif self.drag_mode == Drag.MOVE:
                delta = mouse_pos - self.move_start_point
                self.top_left_corner += delta
                self.bottom_right_corner += delta
                self.move_start_point = mouse_pos
            # Check for out-of-bounds and adjust
            if mouse_pos.x() > self.width():
                self.bottom_right_corner.setX(self.width())
            if mouse_pos.y() > self.height():
                self.bottom_right_corner.setY(self.height())
            if mouse_pos.x() < 0:
                self.top_left_corner.setX(0)
            if mouse_pos.y() < 0:
                self.top_left_corner.setY(0)

            if self.start_point and self.end_point:
                self.top_left_corner = QPointF(min(self.start_point.x(), self.end_point.x()), min(self.start_point.y(), self.end_point.y()))
                self.bottom_right_corner = QPointF(max(self.start_point.x(), self.end_point.x()), max(self.start_point.y(), self.end_point.y()))

            self.crop_region = QRect(self.top_left_corner.toPoint(), self.bottom_right_corner.toPoint())
            self.update_handles_and_edges()
            self.update()

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_mode = Drag.NONE
            if self.start_point and self.end_point:
                self.top_left_corner = QPoint(min(self.start_point.x(), self.end_point.x()), min(self.start_point.y(), self.end_point.y()))
                self.bottom_right_corner = QPoint(max(self.start_point.x(), self.end_point.x()), max(self.start_point.y(), self.end_point.y()))
                self.start_point = None
                self.end_point = None
            self.crop_region = QRect(self.top_left_corner.toPoint(), self.bottom_right_corner.toPoint())
            self.update_handles_and_edges()
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        old_size = event.oldSize()
        new_size = event.size()
        print(f"Resized from {old_size} to {new_size}")
        
        # Use DIVISION for ratio, not subtraction
        x_ratio = new_size.width() / old_size.width() if old_size.width() > 0 else 1
        y_ratio = new_size.height() / old_size.height() if old_size.height() > 0 else 1
        
        if self.crop_region:
            # MULTIPLY coordinates by ratio, don't add delta
            self.top_left_corner = QPointF(self.top_left_corner.x() * x_ratio, self.top_left_corner.y() * y_ratio)
            self.bottom_right_corner = QPointF(self.bottom_right_corner.x() * x_ratio, self.bottom_right_corner.y() * y_ratio)
            self.crop_region = QRect(self.top_left_corner.toPoint(), self.bottom_right_corner.toPoint())
            self.update_handles_and_edges()

    def update_handles_and_edges(self):
        if self.crop_region:
            # top left corner is smallest tuple, bottom right is largest. top right is 2 away from top left, bottom left is 2 away from bottom right in the list
            self.top_right_corner = QPointF(self.bottom_right_corner.x(), self.top_left_corner.y())
            self.bottom_left_corner = QPointF(self.top_left_corner.x(), self.bottom_right_corner.y())
            #print(corners)
            #print(tl_corner, tr_corner, bl_corner, br_corner)
            self.top_left_handle = QRect(self.top_left_corner.toPoint() - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            self.top_right_handle = QRect(self.top_right_corner.toPoint() - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            self.bottom_left_handle = QRect(self.bottom_left_corner.toPoint() - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            self.bottom_right_handle = QRect(self.bottom_right_corner.toPoint() - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            
            self.top_edge = QRect(self.top_left_handle.topRight(), self.top_right_handle.bottomLeft())
            self.bottom_edge = QRect(self.bottom_left_handle.topRight(), self.bottom_right_handle.bottomLeft())
            self.left_edge = QRect(self.top_left_handle.bottomLeft(), self.bottom_left_handle.topRight())
            self.right_edge = QRect(self.top_right_handle.bottomLeft(), self.bottom_right_handle.topRight())
            
    def reset_crop_region(self):
        self.top_left_corner = QPointF(self.size().width() * 0.1, self.size().height() * 0.1)
        self.crop_region = QRect(self.top_left_corner.toPoint(), QSize(self.size().width() - self.top_left_corner.x() * 2, self.size().height() - self.top_left_corner.y() * 2))
        self.top_right_corner = self.crop_region.topRight()
        self.bottom_left_corner = self.crop_region.bottomLeft()
        self.bottom_right_corner = self.crop_region.bottomRight().toPointF()
        self.update_handles_and_edges()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.crop_region:
            painter = QPainter(self)
            pen = QPen(QColor(52, 235, 137), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.crop_region)
            pen = QPen(QColor(255, 0, 0), 1)
            painter.setPen(pen)
            # Draw edges
            painter.drawRect(self.top_edge)
            painter.drawRect(self.bottom_edge)
            painter.drawRect(self.left_edge)
            painter.drawRect(self.right_edge)
            # Draw handles
            painter.fillRect(self.top_left_handle, QColor(52, 235, 137))
            painter.fillRect(self.top_right_handle, QColor(52, 235, 137))
            painter.fillRect(self.bottom_left_handle, QColor(52, 235, 137))
            painter.fillRect(self.bottom_right_handle, QColor(52, 235, 137))

class ArduinoConnectionThread(QThread):
    connected = Signal(object)  # Success: sends ArduinoController
    failed = Signal(str)  # Failure: sends error message
    
    def __init__(self, port):
        super().__init__()
        self.port = port
    
    def run(self):
        try:
            controller = ArduinoController(port=self.port)
            self.connected.emit(controller)
        except serial.SerialException as e:
            self.failed.emit(str(e))
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encounter Tracker")
        self.webcam_stream = WebcamFeed()
        self.arduino_controller = None
        
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_container.setLayout(main_layout)

        # Header
        header_widget = QWidget()          
        header_widget.setMaximumHeight(80)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        header_widget.setLayout(header_layout)
        header_layout.setAlignment(Qt.AlignLeft)
        header_widget.setProperty("class", "container")
        header_heading = QLabel("Encounter Tracker") # Header label
        header_heading.setProperty("class", "header")
        header_icon = QLabel() # Header icon
        header_icon.setProperty("class", "header")
        header_icon.setPixmap(QIcon("icons/sparkle.svg").pixmap(32, 32))
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #dc3545; font-size: 18px; background-color: transparent;")
        self.connection_state_label = QLabel("Not Connected")
        self.connection_state_label.setStyleSheet("font-size: 14px; padding: 6px; border-radius: none; font-weight: bold; background-color: rgb(17, 24, 39); border: 1px solid rgb(31, 41, 55); color: white;")

        com_combobox = QComboBox()
        com_combobox.setMinimumWidth(100)
        com_combobox.setStyleSheet("font-size: 14px; padding: 6px; border-radius: none; font-weight: bold; background-color: rgb(17, 24, 39); color: white")
        serial_ports = serial.tools.list_ports.comports()
        for port in serial_ports:
            com_combobox.addItem(f"{port.device}")
        self.connect_arduino_button = QPushButton("Connect")
        self.connect_arduino_button.setMinimumWidth(100)
        self.connect_arduino_button.setStyleSheet("font-size: 14px; padding: 6px 3px;font-weight: bold; background-color: green")
        self.connect_arduino_button.clicked.connect(lambda: self.connect_arduino(com_combobox.currentText()))
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_heading)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.connection_state_label)
        header_layout.addWidget(com_combobox)
        header_layout.addWidget(self.connect_arduino_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Live feed (left) and statistics (right)
        feed_and_stats_widget = QWidget()
        feed_and_stats_layout = QHBoxLayout()
        feed_and_stats_layout.setContentsMargins(0, 0, 0, 0)
        feed_and_stats_widget.setLayout(feed_and_stats_layout)

        # Live feed
        live_feed_widget = QWidget()
        live_feed_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        live_feed_widget.setProperty("class", "container")
        live_feed_layout = QVBoxLayout()
        live_feed_layout.setAlignment(Qt.AlignTop)
        live_feed_header = QLabel("LIVE FEED")
        live_feed_header.setStyleSheet("font-size: 14px; color: #AAAAAA; font-weight: 600;")
        live_feed_header.setProperty("class", "header")
        live_feed_layout.addWidget(live_feed_header)
        live_feed_widget.setLayout(live_feed_layout)

        # Webcam Feed
        self.webcam_container = QWidget()
        self.webcam_container_layout = QVBoxLayout()
        self.webcam_container_layout.setAlignment(Qt.AlignTop)
        self.video_feed = VideoWithCropOverlay()
        self.video_feed.setScaledContents(True)
        self.video_feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webcam_container_layout.addWidget(self.video_feed)
        self.webcam_container.setLayout(self.webcam_container_layout)
        live_feed_layout.addWidget(self.webcam_container)

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
        reset_crop_button.clicked.connect(self.video_feed.reset_crop_region)
        crop_region_layout.addWidget(set_crop_region_button)
        crop_region_layout.addWidget(reset_crop_button)
        crop_region_widget.setLayout(crop_region_layout)
        live_feed_layout.addWidget(crop_region_widget)

        # Statistics 
        statistics_widget = QWidget()
        statistics_widget.setMinimumWidth(400)
        statistics_widget.setProperty("class", "container")
        statistics_layout = QVBoxLayout()
        statistics_layout.setAlignment(Qt.AlignTop)
        statistics_header = QLabel("STATISTICS")
        statistics_header.setStyleSheet("font-size: 14px; color: #AAAAAA; font-weight: 600;")
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

        # Hunt combobox + Start Tracking button
        hunt_and_start_container = QWidget()
        #hunt_and_start_container.setMinimumHeight(60)
        hunt_and_start_container.setLayout(QVBoxLayout())
        self.hunt_selection_combobox = QComboBox()
        self.hunt_selection_combobox.addItem("HGSS Random Encounters")
        self.hunt_selection_combobox.addItem("Other Hunt Type")
        self.hunt_selection_combobox.currentIndexChanged.connect(self.on_hunt_change)
        self.hunt_selection_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tile_count_box = QWidget()
        self.tile_count_box_layout = QHBoxLayout()
        self.tile_count_box_layout.setSpacing(4)
        tile_count_label = QLabel("Tile Count:")
        tile_count_label.setStyleSheet("font-size: 12px; font-weight: 600;")
        self.tile_count_spinbox = QSpinBox()
        self.tile_count_spinbox.setValue(5)
        self.tile_count_box_layout.addWidget(tile_count_label)
        self.tile_count_box_layout.addWidget(self.tile_count_spinbox, stretch=1)
        self.tile_count_box.setLayout(self.tile_count_box_layout)

        start_tracking_button = QPushButton("Start Hunt")
        start_tracking_button.setMinimumHeight(32)
        start_tracking_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        start_tracking_button.setStyleSheet("font-weight: bold; background-color: green")
        start_tracking_button.clicked.connect(lambda: self.start_hunt(self.hunt_selection_combobox.currentText().lower().replace(" ", "_"), self.tile_count_spinbox.value()))
        hunt_and_start_container.layout().addWidget(self.hunt_selection_combobox)
        hunt_and_start_container.layout().addWidget(self.tile_count_box)
        hunt_and_start_container.layout().addWidget(start_tracking_button)

        statistics_layout.addWidget(encounter_box)
        statistics_layout.addWidget(time_elapsed_box)
        statistics_layout.addStretch()
        statistics_layout.addWidget(hunt_and_start_container)
        statistics_widget.setLayout(statistics_layout)
    
        feed_and_stats_layout.addWidget(live_feed_widget)
        feed_and_stats_layout.addWidget(statistics_widget)

        main_layout.addWidget(header_widget)
        main_layout.addWidget(feed_and_stats_widget)

        self.webcam_stream.frame_ready.connect(self.update_video_feed)
        self.webcam_stream.start()

    def connect_arduino(self, com_port):
        self.connect_arduino_button.setText("Connecting...")
        self.connect_arduino_button.setEnabled(False)
        # Create and start thread
        self.connection_thread = ArduinoConnectionThread(com_port)
        self.connection_thread.connected.connect(self.on_arduino_connected)
        self.connection_thread.failed.connect(self.on_arduino_failed)
        self.connection_thread.start()
    
    def on_arduino_connected(self, controller):
        self.arduino_controller = controller
        self.status_indicator.setStyleSheet("color: #28a745; font-size: 18px; background-color: transparent;")  # Green dot
        self.connection_state_label.setText(f"Connected")
        self.connect_arduino_button.setText("Connected")
        self.connect_arduino_button.setEnabled(True)
    
    def on_arduino_failed(self, error_msg):
        QMessageBox.critical(
            self,
            "Arduino Connection Failed",
            f"Could not connect to Arduino:\n{error_msg}"
        )
        self.arduino_controller = None
        self.status_indicator.setStyleSheet("color: #dc3545; font-size: 18px; background-color: transparent;")
        self.connection_state_label.setText("Disconnected")
        self.connect_arduino_button.setText("Connect")
        self.connect_arduino_button.setEnabled(True)

    def update_video_feed(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        #print(h, w, ch)
        bytes_per_line = ch * w # 3 colors (1 byte each) * width for RGB
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888) 
        pixmap = QPixmap.fromImage(qt_image)
        self.video_feed.setPixmap(pixmap)
            #print(self.video_label.size())
            #print(self.webcam_container.pos(), self.video_label.pos())

    def on_hunt_change(self):
        if self.hunt_selection_combobox.currentText() == "HGSS Random Encounters":
            self.tile_count_box.setVisible(True)
            self.tile_count_box.setEnabled(True)
        else:
            self.tile_count_box.setVisible(False)
            self.title_count_box.setEnabled(False)

    def start_hunt(self, hunt_type, tile_count = None):
        if self.arduino_controller:
            self.arduino_controller.hunt_type = hunt_type
            self.arduino_controller.tile_count = tile_count
            self.arduino_controller.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    app.exec()