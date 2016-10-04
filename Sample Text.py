from __future__ import print_function
from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils
from PIL import Image
from os import listdir
from keras.models import load_model
from os.path import isfile, join
import PIL.ImageOps
import matplotlib.cm as cm
import numpy as np
from skimage import color
from skimage import io
import pickle
import cv
import matplotlib.pyplot as plt
import os
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot
from keras.regularizers import l2, activity_l2
from keras.callbacks import TensorBoard




batch_size = 128
nb_classes = 10
nb_epoch = 200
# input image dimensions
img_rows, img_cols = 32, 32
# number of convolutional filters to use
nb_filters = 32
# size of pooling area for max pooling
nb_pool = 2
# convolution kernel size
kernel_size = (5, 5)

# Creating the Dataset
Train = []
Test = []
for i in range(0, 4200):
    Train.append(i % 10)
for i in range(4200, 6000):
    Test.append(i % 10)
for i in range(0,10):
    path = 'NewDGray/'+str(i)
    num_files = len([f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))])
    for j in range(0,num_files):
        Train.append(i)

for i in range(0,10):
    path = 'NewDGray/test/'+str(i)
    num_files = len([f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))])
    for j in range(0,num_files):
        Test.append(i)



y_train = np.asarray(Train)
y_test = np.asarray(Test)

Name = []
for filename in listdir("Train"):
    if filename.endswith(".bmp"):
        Name.append("Train/" + filename)
Name.sort()
for i in range(0,10):
    L=[]
    for filename in listdir("NewDGray/"+str(i)+"/"):
        #rint(filename)
        if(filename.endswith(".tif")):
            L.append("NewDGray/"+str(i)+"/"+filename)
    L.sort()
    for i in range(0,len(L)):
        Name.append(L[i])
X_train = np.array([np.array(Image.open(fname)) for fname in Name])
Name2 = []

for filename in listdir("Test"):
    if filename.endswith(".bmp"):
        Name2.append("Test/" + filename)
Name2.sort()
for i in range(0,10):
    L=[]
    for filename in listdir("NewDGray/test/"+str(i)+"/"):
        if(filename.endswith(".tif")):
            L.append("NewDGray/test/"+str(i)+"/"+filename)
    L.sort()
    for i in range(0,len(L)):
        Name2.append(L[i])
    #Name2.append(L)
X_test = np.array([np.array(Image.open(fname)) for fname in Name2])

X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)

print(X_train.shape)
print(X_test.shape)



#Autoencoder Part:

input_img = Input(shape=(1, 32, 32))

x = Convolution2D(128, 3, 3, activation='relu', border_mode='same')(input_img)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Convolution2D(64, 3, 3, activation='relu', border_mode='same')(x)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Dropout(0.35)(x)
x = Convolution2D(16, 3, 3, activation='relu', border_mode='same')(x)
encoded = MaxPooling2D((2, 2), border_mode='same')(x)

# at this point the representation is (32, 7, 7)

x = Convolution2D(16, 3, 3, activation='relu', border_mode='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Dropout(0.35)(x)
x = Convolution2D(64, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
x = Convolution2D(128 , 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
decoded = Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='RMSprop', loss='binary_crossentropy')

datagen = ImageDataGenerator(

    rotation_range=0.8,
    width_shift_range=0.3,
    height_shift_range=0.2
)

datagen.fit(X_train,augment=True)

autoencoder.fit_generator(datagen.flow(X_train, X_train, batch_size=128,shuffle=True),
                          nb_epoch=20,
                          samples_per_epoch=23513,
                          validation_data=(X_test, X_test)
                          )

# autoencoder.fit_generator(X_train, X_train,
#                 nb_epoch=100,
#                 batch_size=128,
#                 shuffle=True,
#                 validation_data=(X_test, X_test),
#                 callbacks = [TensorBoard(log_dir='/tmp/oencoder3')]
#                 )

#autoencoder.load_weights('autoencoder.h5')
#encoded_imgs = autoencoder.predict(X_train)
decoded_imgs = autoencoder.predict(X_test)

#autoencoder.save('autoencoder.h5')

#Supervised Learning Part
x=Convolution2D(256, 4, 4, activation='relu', border_mode='same')(encoded)
x=MaxPooling2D((2, 2), border_mode='same')(x)
x=Dropout(0.35)(x)
x=Convolution2D(128, 2, 2, activation='relu', border_mode='same')(x)
x=MaxPooling2D((2, 2), border_mode='same')(x)
x=Flatten()(x)
x=Dense(512,activation='relu')(x)
x=Dense(128,activation='relu')(x)
x=Dropout(0.35)(x)
x=Dense(50,activation='relu')(x)
x=Dense(10,activation='softmax')(x)
MODEL=Model([input_img],[x])



MODEL.compile(loss='categorical_crossentropy',
              optimizer='RMSprop',
              metrics=['accuracy'])


train_datagen = ImageDataGenerator(
         rotation_range=0.3,
         width_shift_range=0.2,
        height_shift_range=0.2
        )
train_datagen.fit(X_train, augment=True)
test_datagen = ImageDataGenerator(

)

train_generator = train_datagen.flow(
         X_train, Y_train,
         batch_size=batch_size)
validation_generator = test_datagen.flow(
        X_test,Y_test,
        batch_size=batch_size)

from keras.callbacks import TensorBoard

MODEL.fit_generator(
        train_generator,
        samples_per_epoch=23513,
        nb_epoch=120,
        validation_data=validation_generator,
        nb_val_samples=5786,
        callbacks = [TensorBoard(log_dir='/tmp/oencoder3')])



score = MODEL.evaluate(X_test, Y_test, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])