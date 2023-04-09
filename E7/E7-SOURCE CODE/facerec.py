import cv2
import numpy
import os

size = 2
haar_cascade = cv2.CascadeClassifier(r'face_cascade.xml')


def train_model():
    model = cv2.face.LBPHFaceRecognizer_create()
    fn_dir = 'face_samples'

    print('Training...')

    (images, lables, names, id) = ([], [], {}, 0)

    for (subdirs, dirs, files) in os.walk(fn_dir):
        
        for subdir in dirs:
            names[id] = subdir
            subjectpath = os.path.join(fn_dir, subdir)
            
            for filename in os.listdir(subjectpath):
                
                f_name, f_extension = os.path.splitext(filename)
                if(f_extension.lower() not in ['.png','.jpg','.jpeg','.gif','.pgm']):
                    print("Skipping "+filename+", wrong file type")
                    continue
                path = subjectpath + '/' + filename
                lable = id
                
                images.append(cv2.imread(path, 0))
                lables.append(int(lable))
            id += 1

   
    (images, lables) = [numpy.array(lis) for lis in [images, lables]]
    
    model.train(images, lables)

    return (model, names)



def detect_faces(gray_frame):
    global size, haar_cascade

    
    mini_frame = cv2.resize(gray_frame, (int(gray_frame.shape[1] / size), int(gray_frame.shape[0] / size)))

    
    faces = haar_cascade.detectMultiScale(mini_frame)
    return faces


def recognize_face(model, frame, gray_frame, face_coords, names):
    (img_width, img_height) = (112, 92)
    recognized = []
    recog_names = []

    for i in range(len(face_coords)):
        face_i = face_coords[i]

        
        (x, y, w, h) = [v * size for v in face_i]
        face = gray_frame[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (img_width, img_height))

        
        (prediction, confidence) = model.predict(face_resize)

        
        if (confidence<95 and names[prediction] not in recog_names):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            recog_names.append(names[prediction])
            recognized.append((names[prediction].capitalize(), confidence))
        elif (confidence >= 95):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return (frame, recognized)


