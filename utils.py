import cv2
import numpy as np


def convert_to_cv(src):
    """  Converts a QImage into an opencv MAT format  """

    src = src.convertToFormat(4)

    width = src.width()
    height = src.height()

    ptr = src.bits()
    ptr.setsize(src.byteCount())
    arr = np.array(ptr).reshape((height, width, 4))  # Copies the data

    im = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return im
