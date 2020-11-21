import argparse

from .scaler import Scaler


def parse():
    parser = argparse.ArgumentParser(
        description="This example demonstrates scaling."
    )
    parser.add_argument("-video", "--v", type=str, help="path to input video file")
    parser.add_argument("-csv", "--csv", type=str, help="path to input csv file")
    return parser.parse_args()


args = vars(parse())
if not (args.get("video", False) or args.get("csv", False)):
    print("Нужно указать путь к исходном файлам. Параметр -video и -csv.")
else: 
    scaler = Scaler(args["video"], args["csv"])
    scaler.run()
