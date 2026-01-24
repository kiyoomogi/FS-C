# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 11:56:13 2025

@author: matthijs
"""

import os
import pandas as pd
import matplotlib.pyplot as plt 

# Directory containing the CSV files
directory = r"C:\Users\matthijs\simple_model\meshmaker_dummy\safe_states"

# List to store DataFrames
dfs = []

# Iterate over the files in the directory
for filename in os.listdir(directory):

    if filename.endswith('CONNE.csv'):
        # Read the CSV file
        df = pd.read_csv(os.path.join(directory, filename), skiprows=1)
        df = df.rename(columns=lambda x: x.strip())
        df.iloc[:, 0] = df.iloc[:, 0].shift(1)
        df = df.dropna()
        df = df.iloc[:, [0, -2]]
        df.iloc[:, 0] = df.iloc[:, 0].str.split(' ').str[-1].astype(float)
        # Append the DataFrame to the list
        dfs.append(df)

# Combine all DataFrames in the list into a single DataFrame
combined_df = pd.concat(dfs, ignore_index=True)
combined_df = combined_df.sort_values(by=combined_df.columns[0])
combined_df = combined_df.rename(columns={combined_df.columns[0]: 'TimeElapsed', combined_df.columns[-1]: 'GAS_INJEC'})
combined_df.GAS_INJEC = combined_df.GAS_INJEC * -1

initial_date = pd.to_datetime('2022-07-11 07:47:00')

# Calculate the corresponding date for each value in the "TIME_S" column
combined_df['Date'] = initial_date + pd.to_timedelta(combined_df['TimeElapsed'], unit='s')
# Export the DataFrame to a CSV file
combined_df.to_csv(r"C:\Users\matthijs\simple_model\meshmaker_dummy\safe_states\combined_gasrates_2-1L_lessrefill.csv", index=False)

plt.plot(combined_df.TimeElapsed, combined_df.GAS_INJEC, '-o')
plt.yscale('log')

# Load the second CSV
second_df = pd.read_csv(r"C:\Users\matthijs\simple_model\meshmaker\safe-states\combined_gasrates_v4.csv")

# Ensure column names match and are clean (adjust if needed)
second_df = second_df.rename(columns=lambda x: x.strip())
if 'TimeElapsed' not in second_df.columns:
    second_df = second_df.rename(columns={second_df.columns[0]: 'TimeElapsed', second_df.columns[-1]: 'GAS_INJEC'})

# Plot the second dataset on the same figure
plt.plot(second_df['TimeElapsed'], second_df['GAS_INJEC'], '-s', label='V4 Gas Rate')

# Final touches
plt.yscale('log')
plt.xlabel("Time Elapsed [s]")
plt.ylabel("Gas Injection Rate")
plt.legend(["2-1L less refill", "V4 gas rate"])
plt.grid(True)
plt.title("Comparison of Gas Injection Rates")
plt.tight_layout()
plt.show()
