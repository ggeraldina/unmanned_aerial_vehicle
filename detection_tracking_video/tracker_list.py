class TrackerList:
    def __init__(self):
        self._trackers = []
        self._current_boxes = []

    def add(self, tracker, frame, box):
        tracker.init(frame, box)
        self._trackers.append(tracker)

    def update(self, frame):
        boxes_success = True
        self._current_boxes = []
        for tracker in self._trackers:
            (success, box) = tracker.update(frame)
            if not success:
                boxes_success = False
            self._current_boxes.append(box)
        return boxes_success, self._current_boxes

            