import csv


def write_csv_data(csv_file_name, header, data):
    with open(csv_file_name, "w") as f:
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(data)
