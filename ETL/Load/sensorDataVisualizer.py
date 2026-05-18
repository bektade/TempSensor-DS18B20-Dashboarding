import argparse
import glob
import os
import sys
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, DateFormatter

LOAD_DIR = os.path.dirname(os.path.abspath(__file__))
ETL_DIR = os.path.dirname(LOAD_DIR)
TRANSFORM_DIR = os.path.join(ETL_DIR, 'Transform')
EXTRACT_DIR = os.path.join(ETL_DIR, 'Extract')

sys.path.insert(0, TRANSFORM_DIR)
from coalesce_sensor_data import coalesce_sensor_csvs, group_rows_by_sensor


class SensorDataVisualizer:
    def __init__(self, csv_dir=EXTRACT_DIR, time_window_minutes=90, include_archive=True):
        self.csv_dir = csv_dir
        self.time_window = timedelta(minutes=time_window_minutes)
        self.include_archive = include_archive
        self.data = {}

    def find_csv_files(self):
        csv_files = sorted(glob.glob(os.path.join(self.csv_dir, '*.csv')))
        csv_files = [
            path for path in csv_files
            if not os.path.basename(path).startswith('coalesced_')
        ]
        if self.include_archive:
            archive_dir = os.path.join(self.csv_dir, 'archive')
            csv_files += sorted(glob.glob(os.path.join(archive_dir, '*.csv')))
        return csv_files

    def load_data(self):
        csv_files = self.find_csv_files()
        rows = coalesce_sensor_csvs(csv_files)
        self.data = group_rows_by_sensor(rows)
        self._filter_to_time_window()

    def _filter_to_time_window(self):
        cutoff = datetime.now() - self.time_window
        filtered = {}
        for label, points in self.data.items():
            recent = [(timestamp, temp_c) for timestamp, temp_c in points if timestamp >= cutoff]
            if recent:
                filtered[label] = recent
        self.data = filtered

    def plot(self):
        if not self.data:
            raise RuntimeError('No sensor data found in the last {} minutes.'.format(int(self.time_window.total_seconds() / 60)))

        fig, ax = plt.subplots(figsize=(12, 6))

        for label, points in self.data.items():
            if not points:
                continue
            times = [t for t, _ in points]
            temps = [temp for _, temp in points]
            ax.plot(times, temps, marker='o', label=label)

        ax.set_title('DS18B20 Sensor Temperature (last {} minutes)'.format(int(self.time_window.total_seconds() / 60)))
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature (°C)')
        ax.legend()
        ax.grid(True)

        locator = AutoDateLocator()
        formatter = DateFormatter('%I:%M %p')
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate()
        plt.tight_layout()
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Visualize DS18B20 sensor CSV data over the last 90 minutes.')
    parser.add_argument('--csv-dir', default=EXTRACT_DIR, help='Directory containing sensor CSV files')
    parser.add_argument('--minutes', type=int, default=90, help='Time window in minutes to visualize')
    parser.add_argument('--no-archive', action='store_true', help='Do not include archived CSV files')
    args = parser.parse_args()

    visualizer = SensorDataVisualizer(
        csv_dir=args.csv_dir,
        time_window_minutes=args.minutes,
        include_archive=not args.no_archive,
    )
    visualizer.load_data()
    visualizer.plot()


if __name__ == '__main__':
    main()
