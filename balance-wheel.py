import sys
import math
import cv2 as cv

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QLabel,
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
        super().__init__(-15, -15, 30, 30, parent)
        self.setBrush(QColor("white"))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.index = index  # 0 for start, 1 for end

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if self.parentItem():
                self.parentItem().update_handle(self.index, value)
        return super().itemChange(change, value)


class MovableLine(QGraphicsItem):
    """Two connected line segments with three draggable handles."""

    def __init__(self, x1, y1, x2, y2, x3, y3):
        super().__init__()
        pen = QPen(QColor("white"), 10)

        self.seg1 = QGraphicsLineItem(x1, y1, x2, y2, self)
        self.seg1.setPen(pen)
        self.seg2 = QGraphicsLineItem(x2, y2, x3, y3, self)
        self.seg2.setPen(pen)

        self.p1 = Handle(self, 0)
        self.p2 = Handle(self, 1)
        self.p3 = Handle(self, 2)
        self.p1.setPos(x1, y1)
        self.p2.setPos(x2, y2)
        self.p3.setPos(x3, y3)

    def update_handle(self, index, pos):
        if index == 0:
            l = self.seg1.line(); l.setP1(pos); self.seg1.setLine(l)
        elif index == 1:
            l = self.seg1.line(); l.setP2(pos); self.seg1.setLine(l)
            l = self.seg2.line(); l.setP1(pos); self.seg2.setLine(l)
        else:
            l = self.seg2.line(); l.setP2(pos); self.seg2.setLine(l)

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget):
        pass


class ImageViewer(QGraphicsView):
    def __init__(self, frames, frame_label):
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.frame_label = frame_label

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        pixmap = cv_to_pixmap(frames[0])
        self.pixmap_item = self.scene.addPixmap(pixmap)

        self.line_item = MovableLine(50, 50, 200, 200, 350, 350)
        self.scene.addItem(self.line_item)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameStyle(0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def show_frame(self, index):
        self.frame_index = index
        self.pixmap_item.setPixmap(cv_to_pixmap(self.frames[index]))
        self.frame_label.setText(f"Frame: {index}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.show_frame(min(self.frame_index + 1, len(self.frames) - 1))
        elif event.key() == Qt.Key.Key_Left:
            self.show_frame(max(self.frame_index - 1, 0))
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Draggable Line Over Image")
    layout = QHBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)

    label = QLabel("Frame: 0")
    label.setAlignment(Qt.AlignmentFlag.AlignTop)

    viewer = ImageViewer(frames, label)
    layout.addWidget(viewer)
    layout.addWidget(label)

    screen = app.primaryScreen().availableGeometry()
    img_h, img_w = frames[0].shape[:2]
    label_w = label.sizeHint().width()
    scale = min((screen.width() - label_w) / img_w, screen.height() / img_h, 1.0)
    window.resize(int(img_w * scale) + label_w, int(img_h * scale))

    window.show()
    viewer.fitInView(viewer.pixmap_item, Qt.KeepAspectRatio)

    sys.exit(app.exec())
