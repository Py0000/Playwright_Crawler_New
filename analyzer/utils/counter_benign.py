import argparse
import os

class Counter:
    def __init__(self):
        self.accumulated = 0
    
    def count(self, dataset_path):
        total_count = 0
        files = os.listdir(dataset_path)
        folder_count = sum(1 for file in files if file.endswith(".zip"))
        total_count += folder_count

        print(folder_count)
        print(total_count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset_path", help="Dataset Path")
    args = parser.parse_args()

    counter = Counter()
    counter.count(args.dataset_path)



