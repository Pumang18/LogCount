import os
import argparse
from collections import Counter
import csv
import gzip
import configparser

# Load config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
output_file_path=config["paths"]["OUTPUT_FILE_PATH"]
threshold_value=config["constant"]["THRESHOLD"]

class LogLine:
    def __init__(self, line, matching_line, count=1):
        self.line = line
        self.matching_line = matching_line
        self.count = count

    def increment(self):
        self.count += 1

def compare(line1, line2, threshold=float(threshold_value)):
    count1 = Counter(line1)
    count2 = Counter(line2)

    intersection_size = sum((count1 & count2).values())

    max_size = max(sum(count1.values()), sum(count2.values()))

    if max_size == 0:
        return False

    similarity_score = intersection_size / max_size

    return similarity_score > threshold

def process_lines(file_path):
    try:
        log_dict = {}
        line_count = 0

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line_count += 1
                if line_count % 50000 == 0:
                    print("{0} lines processed".format(line_count))

                if " ERROR " in line:
                    split_string_from = " ERROR "
                elif " WARN " in line:
                    split_string_from = " WARN "
                else:
                    continue

                stripped_line = line[line.index(split_string_from):].lower()

                found = False
                for key in log_dict:
                    if compare(key, stripped_line):
                        log_dict[key].increment()
                        found = True
                        break

                if not found:
                    log_dict[stripped_line] = LogLine(line, stripped_line)

        return log_dict.values()
    except Exception as e:
        print("Some Error Occurred: {0}".format(e))

def main(file_name):


    print("Reading file {0}".format(file_name))
    print("Parsing lines")


    output_file = os.path.join(output_file_path, f"{os.path.splitext(os.path.basename(file_name))[0]}_output.csv")

    processed_lines = process_lines(file_name)

    final_results = sorted(processed_lines, key=lambda x: x.count, reverse=True)

    if os.path.exists(output_file):
        os.remove(output_file)

    with open(output_file, 'w') as file:
        writer = csv.writer(file)
        field = ["Incident_Count", "Incident"]
        writer.writerow(field)
        for log_line in final_results:
            # writer.writerow([f"{log_line.count}",f"{log_line.line}"])
            writer.writerow([log_line.count,log_line.line])

    print("Lines Parsed Successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process log files and aggregate similar error and warning messages.")
    parser.add_argument("file_name", type=str, help="The name of the log file to process.")
    args = parser.parse_args()

    main(args.file_name)