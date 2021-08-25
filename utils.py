import cv2
import numpy as np
from PyQt5.QtGui import QImage


def convert_to_cv(src):
    """  Converts a QImage into an opencv MAT format  """

    src = src.convertToFormat(4)

    width = src.width()
    height = src.height()

    ptr = src.bits()
    ptr.setsize(src.byteCount())
    arr = np.array(ptr).reshape((height, width, 4))  # Copies the data

    # Note sure why this arr is in BGRA format
    im = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
    return im


def convert_pil_to_q_image(pil_im):
    rgb = np.array(pil_im)
    height, width, _ = rgb.shape
    bytes_per_line = 3 * width
    return QImage(rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)


def convert_cv_to_q_image(cv_im):
    # Convert BGR to RGB for QImage
    rgb = cv2.cvtColor(cv_im, cv2.COLOR_BGR2RGB)
    height, width, _ = rgb.shape
    bytes_per_line = 3 * width
    return QImage(rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)


def convert_to_mask(red_green_src):
    # Input BGR images containing red or green color
    lower_red = np.array([0, 0, 50])
    upper_red = np.array([0, 0, 255])
    mask_red = cv2.inRange(red_green_src, lower_red, upper_red)

    lower_green = np.array([0, 50, 0])
    upper_green = np.array([0, 255, 0])
    mask_green = cv2.inRange(red_green_src, lower_green, upper_green)

    mask = np.zeros(red_green_src.shape[:2]).astype(np.uint8)
    # Mark red as bg, green as fg
    mask[np.where(mask_red)] = 128
    mask[np.where(mask_green)] = 255

    return mask


def get_max_contours(contours):
    """
    Get index of max-area-contour
    Args:
        contours: list of contour
    Returns:
        index: int index of max-area-contour, -1 if not found
    """
    max_area = -1
    index = -1
    for idx, con in enumerate(contours):
        area = cv2.contourArea(con)
        if area > max_area:
            max_area = area
            index = idx

    return index


def get_max_contour_rect(mask):
    """
    Get the bounding rect of given mask using contours
    Args:
        mask: gray scale mask contain contours
    Returns:
        rect: x,y,w,h rectangle
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return 0, 0, mask.shape[1], mask.shape[0]

    max_idx = get_max_contours(contours)
    rect = cv2.boundingRect(contours[max_idx])

    return rect


def resize_max(cv_im, max_size=1080):
    """
    Args:
        cv_im: H x W x C cv image (not gray)
        max_size: expect maximum size
    Returns:
        resized_im
    """
    h, w, _ = cv_im.shape
    max_s = max(h, w)
    # Skip if smaller than max_size
    if max_size > max_s:
        return cv_im

    scale = max_size / max_s
    resized_im = cv2.resize(cv_im, None, fx=scale, fy=scale)
    return resized_im
