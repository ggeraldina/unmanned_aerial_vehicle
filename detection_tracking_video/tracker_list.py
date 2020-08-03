from .utils import is_intersecting_boxes


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
        if box == (0, 0, 0, 0):
            return
        tracker.init(frame, box)
        self._trackers.append(tracker)
        self._current_boxes.append(box)

    def add_with_update(self, tracker, frame, box):
        """ Добавить или обновить трекер 

        Parameters
        ----------
        tracker: TrackerXXX
            Трекер
        frame: array([...], dtype=uint8)
            Текущий кадр
        box: (int, int, int, int)
            (x, y, w, h) - характеристики прямоугольника
        """
        if box == (0, 0, 0, 0):
            return
        update_tracker = False
        amount_del_trackers = 0
        tracker.init(frame, box)
        for i, current_box in enumerate(self._current_boxes):
            if is_intersecting_boxes(box, current_box):
                if update_tracker:
                    del self._trackers[i - amount_del_trackers]
                    del self._current_boxes[i - amount_del_trackers]
                    amount_del_trackers += 1
                    continue
                self._trackers[i - amount_del_trackers] = tracker
                self._current_boxes[i] = box
                update_tracker = True
        if not update_tracker:
            self._trackers.append(tracker)
            self._current_boxes.append(box)

    def delete(self, box):
        """ Удалить объект из отслеживаемых 

        Parameters
        ----------        
        box: (int, int, int, int)
            (x, y, w, h) - характеристики области

        Returns
        -------
        int - Количество удаленных трекеров
        """
        amount_del_trackers = 0
        for i, current_box in enumerate(self._current_boxes):
            if is_intersecting_boxes(box, current_box):
                del self._trackers[i - amount_del_trackers]
                del self._current_boxes[i - amount_del_trackers]
                amount_del_trackers += 1
        return amount_del_trackers

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

    def get_count_current_boxes(self):
        """ Вернуть количество отсеживаемых объектов """
        return self._current_boxes.__len__()
