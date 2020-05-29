#!/usr/bin/python

import csv
import os.path
import sys

if ( (len(sys.argv) - 1 < 1) or ( not os.path.isfile(sys.argv[1]) ) ):
    print("Error: Input file name saved from Google Sheet must be provided as a parameter and exist.")
    exit(1)

input = sys.argv[1]
rfc = None
command_rows = {}
fieldnames = None

with open(input, "r") as proto_file:
    proto_reader = csv.DictReader(proto_file)
    for row in proto_reader:
        if row["RFC"] and 0 < len(row["RFC"]):
            rfc = row["RFC"]
        if (row["Command"] and 0 < len(row["Command"])) or (row["Response"] and 0 < len(row["Response"])):
            new_row = {
                "rfc": rfc,
                "command": row["Command"],
                "response": row["Response"],
                "topic": row["Topic"],
                "method": row["Method"],
                "operation": row["Operation"],
                "id": "Y" if row["Id"] and 0 < len(row["Id"]) else "",
                "data": "Y" if row["Data Parameter"] and 0 < len(row["Data Parameter"]) else "",
                "description": row["Description"],
                "id_details": row["Id"],
                "data_details": row["Data Parameter"],
                "result_details": row["Result"],
            }
            if not fieldnames:
                fieldnames = new_row.keys()
            row_key = (new_row["command"] + "_" +
                       new_row["response"] + "_" +
                       new_row["method"] + "_" +
                       new_row["topic"] + "_" +
                       new_row["method"] + "_" +
                       new_row["operation"] + "_" +
                       new_row["id"] + "_" +
                       new_row["data"])
            old_row = command_rows[row_key] if row_key in command_rows else {}
            for key, val in new_row.items():
                if (key not in old_row or not old_row[key] or 0 == len(old_row[key])):
                    old_row[key] = new_row[key]
            command_rows[row_key] = old_row

with open('../../aries-backchannel/data/backchannel_operations.csv', 'w') as command_file:
    writer = csv.DictWriter(command_file, fieldnames=fieldnames)
    writer.writeheader()
    for key, val in command_rows.items():
        writer.writerow(val)
