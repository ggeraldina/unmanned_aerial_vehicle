import argparse

from .video import Video


def parse():
    parser = argparse.ArgumentParser(
        description="This example demonstrates searching for moving objects."
    )
    parser.add_argument("-v", "--video", type=str, help="path to video file")
    parser.add_argument("-sv", "--saving_videos", type=bool, help="saving video")
    parser.add_argument("-shm", "--showing_mask", type=bool, help="showing mask")
    return parser.parse_args()


args = parse()
if not args.video:
    print("Нужно указать путь к видео. Параметр -v или --video.")
else:    
    saving_videos = args.saving_videos if not args.saving_videos is None else False
    showing_mask = args.showing_mask if not args.showing_mask is None else False
    video = Video(args.video,saving_videos=saving_videos, showing_mask=showing_mask)
    video.run()
