import pandas as pd
import numpy as np

csv_path = "playbrush/"
rawdata = pd.read_csv(csv_path+"data/1_rawdata.csv", parse_dates=["TimestampUTC"])
rawdata = rawdata.sort_values(by=["PlaybrushID", "TimestampUTC"])

# Merge brush sessions that are less than 2minutes apart into a single brush session.

rawdata["delta"] = (rawdata["TimestampUTC"]-rawdata["TimestampUTC"].shift()).fillna(pd.Timedelta(seconds=0))
# rawdata["delta2"] = rawdata["TimestampUTC"].diff()
rawdata["new_track"] = rawdata["delta"] > pd.Timedelta(minutes=2)
rawdata["track"] = pd.to_numeric(rawdata.groupby(["PlaybrushID"])["new_track"].cumsum(), downcast="integer")
rawdata1 = rawdata.groupby(["PlaybrushID", "track"]).agg(
    {"TimestampUTC": "min", "UpTime": "sum", "DownTime": "sum", "LeftTime": "sum", "RightTime": "sum", "NoneTime": "sum"})

# The total length of a brush session is the sum of the up, down, left, right and none times.
rawdata1["TotalTime"] = rawdata1["UpTime"] + rawdata1["DownTime"] + \
    rawdata1["LeftTime"] + rawdata1["RightTime"] + rawdata1["NoneTime"]

# Discard brush sessions that are less than 20 seconds in total
rawdata1 = rawdata1[rawdata1["TotalTime"] > 20]

# When a user brushes multiple times in a morning or an evening, record the longest brush and discard the others.
rawdata1["DayType"] = np.where(rawdata1["TimestampUTC"].dt.hour > 13, "Evening", "Morning")
rawdata2 = rawdata1.groupby(["PlaybrushID", "track", "DayType"]).agg({"TimestampUTC": "first", "TotalTime": "max"})

# Join groups
groups = pd.read_csv(csv_path+"data/2_groups.csv")
rawdata2.index = rawdata2.index.rename(['PBID', 'track', 'DayType'])
task1 = pd.merge(rawdata2.reset_index(), groups, how="left", on=['PBID'])

# Weekdays
task1["Weekdays"] = task1["TimestampUTC"].dt.day_name()
task1["Date"] = task1["TimestampUTC"].dt.date
task1["Time"] = task1["TimestampUTC"].dt.time
# task1['TimestampUTC'] = task1['TimestampUTC'].apply(lambda a: pd.to_datetime(a).date())


task11 = task1.groupby(["PBID", "Date", "Weekdays", "DayType"]).agg(
    {"group": "first", "TimestampUTC": "count", "TotalTime": "max"})
task11 = task11.reset_index()
task11["BrushCount"] = np.where(task11["TimestampUTC"] > 0, 1, 0)

task12 = task11.pivot(index=["PBID", "group", "Weekdays"], columns=[
                      "DayType"], values="BrushCount").fillna(0)
task12["DayBrush"] = task12["Evening"] + task12["Morning"]
task12["TwiceBrush"] = np.where(task12["DayBrush"] == 2, 1, 0)

# task12 = task12.drop(columns=['BrushCount', 'TotalTime'], level=0)
# task12 = task12.drop(index="DayType", level=0)
task12 = task12.reset_index()

task13 = task12.groupby(["PBID", "group", "Weekdays"]).agg({"DayBrush": "sum", "TwiceBrush": "sum"})

task14 = task13.pivot(index=["PBID", "group"], columns=["Weekdays"], values="DayBrush").fillna(0)
task14 = task14.groupby(["PBID", "group"]).sum()

task15 = task13.groupby(["PBID", "group"]).agg({"DayBrush": "sum", "TwiceBrush": "sum"})

task16 = task11.pivot(index=["PBID", "group", "Weekdays"], columns=[
                      "DayType"], values="TotalTime").fillna(0)
task16["DayTotalTime"] = task16["Evening"] + task16["Morning"]
task16 = task16.groupby(["PBID", "group"]).agg({"DayTotalTime": "sum"})

task1all = pd.merge(task14, task16, how="left", on=['PBID', 'group'])
task1all = pd.merge(task1all, task15, how="left", on=['PBID', 'group'])
task1all = task1all[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                     "Saturday", "Sunday",  "DayBrush", "TwiceBrush", "DayTotalTime"]]

task21 = task1all["DayBrush"].sum()
task22 = task1all.groupby("group")["DayBrush"].mean()
task23 = task1all.groupby("group")["DayTotalTime"].mean()

task1[["PBID", "track",  "DayType", "TotalTime", "group", "Weekdays", "Date", "Time"]].to_excel("task1.xlsx")
