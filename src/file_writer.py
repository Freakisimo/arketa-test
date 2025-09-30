
import json
import csv
import os

class FileWriter:
    """
    A class to write data to JSON and CSV files.
    """
    def __init__(self, output_dir='data'):
        """
        Initializes the file writer.

        :param output_dir: The directory where the files will be saved.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def write_to_json(self, data, filename):
        """
        Writes data to a JSON file.

        :param data: The data to write.
        :param filename: The name of the JSON file (without the extension).
        """
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filepath}")

    def write_to_csv(self, data, filename, header_map=None):
        """
        Writes data to a CSV file, with an option to map data keys to CSV headers.

        :param data: The data to write (must be a list of dictionaries).
        :param filename: The name of the CSV file (without the extension).
        :param header_map: Optional dictionary to map data keys to CSV headers. 
                         Example: {'User ID': 'externalId', 'Reason': 'reason'}
        """
        if not data or not isinstance(data, list) or not isinstance(data[0], dict):
            print("Error: Data for CSV must be a list of dictionaries.")
            return

        filepath = os.path.join(self.output_dir, f"{filename}.csv")

        if header_map:
            fieldnames = list(header_map.keys())
            processed_data = [
                {header: item.get(original_key) for header, original_key in header_map.items()}
                for item in data
            ]
            data_to_write = processed_data
        else:
            fieldnames = list(data[0].keys())
            data_to_write = data

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_to_write)
        print(f"Data saved to {filepath}")

