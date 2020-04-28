import csv


with open("../Mapping Aries Protocols for Testing - Aries Agent Test Scripts.csv", "r", newline='') as proto_file:
    proto_reader = csv.DictReader(proto_file)
    for row in proto_reader:
        print(
            row["Backchannel Endpoint"],
            row["Method"],
            row["Operation"],
            row["Id"],
            row["Data Parameter"],
            row["Description"],
            row["Data Parameter"],
            row["Response"],
        )
