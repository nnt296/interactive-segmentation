import torch
import cv2

from matplotlib import pyplot as plt

from dl_is.isegm.inference.predictors import get_predictor
from dl_is.isegm.inference import utils, clicker


class DLSegmentProcessor:
    def __init__(self):
        self.image = None
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.predictor_params = {'brs_mode': 'NoBRS'}
        checkpoint_path = utils.find_checkpoint("./dl_is/weights", "coco_lvis_h18_baseline")
        self.model = utils.load_is_model(checkpoint_path, self.device, cpu_dist_maps=True)
        self.predictor = None
        self.clicker = clicker.Clicker()
        self.segment_threshold = 0.5

    def set_image(self, image):
        self.image = image
        self.predictor = get_predictor(self.model, device=self.device, **self.predictor_params)
        self.predictor.set_input_image(self.image)

    def process(self, y, x, is_positive):
        if self.predictor is None:
            return

        click = clicker.Click(is_positive=is_positive, coords=(y, x))
        self.clicker.add_click(click)
        pred = self.predictor.get_prediction(clicker=self.clicker, prev_mask=None)

        torch.cuda.empty_cache()

        pred[pred > self.segment_threshold] = 255
        pred[pred < self.segment_threshold] = 0

        return pred.astype("uint8")


if __name__ == '__main__':
    origin = cv2.imread("/mnt/CVProjects/nidec.png")

    processor = DLSegmentProcessor()
    processor.set_image(origin)

    coordinates = [(832, 1037, True), (1026, 1241, True),
                   (522, 1021, True), (912, 1290, True),
                   (973, 1264, False)]

    result = None
    for y, x, is_positive in coordinates:
        result = processor.process(y, x, is_positive)

    plt.imshow(result)
    plt.show()
