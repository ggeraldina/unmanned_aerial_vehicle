class TrackerList: 
    """ Трекеры

    Attributes
    ----------
    _trackers: [TrackerXXX...]
        Трекеры
    _current_boxes: [(int, int, int, int)...]
        Текущие отслеживаемые области
    """
    def __init__(self):
        self._trackers = []
        self._current_boxes = []

    def add(self, tracker, frame, box):
        """ Добавить трекер 
        
        Parameters
        ----------
        tracker: TrackerXXX
            Трекер
        frame: array([...], dtype=uint8)
            Текущий кадр
        box: (int, int, int, int)
            (x, y, w, h) - характеристики прямоугольника
        """
        tracker.init(frame, box)
        self._trackers.append(tracker)

    def update(self, frame):
        """ Обновить трекеры

        Parameters
        ----------
        frame: array([...], dtype=uint8)
            Текущий кадр

        Returns
        -------
        (success, [(x, y, w, h), ...]) - Не потеряны ли объекты и координаты углов прямоугольников
        """
        boxes_success = True
        self._current_boxes = []
        for tracker in self._trackers:
            (success, box) = tracker.update(frame)
            if not success:
                boxes_success = False
            self._current_boxes.append(box)
        return boxes_success, self._current_boxes

            