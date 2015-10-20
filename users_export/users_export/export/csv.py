import csv


def writefile(filename, header, data):
    with open(filename, 'w') as csvfile:
        filewriter = csv.writer(
            csvfile, delimiter=',', quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(header)
        for line in data:
            filewriter.writerow(line)
