import pandas as pd
import numpy as np

def mso_get_period_and_duty(digital_data, digital_timestamps, digitalToGet):
    digital_data = [x+32 for x in digital_data]
    data = [[int(x) for x in bin(y)[2:]] for y in digital_data]
    df = pd.DataFrame(data, columns=['1','D4', 'D3', 'D2', 'D1', 'D0'])
    data = np.array(df[digitalToGet])
    # Get the periods and frequencies
    rising = np.flatnonzero((data[:-1] == 0) & (data[1:] == 1))+1
    falling = np.flatnonzero((data[:-1] == 1) & (data[1:] == 0))+1
    #print(rising)
    #print(falling)
    timeRising = [digital_timestamps[x] for x in rising]
    timeFalling = [digital_timestamps[x] for x in falling]
    #print(timeRisingD4)
    #print(timeFallingD4)
    periodRising = [timeRising[i+1]-timeRising[i] for i in range(len(timeRising)-1)]
    #print(periodRisingD4)
    period = sum(periodRising)/len(periodRising)
    freq = 1e9 / period

    # Get the duty
    if timeRising[0] > timeFalling[0]:
        timeFalling = timeFalling[1:]
    min_len = min(len(timeRising), len(timeFalling))
    TOns = [timeFalling[x]-timeRising[x] for x in range(min_len)]
    TOn_average = sum(TOns)/len(TOns)
    #print(TOn_average)
    duty = 100*TOn_average/period

    return duty, freq