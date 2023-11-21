import csv
from collections import defaultdict

def find_and_sort_duplicates(input_file, output_file):
    # Dictionary to store rows based on the fourth column value
    fourth_column_values = defaultdict(list)

    # Read the CSV file and group rows by the fourth column value
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header
        for row in reader:
            fourth_column_values[row[3]].append(row)

    # Write rows with duplicate fourth column values to a new CSV file, sorted by hash
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the header
        for _, rows in sorted(fourth_column_values.items()):
            if len(rows) > 1:
                # Sort rows by hash (assuming hash is in the 5th column, adjust if needed)
                sorted_rows = sorted(rows, key=lambda x: x[4])
                writer.writerows(sorted_rows)

def find_duplicate_rows(input_file, output_file):
    # Dictionary to store rows based on the fourth column value
    fourth_column_values = defaultdict(list)

    # Read the CSV file and group rows by the fourth column value
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header
        for row in reader:
            fourth_column_values[row[3]].append(row)

    # Write rows with duplicate fourth column values to a new CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the header
        for _, rows in fourth_column_values.items():
            if len(rows) > 1:
                writer.writerows(rows)

if __name__ == "__main__":
    input_csv = '/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/output.csv'
    output_csv = '/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/duplicate_rows.csv'

    #find_duplicate_rows(input_csv, output_csv)
    find_and_sort_duplicates(input_csv, output_csv)
