This is the set of code to process the Minilog (and other probe data) after it has been exported as a csv with EST times.
This code is very ugly and really not worth sharing with anyone. It was hacked at for 20 years and got very messy.

emolt_pd.py - cleans with both a) an empirical range & delta check and b) graphically displays the time series to visually inspect.
emolt2_pd.py - plots this years data on top of all those in the database for a particular site code
bill_adler.py -  plots this years data on top of the climatological mean and grayed area of standard deviations
plot_emolt_annual.py - plots annual averages
