from inference import get_model
import supervision as sv
import cv2

# define the image url to use for inference
#pull images from cams later on ****
image_file = "taylor-swift-album-1989.jpeg"
image = cv2.imread(image_file)

# load a pre-trained yolov8n model
# this is my trained model
model = get_model(model_id="vehicle_detection_yolov8-rptry")

# run inference on our chosen image, image can be a url, a numpy array, a PIL image, etc.
# identify the objects in the image
results = model.infer(image)[0]

# load the results into the supervision Detections api
# this is for drawing the boxes
detections = sv.Detections.from_inference(results)

# create supervision annotators
# create the bounding boxes
bounding_box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# annotate the image with our inference results
annotated_image = bounding_box_annotator.annotate(
    scene=image, detections=detections)
annotated_image = label_annotator.annotate(
    scene=annotated_image, detections=detections)

# display the image
sv.plot_image(annotated_image)