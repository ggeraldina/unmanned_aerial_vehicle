import argparse

from .converter import Converter


def parse():
    parser = argparse.ArgumentParser(
        description="This example demonstrates converting."
    )
    parser.add_argument("-csv", "--csv", type=str, help="path to csv file")
    return parser.parse_args()


args = vars(parse())
if not  args.get("csv", False):
    print("Нужно указать путь к csv. Параметр -csv или --csv.")
else: 
    converter = Converter(args["csv"])
    # converter.run_convert_csv()
    converter.run_convert_txt_drone_vs_bird()
