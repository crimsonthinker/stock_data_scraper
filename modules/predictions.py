import pandas as pd
from utils.generic_utils import get_engine, correct_nan_val
from typing import List
import pickle
import numpy as np
import collections
import tensorflow as tf

from keras.models import Model
from keras.layers import Dense, LSTM, Dropout, Attention, BatchNormalization, Input, Conv1D, TimeDistributed, Flatten
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam
from keras import regularizers

from sklearn.model_selection import train_test_split

from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os

def lstm_cnn_model(input_shape : tuple, time_span : int):
    inputs = Input(shape=input_shape)

    lstm_freeze = LSTM(64,return_sequences = True, activation = 'relu', kernel_regularizer=regularizers.l2(0.2))(inputs)
    cnn_freeze = Conv1D(filters=64, kernel_size=2, strides=1, padding='same',  activation = 'relu', kernel_regularizer=regularizers.l2(0.2))(lstm_freeze)
    
    lstm_query = LSTM(64,return_sequences = True)(cnn_freeze)
    lstm_val = LSTM(64,return_sequences = True)(lstm_query)
    attention_lstm = Attention()([lstm_val, lstm_query])
    drop_1 = Dropout(0.3)(attention_lstm)

    cnn_query = Conv1D(filters=64, kernel_size=2, strides=1, padding='same')(drop_1)
    cnn_val = Conv1D(filters=64, kernel_size=2, strides=1, padding='same')(cnn_query)
    attention_cnn = Attention()([cnn_val, cnn_query])
    drop_2 = Dropout(0.3)(attention_cnn)

    lstm_last = LSTM(time_span,return_sequences = False, activation = None, kernel_regularizer=regularizers.l2(0.5))(drop_2)
    outputs = Dense(time_span)(lstm_last)

    model = Model(inputs = inputs, outputs = outputs)
    model.compile(optimizer=Adam(lr=1e-3), loss='mean_squared_error')
    model.summary()

    return model


def close_price_future_prediction(
    models : dict,
    scalers : dict,
    plan_range : int,
    predictor_features : list
):
    engine = get_engine(country = 'AU')

    dfs = {}
    lookback_window = plan_range * 5
    fig = make_subplots(rows = len(models), cols = 1)
    for num,stock_code in enumerate(models):
        query = f"""
            SELECT
                date,
                open,
                high,
                low,
                close,
                volume
            FROM transaction
            WHERE 
                stock_code = '{stock_code}'
            ORDER BY date DESC
            LIMIT {lookback_window}
        """
        df = pd.read_sql_query(query, engine)
        dfs[stock_code] = correct_nan_val(df, lookback_window)

        # Extract to time series data
        stock_data = dfs[stock_code]
        stock_data = stock_data[predictor_features].to_numpy()

        x_pred = []
        for i in range(0,len(stock_data), plan_range):
            x_pred.append(stock_data[i:i + plan_range,:])
        x_pred = np.array(x_pred)
        for n,feat in enumerate(predictor_features):
            x_pred[:,:,n] = (x_pred[:,:,n] - scalers[stock_code][feat]['mean']) / scalers[stock_code][feat]['std']
        
        # predict
        y_pred = models[stock_code].predict(x_pred)
        # Revert to original data
        y_pred = y_pred * scalers[stock_code]['close']['std'] + scalers[stock_code]['close']['mean']
        y_pred = y_pred.flatten()

        # Add some additional dates
        start_date = datetime.strptime(dfs[stock_code]['date'].iloc[plan_range], '%Y-%m-%d')
        new_dates = []
        while len(new_dates) < len(y_pred):
            start_date = start_date + timedelta(days = 1)
            if start_date.weekday() not in [5,6]:
                new_dates.append(start_date)
        prediction_df = pd.DataFrame({'date' : new_dates, 'close' : y_pred})

        fig.add_trace(
            go.Scatter(
                x = prediction_df['date'], 
                y = prediction_df['close'], 
                name = 'Predict', 
                markers=dict(color='red'),
                showlegend = num == 0
            ),
            row = num + 1, col = 1
        )


        fig.add_trace(
            go.Scatter(
                x = dfs[stock_code]['date'], 
                y = dfs[stock_code]['close'], 
                name = 'True', 
                markers=dict(color='blue'),
                showlegend = num == 0
            ),
            row = num + 1, col = 1
        )
    fig.update_layout(height = 1000)
    return fig
        










