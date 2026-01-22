import cv2
import threading

class WebcamStream:
    def __init__(self, show_feed=True):
        self.frame = None
        self.display_frame = None
        self.lock = threading.Lock()
        self.running = False
        self.cap = None
        self.show_feed = show_feed
        
        # Crop selection variables
        self.selecting = False
        self.start_point = None
        self.end_point = None
        self.crop_rect = None  # (x, y, width, height)
        self.cropped_mode = False
        
    def start(self):
        """Start the webcam capture thread"""
        self.cap = cv2.VideoCapture(0)
        self.running = True
        thread = threading.Thread(target=self.update_frame, daemon=True)
        thread.start()
        
        # Set up mouse callback for crop selection
        if self.show_feed:
            cv2.namedWindow('Webcam Feed')
            cv2.setMouseCallback('Webcam Feed', self.mouse_callback)
        
        return self
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drag selection"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start selection
            self.selecting = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            # Update selection rectangle while dragging
            if self.selecting:
                self.end_point = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            # Finish selection
            self.selecting = False
            self.end_point = (x, y)
            
            # Calculate crop rectangle (ensure positive width/height)
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            
            x_min = min(x1, x2)
            y_min = min(y1, y2)
            x_max = max(x1, x2)
            y_max = max(y1, y2)
            
            width = x_max - x_min
            height = y_max - y_min
            
            # Only set crop if the rectangle is large enough
            if width > 10 and height > 10:
                self.crop_rect = (x_min, y_min, width, height)
                self.cropped_mode = True
                print(f"Crop region set: x={x_min}, y={y_min}, w={width}, h={height}")
    
    def update_frame(self):
        """Continuously capture frames in background thread"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
                    
                    # Create display frame with annotations
                    display = frame.copy()
                    
                    # Draw the selection rectangle while selecting
                    if self.selecting and self.start_point and self.end_point:
                        cv2.rectangle(display, self.start_point, self.end_point, 
                                    (0, 255, 0), 2)
                    
                    # Draw the crop rectangle if set
                    elif self.crop_rect:
                        x, y, w, h = self.crop_rect
                        cv2.rectangle(display, (x, y), (x + w, y + h), 
                                    (0, 255, 0), 2)
                        
                        # Add text indicating crop mode
                        cv2.putText(display, "Cropped Region (Press 'r' to reset)", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.7, (0, 255, 0), 2)
                    
                    # Add instructions
                    if not self.crop_rect and not self.selecting:
                        cv2.putText(display, "Drag to select crop region", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.7, (255, 255, 255), 2)
                    
                    self.display_frame = display
                
                # Display the feed if enabled
                if self.show_feed:
                    show_frame = self.display_frame if self.display_frame is not None else frame
                    cv2.imshow('Webcam Feed', show_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.running = False
                    elif key == ord('r'):
                        # Reset crop region
                        self.crop_rect = None
                        self.cropped_mode = False
                        self.start_point = None
                        self.end_point = None
                        print("Crop region reset")
    
    def get_frame(self, cropped=True):
        """Get the current frame (thread-safe)
        
        Args:
            cropped: If True and crop region is set, return cropped frame
        """
        with self.lock:
            if self.frame is None:
                return None
            
            frame = self.frame.copy()
            
            # Apply crop if requested and available
            if cropped and self.crop_rect:
                x, y, w, h = self.crop_rect
                # Ensure crop is within frame bounds
                height, width = frame.shape[:2]
                x = max(0, min(x, width - 1))
                y = max(0, min(y, height - 1))
                w = min(w, width - x)
                h = min(h, height - y)
                frame = frame[y:y+h, x:x+w]
            
            return frame
    
    def get_crop_rect(self):
        """Get the current crop rectangle"""
        return self.crop_rect
    
    def set_display_frame(self, frame):
        """Set a frame with annotations to display"""
        with self.lock:
            self.display_frame = frame.copy()
    
    def stop(self):
        """Stop the webcam capture"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


# Example usage
if __name__ == "__main__":
    webcam = WebcamStream(show_feed=True)
    webcam.start()
    
    try:
        while True:
            # Get the cropped frame
            cropped_frame = webcam.get_frame(cropped=True)
            
            if cropped_frame is not None:
                # Do something with the cropped frame
                # For example, show it in a separate window
                if webcam.crop_rect:
                    cv2.imshow('Cropped View', cropped_frame)
                    cv2.waitKey(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        webcam.stop()