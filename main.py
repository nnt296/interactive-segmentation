from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QFileDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint

from PIL import Image
import sys

from utils import convert_to_cv
import cv2


class Window(QMainWindow):
    def __init__(self, im_path="/mnt/CVProjects/QtApp/background.jpg"):
        super().__init__()

        self.im_path = im_path
        im = Image.open(self.im_path)

        self.top = 400
        self.left = 400
        self.width = im.size[0]
        self.height = im.size[1]

        self.icon = "icon.jpeg"

        self.setWindowTitle("Drawing")
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setWindowIcon(QIcon(self.icon))

        # ARGB32 for transparent image
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.transparent)

        self.pixel_map = QPixmap(self.im_path)

        self.drawing = False
        self.brushSize = 2
        self.brushColor = Qt.black

        self.lastPoint = QPoint()

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("File")
        brush_menu = main_menu.addMenu("Brush Size")
        brush_color = main_menu.addMenu("Brush Color")
        process_image = main_menu.addMenu("Process Image")

        save_action = QAction(QIcon("icon.jpeg"), "Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save)

        clear_action = QAction(QIcon("icon.jpeg"), "Clear", self)
        clear_action.setShortcut("Ctrl+C")
        file_menu.addAction(clear_action)
        clear_action.triggered.connect(self.clear)

        three_px_action = QAction(QIcon("icon.jpeg"), "3px", self)
        three_px_action.setShortcut("Ctrl+T")
        brush_menu.addAction(three_px_action)
        three_px_action.triggered.connect(self.three_pixel)

        five_px_action = QAction(QIcon("icon.jpeg"), "5px", self)
        five_px_action.setShortcut("Ctrl+F")
        brush_menu.addAction(five_px_action)
        five_px_action.triggered.connect(self.five_pixel)

        red_action = QAction(QIcon("icon.jpeg"), "Red", self)
        red_action.setShortcut("Ctrl+R")
        brush_color.addAction(red_action)
        red_action.triggered.connect(self.red_pen)

        green_action = QAction(QIcon("icon.jpeg"), "Green", self)
        green_action.setShortcut("Ctrl+G")
        brush_color.addAction(green_action)
        green_action.triggered.connect(self.green_pen)

        processing_action = QAction(QIcon("icon.jpeg"), "Process image", self)
        processing_action.setShortcut("Ctrl+X")
        process_image.addAction(processing_action)
        processing_action.triggered.connect(self.process_image)

    def process_image(self):
        pass

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            # Create a painter on top of transparent image
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        # This function is used to set background = pix-map
        # and set an additional layer as transparent image for drawing
        canvas_painter = QPainter(self)
        # canvas_painter.drawImage(self.rect(), self.image, self.image.rect())
        canvas_painter.drawPixmap(self.rect(), self.pixel_map, self.pixel_map.rect())
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    def save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                   "PNG(*.png);;JPEG(*.jpg *.jpeg);; ALL Files(*.*)")
        if file_path == "":
            print("ERROR")
            return

        # We drawn on image, hence, save the image
        # Convert format before saving
        tobe_save = self.image.copy()
        tobe_save = tobe_save.convertToFormat(QImage.Format_RGB32)
        tobe_save.save(file_path)

        # self.image.save(file_path)
        # self.pixel_map.save(file_path)

    def clear(self):
        self.image.fill(Qt.transparent)
        self.update()

    def three_pixel(self):
        self.brushSize = 3

    def five_pixel(self):
        self.brushSize = 5

    def red_pen(self):
        self.brushColor = Qt.red

    def green_pen(self):
        self.brushColor = Qt.green


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
