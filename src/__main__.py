import argparse
from video import run


def parse():
    parser = argparse.ArgumentParser(
        description="This example demonstrates searching for moving objects."
    )
    parser.add_argument("-v", "--video", type=str, help="path to video file")
    return parser.parse_args()


args = parse()
if not args.video:
    print("Нужно указать путь к видео. Параметр -v или --video.")
else:
    run(args.video)
