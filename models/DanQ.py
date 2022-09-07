import tensorflow as tf
from models.BaseModel import BaseModel

# https://github.com/jiawei6636/Bioinfor-DanQ

class DanQ(BaseModel):
    def __init__(
        self, 
        filter=320, 
        kernel=26, 
        lstm_units=320, 
        dropout1=0.2,
        dropout2=0.5, 
        dense=925, 
        classes=919, 
        shape=(1000, 4),
        learning_rate=1e-3, 
        pool=13, 
        name='DanQ'
    ):
        super(DanQ, self).__init__(
            name=name,
            shape=shape, 
            classes=classes, 
            learning_rate=learning_rate,
        )
        self.filter = filter
        self.kernel = kernel
        self.dropout1 = dropout1
        self.dropout2 = dropout2
        self.dense = dense
        self.lstm_units = lstm_units
        self.pool = pool

        tf.random.set_seed(0)
        self.__build__()

    def __build__(
        self,
    ):
        input = tf.keras.layers.Input(shape=self.shape)

        conv = tf.keras.layers.Conv1D(
            self.filter, 
            kernel_size=self.kernel, 
            strides=1, 
            padding='valid', 
            activation='relu'
        )(input)
        pool = tf.keras.layers.MaxPool1D(
            pool_size=self.pool, 
            strides=self.pool, 
            padding='valid'
        )(conv)
        drop1 = tf.keras.layers.Dropout(self.dropout1)(pool)

        lstm = tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(units=self.lstm_units)
        )(drop1)
        drop2 = tf.keras.layers.Dropout(self.dropout2)(lstm)

        flat = tf.keras.layers.Flatten()(drop2)
        feed = tf.keras.layers.Dense(
            units=self.dense, 
            activation='relu'
        )(flat)
        output = tf.keras.layers.Dense(
            units=self.classes, 
            activation='sigmoid'
        )(feed)
        
        self.make_model(input, output)