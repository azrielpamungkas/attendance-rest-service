import csv

with open("/home/pamungkas/Dev/apii/pop/siamawolu_sb.csv") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        print(row)
