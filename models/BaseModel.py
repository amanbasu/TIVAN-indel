import tensorflow as tf

class BaseModel:
    def __init__(
        self, 
        classes=919, 
        shape=(1000, 4), 
        learning_rate=1e-3,
        name='BaseModel'
    ):
        self.checkpoint = f'../checkpoint/{name}'
        self.classes = classes
        self.shape = shape
        self.learning_rate = learning_rate
        self.name = name
        self.model = None
    
    def __build__(
        self,
    ):
        # add your model implementation in the child class
        pass

    def scheduler(
        self, 
        epoch, 
        lr
    ):
        if epoch < 5:
            return lr
        else:
            return lr * tf.math.exp(-0.1)

    def fit(
        self, 
        dataiter, 
        epochs=200, 
        validation_data=None
    ):
        learning_rate = tf.keras.callbacks.LearningRateScheduler(self.scheduler)
        early_stop = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=5, 
            mode='auto', 
            restore_best_weights=True
        )
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            self.checkpoint,
            monitor='val_loss',
            verbose=0,
            save_weights_only=True,
            mode='auto',
            save_freq='epoch'
        )
        self.model.fit(
            dataiter, 
            epochs=epochs, 
            callbacks=[early_stop, learning_rate, checkpoint], 
            validation_data=validation_data, 
            verbose=1
        )

    def predict(
        self, 
        x
    ):
        return self.model.predict(x)

    def save_model(
        self, 
        model_name
    ):
        self.model.save(model_name)

    def make_model(
        self,
        input,
        output,
        loss='binary_crossentropy'
    ):
        self.model = tf.keras.models.Model(
            inputs=input, outputs=output, name=self.name
        ) 
        opt = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)

        self.model.compile(
            optimizer=opt, 
            loss=loss, 
            metrics=[tf.keras.metrics.AUC(name='auc')]
        ) 

        try:
            self.model.load_weights(self.checkpoint)
            print('weights loaded from', self.checkpoint)
        except Exception as e:
            print('no weights at', self.checkpoint)
            print(e)