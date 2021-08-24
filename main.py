import cv2
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QWidget
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint, QRect

import sys

from qc_processor import GrabCutProcessor
from utils import convert_to_cv, convert_to_mask, convert_cv_to_q_image, get_max_contour_rect


class Window(QMainWindow):
    def __init__(self, im_path="/mnt/CVProjects/QtApp/background.jpg"):
        super().__init__()
        self.icon = "icon.jpeg"
        self.setWindowTitle("Drawing")
        self.setWindowIcon(QIcon(self.icon))

        self.im_path = im_path
        self.cv_background = cv2.imread(self.im_path)

        self.top = 400
        self.left = 400
        self.width = self.cv_background.shape[1]
        self.height = self.cv_background.shape[0]

        self.setGeometry(self.top, self.left, self.width, self.height)

        # ARGB32 for transparent image
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.transparent)

        self.pixel_map = QPixmap(self.im_path)

        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.green

        self.lastPoint = QPoint()

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("File")
        brush_menu = main_menu.addMenu("Brush Size")
        brush_color = main_menu.addMenu("Brush Color")
        process_image = main_menu.addMenu("Process Image")
        drawing_mode = main_menu.addMenu("Drawing Mode")

        open_action = QAction(QIcon("icon.jpeg"), "Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open_image)

        save_action = QAction(QIcon("icon.jpeg"), "Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save)

        clear_action = QAction(QIcon("icon.jpeg"), "Clear", self)
        clear_action.setShortcut("Ctrl+C")
        file_menu.addAction(clear_action)
        clear_action.triggered.connect(self.clear)

        reset_action = QAction(QIcon("icon.jpeg"), "Reset", self)
        reset_action.setShortcut("Ctrl+E")
        file_menu.addAction(reset_action)
        reset_action.triggered.connect(self.reset)

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

        processing_action = QAction(QIcon("icon.jpeg"), "Process", self)
        processing_action.setShortcut("Ctrl+X")
        process_image.addAction(processing_action)
        processing_action.triggered.connect(self.process_image)

        rect_action = QAction(QIcon("icon.jpeg"), "Draw rect", self)
        rect_action.setShortcut("Ctrl+1")
        drawing_mode.addAction(rect_action)
        rect_action.triggered.connect(self.draw_rect_mode)

        point_action = QAction(QIcon("icon.jpeg"), "Draw point", self)
        point_action.setShortcut("Ctrl+2")
        drawing_mode.addAction(point_action)
        point_action.triggered.connect(self.draw_point_mode)

        self.pop_up_w = None

        self.rect_mode = True
        self.start_rect_pos = None
        self.end_rect_pos = None
        self.gc = None
        self.processed_im = None
        self.reset()

    def process_image(self):
        src_im = self.processed_im

        if self.rect_mode:
            cv_red_green = convert_to_cv(self.image)
            cv_rect_mask = convert_to_mask(cv_red_green)
            rect = get_max_contour_rect(cv_rect_mask)
            processed = self.gc.gc_process_rect(image=src_im, rect=rect)
        else:
            cv_red_green = convert_to_cv(self.image)
            gray_mask = convert_to_mask(cv_red_green)
            processed = self.gc.gc_process(image=src_im, support_mask=gray_mask)

        self.processed_im = processed
        self.pixel_map = QPixmap(convert_cv_to_q_image(self.processed_im))
        self.update()

        # Work on pop up instead
        # p_w = processed.shape[1]
        # p_h = processed.shape[0]
        #
        # print("pop up")
        # self.pop_up_w = MyPopup(cv_im=processed)
        # self.pop_up_w.setGeometry(100, 100, p_w, p_h)
        # self.pop_up_w.show()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

            if self.rect_mode:
                self.start_rect_pos = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            # Create a painter on top of transparent image
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            if not self.rect_mode:
                painter.drawLine(self.lastPoint, event.pos())
                self.lastPoint = event.pos()
            else:
                self.clear()
                self.end_rect_pos = event.pos()
                rect = QRect(self.start_rect_pos, self.end_rect_pos)
                painter.drawRect(rect)
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

    def open_image(self):
        self.im_path, _ = QFileDialog.getOpenFileName()
        self.cv_background = cv2.imread(self.im_path)
        self.width = self.cv_background.shape[1]
        self.height = self.cv_background.shape[0]
        self.pixel_map = QPixmap(self.im_path)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.transparent)
        self.update()

    def save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                   "PNG(*.png);;JPEG(*.jpg *.jpeg);; ALL Files(*.*)")
        if file_path == "":
            print("ERROR")
            return

        # We drawn on image, hence, save the image
        # Convert format before saving

        self.pixel_map.save(file_path)

        # tobe_save = self.image.copy()
        # tobe_save = tobe_save.convertToFormat(QImage.Format_RGB32)
        # tobe_save.save(file_path)

        # self.image.save(file_path)
        # self.pixel_map.save(file_path)

    def reset(self):
        self.clear()
        self.start_rect_pos = None
        self.end_rect_pos = None
        self.gc = GrabCutProcessor()
        self.pixel_map = QPixmap(self.im_path)
        self.processed_im = self.cv_background
        self.update()

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

    def draw_rect_mode(self):
        self.rect_mode = True

    def draw_point_mode(self):
        self.rect_mode = False


class MyPopup(QWidget):
    def __init__(self, cv_im):
        QWidget.__init__(self)
        self.cv_im = cv_im
        self.image = convert_cv_to_q_image(self.cv_im)

    def paintEvent(self, e):
        dc = QPainter(self)
        dc.drawImage(self.rect(), self.image, self.rect())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
