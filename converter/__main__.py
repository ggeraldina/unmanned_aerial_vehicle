import argparse

from .converter import Converter


def parse():
    parser = argparse.ArgumentParser(
        description="This example demonstrates converting."
    )
    parser.add_argument("-input", "--input", type=str, help="path to input file")
    return parser.parse_args()


args = vars(parse())
if not  args.get("input", False):
    print("Нужно указать путь к исходному файлу. Параметр -input или --input.")
else: 
    converter = Converter(args["input"])
    converter.convert_my_csv_to_my_xml()
    # converter.convert_txt_drone_vs_bird_to_my_xml()
