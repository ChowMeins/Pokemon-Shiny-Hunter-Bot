import cv2
import threading

class WebcamStream:
    def __init__(self, show_feed=True):
        self.frame = None
        self.display_frame = None  # Separate frame for display with annotations
        self.lock = threading.Lock()
        self.running = False
        self.cap = None
        self.show_feed = show_feed
        
    def start(self):
        """Start the webcam capture thread"""
        self.cap = cv2.VideoCapture(0)
        self.running = True
        thread = threading.Thread(target=self.update_frame, daemon=True)
        thread.start()
        return self
    
    def update_frame(self):
        """Continuously capture frames in background thread"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
                    # Use display_frame if set, otherwise use original frame
                    show_frame = self.display_frame if self.display_frame is not None else frame
                
                # Display the feed if enabled
                if self.show_feed:
                    cv2.imshow('Webcam Feed', show_frame)
                    if cv2.waitKey(1) == ord('q'):
                        self.running = False
    
    def get_frame(self):
        """Get the current frame (thread-safe)"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
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