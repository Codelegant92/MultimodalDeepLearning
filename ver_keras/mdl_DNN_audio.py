__author__ = 'jhlee'

from keras.models import Graph, Sequential
from keras.preprocessing import sequence

from keras.utils import np_utils
from keras.utils.np_utils import accuracy

from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
#from keras.datasets import imdb
#from keras.optimizers import RMSprop

import mdl_data
import numpy as np

np.random.seed(1337)  # for reproducibility

data = mdl_data.YLIMED('YLIMED_info.csv', '/DATA/YLIMED150924/audio/mfcc20', '/DATA/YLIMED150924/keyframe/fc7')

X_train = data.get_aud_X_train()
X_test = data.get_aud_X_test()
y_train = data.get_y_train()
y_test = data.get_y_test()

max_features = len(X_train)	#43599
maxlen = len(X_train[0])	#2000
batch_size = 32
nb_epoch = 10

print len(X_train), 'train sequences'
print len(X_test), 'test sequences'

#Pad sequences (samples x time)
X_train = sequence.pad_sequences(X_train, maxlen=maxlen)
X_test = sequence.pad_sequences(X_test, maxlen=maxlen)
print 'X_train	shape:', X_train.shape
print 'X_test	shape:', X_test.shape

Y_train = np_utils.to_categorical(y_train, 10)
Y_test = np_utils.to_categorical(y_test, 10)

model = Graph()
model.add_input(name='input', input_shape=(maxlen,))
model.add_node(Dense(1000, activation='relu'), name='dense1', input='input')
model.add_node(Dropout(0.5), name='dropout1', input='dense1')
model.add_node(Dense(600, activation='relu'), name='dense2', input='dropout1')
model.add_node(Dropout(0.5), name='dropout2', input='dense2')
model.add_node(Dense(10, activation='softmax'), name='soft_max', input='dense2')
model.add_output(name='output', input='soft_max')
model.compile('rmsprop', {'output':'categorical_crossentropy'})

history = model.fit({'input':X_train, 'output':Y_train}, nb_epoch=10)
model.save_weights('AUDNN.model', overwrite=False)

pred = np.array(model.predict({'input':X_test})['output'])
ac = 0
for i in range(0, len(X_test)):
    if np.argmax(Y_test[i]) == np.argmax(pred[i]):
        ac += 1
print 'Test per frame accuracy: ', float(ac) / float(len(X_test))

#test per VID
vid = data.get_testVID()
setvid = list(set(vid))
totalvid = np.zeros(len(setvid))
corrvid = np.zeros(len(setvid))

for temp in vid:
    totalvid[setvid.index(temp)] += 1
                                                                                      
for i in range(0, len(X_test)):
    if np.argmax(Y_test[i]) == np.argmax(pred[i]):
        corrvid[setvid.index(vid[i])] += 1

accmat = corrvid / totalvid

acc = 0
total = 0
for i in accmat:
    total += 1
    if i > 0.5:
        acc += 1
print 'Test per VID accuracy: ', float(acc) / float(total)




#https://github.com/fchollet/keras/blob/master/examples/imdb_bidirectional_lstm.py
#https://github.com/fchollet/keras/issues/1063
#http://keras.io/models/
