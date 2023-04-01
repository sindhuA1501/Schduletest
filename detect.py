import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils
import time
import numpy

def run(model: str, camera_id, width, height, num_threads: int,threshold : float,enable_edgetpu: bool):

    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()

    # Start capturing video input from the camera
    cap = cv2.VideoCapture(str(camera_id))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Visualization parameters
    row_size = 20  # pixels
    left_margin = 24  # pixels
    text_color = (0, 0, 255)  # red
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
    detection_options = processor.DetectionOptions(
        max_results=3, score_threshold= float(threshold))
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
    detector = vision.ObjectDetector.create_from_options(options)

    # Continuously capture images from the camera and run inference
    while True:
        success, image = cap.read()

        if success is False or image is None:
            print(image)
            print("XXXXXXXXXXXXXXXXXXX")

#            run(model, camera_id, width, height, num_threads,threshold, enable_edgetpu)
        print("GGG",image)
#cv2.imshow('x',image)
        counter += 1
        # image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(rgb_image)
        # Run object detection estimation using the model.
        detection_result = detector.detect(input_tensor)

        # Draw keypoints and edges on input image
        image, result = utils.visualize(image, detection_result)
        cv2.imwrite("Frame2.jpg", image)
        if counter % fps_avg_frame_count == 0:
            end_time = time.time()
            fps = fps_avg_frame_count / (end_time - start_time)
            start_time = time.time()

        # Show the FPS
        fps_text = 'FPS = {:.1f}'.format(fps)
        text_location = (left_margin, row_size)
        cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, text_color, font_thickness)
        cv2.imwrite('object_detector.jpg', image)

        # Stop the program if the ESC key is pressed.
        # if cv2.waitKey(1) == 27:
        # break
        personCount = 0
        for i in result:
            objectName = i
            if objectName == 'person':
                personCount = personCount + 1
            if personCount > 1:
                cv2.imwrite('personcount.jpg', image)


        key = cv2.waitKey(1)
        if key == 27:
            break
        return personCount



#run('/home/pi/Downloads/Schduletest/efficientdet_lite0.tflite','rtsp://admin:xx2317xx2317@192.168.1.45:554/media/video2',640, 480, 1,0.5, False)
