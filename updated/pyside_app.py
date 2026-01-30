from enum import Enum
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QPushButton, QDialog, QListWidget, QListWidgetItem, QMessageBox, QSizePolicy
from PySide6.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen
from PySide6.QtCore import Qt, QObject, Signal, QRect, QPoint, QSize
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
        self.top_left_corner = QPoint(self.size().width() * 0.1, self.size().height() * 0.1)
        self.crop_region = QRect(self.top_left_corner, QSize(self.size().width() - self.top_left_corner.x() * 2, self.size().height() - self.top_left_corner.y() * 2))
        self.top_right_corner = self.crop_region.topRight()
        self.bottom_left_corner = self.crop_region.bottomLeft()
        self.bottom_right_corner = self.crop_region.bottomRight()
        # For creating new crop region
        self.start_point = None
        self.end_point = None

        self.video_feed = QLabel()
        self.dragging = False
        self.drag_mode = Drag.NONE
        # Handles for diagonally resizing crop region
        self.handle_size = QSize(8, 8)
        self.top_left_handle = QRect(QPoint(self.top_left_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        self.top_right_handle = QRect(QPoint(self.top_right_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        self.bottom_left_handle = QRect(QPoint(self.bottom_left_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
        self.bottom_right_handle = QRect(QPoint(self.bottom_right_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2)), self.handle_size)
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
        mouse_pos = event.position().toPoint() # Convert QPointF -> QPoint
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_mode = self.get_drag_mode(mouse_pos)
            if self.drag_mode == Drag.NEW_REGION:
                self.start_point = mouse_pos
                self.end_point = mouse_pos
            elif self.drag_mode == Drag.MOVE:
                self.move_start_point = mouse_pos
            self.update_handles_and_edges()
            self.update()

    def mouseMoveEvent(self, event):
        mouse_pos = event.position().toPoint()
        if self.drag_mode == Drag.NEW_REGION:
            self.setCursor(Qt.CrossCursor)
        elif self.top_left_handle.contains(mouse_pos) or self.bottom_right_handle.contains(mouse_pos):
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.top_right_handle.contains(mouse_pos) or self.bottom_left_handle.contains(mouse_pos):
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.top_edge.contains(mouse_pos) or self.bottom_edge.contains(mouse_pos):
            self.setCursor(Qt.SizeVerCursor)
        elif self.left_edge.contains(mouse_pos) or self.right_edge.contains(mouse_pos):
            self.setCursor(Qt.SizeHorCursor)
        elif self.crop_region.contains(mouse_pos):
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
                self.top_left_corner = QPoint(min(self.start_point.x(), self.end_point.x()), min(self.start_point.y(), self.end_point.y()))
                self.bottom_right_corner = QPoint(max(self.start_point.x(), self.end_point.x()), max(self.start_point.y(), self.end_point.y()))

            self.crop_region = QRect(self.top_left_corner, self.bottom_right_corner)
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
            self.crop_region = QRect(self.top_left_corner, self.bottom_right_corner)
            self.update_handles_and_edges()
            self.update()

    def update_handles_and_edges(self):
        if self.crop_region:
            # top left corner is smallest tuple, bottom right is largest. top right is 2 away from top left, bottom left is 2 away from bottom right in the list
            corners = [self.crop_region.topLeft().toTuple(), self.crop_region.topRight().toTuple(), self.crop_region.bottomLeft().toTuple(), self.crop_region.bottomRight().toTuple()]
            tl_corner = min(corners)
            br_corner = max(corners)
            self.top_right_corner, self.bottom_left_corner = QPoint(br_corner[0], tl_corner[1]), QPoint(tl_corner[0], br_corner[1])
            self.top_left_corner, self.bottom_right_corner = QPoint(tl_corner[0], tl_corner[1]), QPoint(br_corner[0], br_corner[1])
            #print(corners)
            #print(tl_corner, tr_corner, bl_corner, br_corner)
            self.top_left_handle = QRect(self.top_left_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            self.top_right_handle = QRect(self.top_right_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            self.bottom_left_handle = QRect(self.bottom_left_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            self.bottom_right_handle = QRect(self.bottom_right_corner - QPoint(self.handle_size.width() // 2, self.handle_size.height() // 2), self.handle_size)
            
            self.top_edge = QRect(self.top_left_handle.topRight(), self.top_right_handle.bottomLeft())
            self.bottom_edge = QRect(self.bottom_left_handle.topRight(), self.bottom_right_handle.bottomLeft())
            self.left_edge = QRect(self.top_left_handle.bottomLeft(), self.bottom_left_handle.topRight())
            self.right_edge = QRect(self.top_right_handle.bottomLeft(), self.bottom_right_handle.topRight())
            
    def reset_crop_region(self):
        self.start_point = QPoint(self.size().width() * 0.1, self.size().height() * 0.1)
        self.crop_region = QRect(self.start_point, QSize(self.size().width() - self.start_point.x() * 2, self.size().height() - self.start_point.y() * 2))
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
        live_feed_widget.setLayout(live_feed_layout)

        # Webcam Feed
        self.webcam_container = QWidget()
        self.webcam_container_layout = QStackedLayout()

        self.video_feed = VideoWithCropOverlay()

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
        self.video_feed.setPixmap(pixmap)
        #print(self.video_label.size())
        #print(self.webcam_container.pos(), self.video_label.pos())
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    app.exec()