import numpy as np
import pandas as pd
import cv2, os, re
import matplotlib.image
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from PIL import Image
import io

class Detector:

    def detector(file):

        def to_input(image_input):

            image_input = Image.open(io.BytesIO(image_input))

            #print(os.path.join(image_input, file))
            #image = cv2.imread(image_input)
            image = np.array(image_input)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            return image

        def find_roi(image, method="fast"):

            ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
            ss.setBaseImage(image)

            if method == 'fast':
                ss.switchToSelectiveSearchFast()
            else:
                ss.switchToSelectiveSearchQuality()

            rects = ss.process()
            roi = []

            for (x,y,w,h) in rects:

                roi.append([x,y,w,h])
                pass

            return roi


        def normalise_roi(image,roi_input):

            rois, rois_localisations = [], []
            (H, W) = image.shape[:2]

            for (x,y,w,h) in roi_input:

                if w/float(W) > 0.10 and h/float(H) > 0.10:
                    continue

                roi_output = image[y:y+h,x:x+w]
                roi_output = cv2.cvtColor(roi_output,cv2.COLOR_BGR2RGB)
                roi_output = cv2.resize(roi_output, (20,20))
                roi_output = np.array(list(map(lambda x : x/255,roi_output)))

                rois.append(roi_output)
                rois_localisations.append((x,y,x+w,y+h))
                pass

            return rois, rois_localisations


        def classification_on_roi(rois, model):

            predictions = model.predict(np.array(rois,dtype=np.float32))
            predictions = np.argmax(predictions, axis=1)

            return predictions

        def insert_roi_classed_on_image(image, predictions, rois_localisations):

            image_predicted = image.copy()

            for (i,label) in enumerate(predictions):

                if label == 1:
                    (startX,startY,endX,endY) = rois_localisations[i]
                    cv2.rectangle(image_predicted,(startX,startY),(endX,endY),(0,255,0),2)
                pass

            return image_predicted

        def to_output(image_predicted):

            #matplotlib.image.imsave('detector.png', image_predicted)
            #pass
            img = Image.fromarray(image_predicted)
            bytesIoObj = io.BytesIO()

            img.save(bytesIoObj, "PNG")
            #bytesIoObj.seek(0)
            #byteImg = bytesIoObj.read()
            bytesio_img = bytesIoObj.getvalue()
            #return image_predicted.tobytes()
            return bytesio_img




        model =  load_model('plane-model.h5')

        image = to_input(file)
        roi = find_roi(image)
        rois, rois_locations = normalise_roi(image, roi)
        predictions = classification_on_roi(rois, model)
        image_predicted = insert_roi_classed_on_image(image, predictions, rois_locations)

        return to_output(image_predicted)
