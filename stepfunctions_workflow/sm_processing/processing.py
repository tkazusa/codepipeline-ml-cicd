import argparse
import os

import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default=None)

    args, _ = parser.parse_known_args()

    input_data_path = os.path.join(args.input_dir, "train.csv")
    output_data_path = os.path.join(args.output_dir, "preprocessed.csv")

    data = pd.read_csv(input_data_path)
    data.to_csv(output_data_path, header=False, index=False)
