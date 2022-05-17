# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
from my_functions import datestr_to_seconds
from my_functions import error_turnoff_model

# parameters:
dev_std = 0.5
T_init = 38.2 # average Ts for turning-off and no-change
# T_init = 36.5 # average Ts for door-open
# T_init = 37.6 # average Ts for door-ajar
max_error = 1.3
min_error = 2.0

# open and read the sensor data as pandas dataframe
# chose data to compare:

# 1) Incubator being turned off
# temp_data = pd.read_csv('LargeIncubator_TurnOff.csv', sep=',', header=0)

# 2) Incubator working well
# temp_data = pd.read_csv('LargeIncubator_NoChange.csv', sep=',', header=0)

# 3) Incubator with door completely open
temp_data = pd.read_csv('LargeIncubator_DoorOpen.csv', sep=',', header=0)

# 4) Incubator with door left ajar
# temp_data = pd.read_csv('LargeIncubator_DoorAjar.csv', sep=',', header=0)

# loop cycle: analyse data in subsets of 5 data points
# loop of 30 min

temperature_stable = True

for i in range(0,60):
    # select first 5 points (5 minutes approx):
    temp_subset = temp_data.loc[i:i + 4]

    if temperature_stable:
        # from timestamp to seconds:
        date_ref = temp_subset['timestamp'][i]
        seconds = []
        for date in temp_subset['timestamp']:
            seconds.append(datestr_to_seconds(date, date_ref))

        # re-order dataframe:
        pd.options.mode.chained_assignment = None
        temp_subset["Time (sec)"] = seconds
        temp_subset.drop('timestamp', inplace=True, axis=1)
        temp_subset = temp_subset[['Time (sec)', 'sensor1value']]

        # check if T_ave is higher/lower than "T_init +/- dev_std":
        if T_init - dev_std < temp_subset['sensor1value'].mean() < T_init + dev_std:
            print("Minute: ", i + 4, "- All good. The incubator is working as normal")
        # if deviation is bigger, compare with the TuningOnOff model:
        else:
            time = temp_subset['Time (sec)']
            temperature_data = temp_subset['sensor1value']
            initial_temperature = T_init
            error = error_turnoff_model(time, temperature_data, initial_temperature)
            if error < max_error:
                print("Minute: ", i + 4, "- Warning! The incubator seems to be turned off")
                temperature_stable = False
                date0 = date_ref
            elif error > min_error:
                print("Minute: ", i + 4, "- Analysis inconclusive. The incubator might be open")

    else:
        seconds = []
        for date in temp_subset['timestamp']:
            seconds.append(datestr_to_seconds(date, date0))

        # re-order dataframe:
        pd.options.mode.chained_assignment = None
        temp_subset["Time (sec)"] = seconds
        temp_subset.drop('timestamp', inplace=True, axis=1)
        temp_subset = temp_subset[['Time (sec)', 'sensor1value']]

        time = temp_subset['Time (sec)']
        temperature_data = temp_subset['sensor1value']
        initial_temperature = T_init
        error = error_turnoff_model(time, temperature_data, initial_temperature)
        if error < max_error:
            print("Minute: ", i + 4, "- Warning! The incubator seems to be turned off")
            temperature_stable = False
        elif error > min_error:
            print("Minute: ", i + 4, "- Analysis inconclusive. The incubator might be open")

