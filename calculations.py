import os
import pandas as pd
import datetime
import numpy as np

class Calculations:
    def __init__(self, files):
        self.trips = self.produce_trips_table(files)
        self.daily_counts = self.calculate_daily_counts(self.get_trips())
        self.monthly_counts = self.calculate_monthly_counts(self.get_trips())
    
    def get_trips(self):
        return self.trips

    def get_daily_counts(self):
        return self.daily_counts

    def get_monthly_counts(self):
        return self.monthly_counts

    def produce_trips_table(self, files):
        # DataFrame must have at least the 'Bikeid', 'Starttime', 'Trip id', 'From station id', 'To station id' columns
        masterdf = pd.DataFrame(columns=['Bikeid', 'Starttime', 'Trip id', 'From station id', 'To station id'])
        
        bikeids = []
        starttimes = []
        tripids = []
        fromids = []
        toids = []
        
        
        for file in files:
            curr = pd.read_csv(file)
                        
            # Transform each starttime into a datetime object
            for idx in range(len(curr['Starttime'])):
                bikeids.append(curr['Bikeid'][idx])
                tripids.append(curr['Trip id'][idx])
                fromids.append(curr['From station id'][idx])
                toids.append(curr['To station id'][idx])
                
                starttime = curr['Starttime'][idx].split(' ')
                date = starttime[0].split('/')
                time = starttime[1].split(':')
                
                month = int(date[0])
                day = int(date[1])
                year = int(date[2])
                hour = int(time[0])
                minute = int(time[1])
                
                dto = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
                
                starttimes.append(dto)
            
        masterdf['Bikeid'] = bikeids
        masterdf['Starttime'] = starttimes
        masterdf['Trip id'] = tripids
        masterdf['From station id'] = fromids
        masterdf['To station id'] = toids
        
        # masterdf.astype({'Bikeid': int, 'Trip id': int, 'From station id': int, 'To station id': int})
        
        # print(masterdf)
        return masterdf
    
    def calculate_daily_counts(self, trips):        
        # DataFrame must have "day", "station_id", "fromCNT", "toCNT" and "rebalCNT" columns
        from_df = trips[['Starttime', 'From station id']].copy()
        to_df = trips[['Starttime', 'To station id']].copy()
        
        # Get the counts by using groupby on the starttime then from/to station id. Get the counts by using size then convert
        # the resulting Series to a DF. 
        from_df = from_df.groupby([from_df["Starttime"].dt.date, "From station id"]).size().to_frame(name='fromCNT').reset_index()
        to_df = to_df.groupby([to_df["Starttime"].dt.date, "To station id"]).size().to_frame(name='toCNT').reset_index()
        
        # # Rename the column headers to the designated column headers in the README
        from_df = from_df.rename(columns={'Starttime': 'day', 'From station id': 'station_id'})
        to_df = to_df.rename(columns={'Starttime': 'day', 'To station id': 'station_id'})
        
        # Merge the two dataframes together
        master_df = pd.merge(from_df, to_df, on=['day', 'station_id'], how='outer')
        # Handle NaNs in the master
        master_df = master_df.fillna(0)
        
        # TODO: Compute rebalance by implementing proper algorithm
        # Use the approximation for rebalance
        master_df['rebalCNT'] = abs(master_df['fromCNT'] - master_df['toCNT'])

        # Handle proper date format
        new_days = []
        for idx in range(len(master_df['day'])):
            year_month_day = str(master_df['day'][idx]).split('-')
            year = year_month_day[0].zfill(4)
            month = year_month_day[1].zfill(2)
            day = year_month_day[2].zfill(2)
            
            new_day = f"{month}/{day}/{year}"
            new_days.append(new_day)
        
        master_df['day'] = new_days
        
        # Handle format of DF
        master_df = master_df.astype({'day': str, 'station_id': int, 'fromCNT': int, 'toCNT': int, 'rebalCNT': int})
        
        # print(master_df.head(10))
        return master_df

    def calculate_monthly_counts(self, trips):
        # DataFrame must have "month", "station_id", "fromCNT", "toCNT" and "rebalCNT" columns
        from_df = trips[['Starttime', 'From station id']].copy()
        to_df = trips[['Starttime', 'To station id']].copy()
        
        # Get the counts by using groupby on the starttime then from/to station id. Get the counts by using size then convert
        # the resulting Series to a DF. 
        from_df = from_df.groupby([from_df["Starttime"].dt.month, "From station id"]).size().to_frame(name='fromCNT').reset_index()
        to_df = to_df.groupby([to_df["Starttime"].dt.month, "To station id"]).size().to_frame(name='toCNT').reset_index()
        
        # # Rename the column headers to the designated column headers in the README
        from_df = from_df.rename(columns={'Starttime': 'month', 'From station id': 'station_id'})
        to_df = to_df.rename(columns={'Starttime': 'month', 'To station id': 'station_id'})
        
        # print(from_df)
        
        # Merge the two dataframes together
        master_df = pd.merge(from_df, to_df, on=['month', 'station_id'], how='outer')
        # Handle NaNs in the master
        master_df = master_df.fillna(0)
        
        # TODO: Compute rebalance by implementing proper algorithm
        # Use the approximation for rebalance
        master_df['rebalCNT'] = abs(master_df['fromCNT'] - master_df['toCNT'])
        
        # Handle proper date format
        new_months = []
        for idx in range(len(master_df['month'])):
            month = str(master_df['month'][idx]).zfill(2)
            
            # Year is only 2021 data
            new_month = f"{month}/2021"
            new_months.append(new_month)
        
        master_df['month'] = new_months
        
        # Handle format of DF
        master_df = master_df.astype({'month': str, 'station_id': int, 'fromCNT': int, 'toCNT': int, 'rebalCNT': int})

        return master_df
    
        
if __name__ == "__main__":
    calculations = Calculations(['HealthyRideRentals2021-Q1.csv', 'HealthyRideRentals2021-Q2.csv', 'HealthyRideRentals2021-Q3.csv'])
    print("-------------- Trips Table ---------------")
    print(calculations.get_trips())
    print()
    print("-------------- Daily Counts ---------------")
    print(calculations.get_daily_counts().head(10))
    print()
    print("------------- Monthly Counts---------------")
    print(calculations.get_monthly_counts().head(10))
    print()