from numpy import loadtxt
from keras.models import load_model
import numpy as np

def make_predictions(img):
	model = load_model('plant_diagnosis.h5')
	img = np.reshape(img, [1, 256, 256, 3])
	y = model.predict(img)
	y = np.argmax(y)
	return y