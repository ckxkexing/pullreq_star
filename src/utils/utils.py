import csv
import datetime

def write_csv_data(csv_file_name, header, data):
    with open(csv_file_name, 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(data)

def time_handler(target_time: str):
    _date = datetime.datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%SZ")
    return _date

def str_handler(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')
