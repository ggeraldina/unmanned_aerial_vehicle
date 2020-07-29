class TrackerList:
    def __init__(self):
        self._trackers = []

    def add(self, tracker, frame, box):
        tracker.init(frame, box)
        self._trackers.append(tracker)

    def update(self, frame):
        boxes_success = True
        boxes = []
        for tracker in self._trackers:
            (success, box) = tracker.update(frame)
            if not success:
                boxes_success = False
            boxes.append(box)
        return boxes_success, boxes

            