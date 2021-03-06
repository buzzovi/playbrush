import pandas as pd
import numpy as np


class DataProc:
    def process(self, rawdataPath, groupPath):
        rawdata = pd.read_csv(rawdataPath, parse_dates=["TimestampUTC"])
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
        rawdata2 = rawdata1.groupby(["PlaybrushID", "track", "DayType"]).agg(
            {"TimestampUTC": "first", "TotalTime": "max"})

        # Join groups
        groups = pd.read_csv(groupPath)
        rawdata2.index = rawdata2.index.rename(['PBID', 'track', 'DayType'])
        task1 = pd.merge(rawdata2.reset_index(), groups, how="left", on=['PBID'])

        # Weekdays
        task1["Weekdays"] = task1["TimestampUTC"].dt.day_name()
        task1["Date"] = task1["TimestampUTC"].dt.date
        task1["Time"] = task1["TimestampUTC"].dt.time

        task11 = task1.groupby(["PBID", "Date", "Weekdays", "DayType"]).agg(
            {"group": "first", "TimestampUTC": "count", "TotalTime": "max"})
        task11 = task11.reset_index()
        task11["BrushCount"] = np.where(task11["TimestampUTC"] > 0, 1, 0)

        # Total brush session
        task12 = task11.pivot(index=["PBID", "group", "Weekdays"], columns=[
            "DayType"], values="BrushCount").fillna(0)
        task12["DayBrush"] = task12["Evening"] + task12["Morning"]
        task12["TwiceBrush"] = np.where(task12["DayBrush"] == 2, 1, 0)
        task12 = task12.reset_index()

        # Weekdays and brush session
        task13 = task12.groupby(["PBID", "group", "Weekdays"]).agg({"DayBrush": "sum", "TwiceBrush": "sum"})

        # 3 part with same key PBID, group
        # Weekdays columns
        task14 = task13.reset_index().pivot(index=["PBID", "group"], columns=["Weekdays"], values="DayBrush").fillna(0)
        task14 = task14.groupby(["PBID", "group"]).sum()

        # Brush session columns
        task15 = task13.groupby(["PBID", "group"]).agg({"DayBrush": "sum", "TwiceBrush": "sum"})

        # TotalTime columns
        task16 = task11.pivot(index=["PBID", "group", "Weekdays"], columns=[
            "DayType"], values="TotalTime").fillna(0)
        task16["DayTotalTime"] = task16["Evening"] + task16["Morning"]
        task16 = task16.groupby(["PBID", "group"]).agg({"DayTotalTime": "sum"})

        # Final table put together
        task1all = pd.merge(task14, task16, how="left", on=['PBID', 'group'])
        task1all = pd.merge(task1all, task15, how="left", on=['PBID', 'group'])
        task1all["AvgBrushTime"] = task1all["DayTotalTime"] / task1all["DayBrush"]
        task1csv = task1all[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                            "Saturday", "Sunday",  "DayBrush", "TwiceBrush", "AvgBrushTime"]]
        # Task 1 csv
        # "group,PBID,mon,tue,wed,thu,fri,sat,sun,total-brushes,twice-brushes,avg-brush-time"
        task1csv = task1csv.reset_index()
        task1csv = task1csv.rename(columns={"Monday": "mon", "Tuesday": "tue", "Wednesday": "wed", "Thursday": "thu", "Friday": "fri", "Saturday": "sat",
                                            "Sunday": "sun", "DayBrush": "total-brushes", "TwiceBrush": "twice-brushes", "AvgBrushTime": "avg-brush-time"}, errors="raise")
        # Task 2 answers
        task21 = task1all["DayBrush"].sum()
        task22 = task1all.groupby("group")["DayBrush"].mean().reset_index().rename(
            columns={"DayBrush": "Average number of brushing sessions"})
        task23 = task1all.groupby("group")["DayTotalTime"].mean().reset_index().rename(
            columns={"DayTotalTime": "Average brushing duration"})
        task24 = task1all.groupby("group")["DayTotalTime"].mean(
        ).reset_index().sort_values("DayTotalTime", ascending=False).rename(columns={"DayTotalTime": "Total brushing time"})

        return (task1csv, task21, task22, task23, task24)
        # task1[["PBID", "track",  "DayType", "TotalTime", "group", "Weekdays", "Date", "Time"]].to_excel("task1.xlsx")
