import sys
import math
import cv2 as cv

from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsLineItem,
    QGraphicsEllipseItem,
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QImage, QPixmap, QPen, QColor, QPainter

VIDEO_PATH = "PXL_20260417_113052141.mp4"


def read_frames(path):
    cap = cv.VideoCapture(VIDEO_PATH)

    frames = []

    print("Reading images", flush=True)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    print("Done", flush=True)

    return frames


frames = read_frames(VIDEO_PATH)


def cv_to_pixmap(frame):
    # 1. Convert BGR (OpenCV default) to RGB
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # 2. Get dimensions
    height, width, channel = frame_rgb.shape
    bytes_per_line = channel * width

    # 3. Create QImage
    # Note: We use .data to pass the buffer, but ensure the frame
    # doesn't get garbage collected while the QImage is in use!
    q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

    # 4. Convert to Pixmap for the Scene (copies the data, making it safe)
    return QPixmap.fromImage(q_img)


class Handle(QGraphicsEllipseItem):
    """The draggable endpoints of the line."""

    def __init__(self, parent, index):
        super().__init__(-6, -6, 12, 12, parent)
        self.setBrush(QColor("cyan"))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.index = index  # 0 for start, 1 for end

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if self.parentItem():
                # Tell the parent line to update its coordinates when the handle moves
                self.parentItem().update_line(self.index, value)
        return super().itemChange(change, value)


class MovableLine(QGraphicsLineItem):
    """A line with two interactive handles."""

    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        pen = QPen(QColor("yellow"), 3)
        self.setPen(pen)

        # Create handles at the start and end points
        self.p1 = Handle(self, 0)
        self.p2 = Handle(self, 1)
        self.p1.setPos(x1, y1)
        self.p2.setPos(x2, y2)

    def update_line(self, index, pos):
        line = self.line()
        if index == 0:
            line.setP1(pos)
        else:
            line.setP2(pos)
        self.setLine(line)


class ImageViewer(QGraphicsView):
    def __init__(self, frame):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 1. Load the Image
        pixmap = cv_to_pixmap(frame)

        self.pixmap_item = self.scene.addPixmap(pixmap)

        # 2. Add the Movable Line
        self.line_item = MovableLine(50, 50, 200, 200)
        self.scene.addItem(self.line_item)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def update_frame(self, new_frame):
        """Call this if you are reading a video stream"""
        pixmap = cv_to_pixmap(new_frame)
        self.pixmap_item.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Replace 'your_image.jpg' with your actual file path
    viewer = ImageViewer(frames[0])
    viewer.setWindowTitle("Draggable Line Over Image")
    viewer.resize(800, 600)
    viewer.show()

    sys.exit(app.exec())
