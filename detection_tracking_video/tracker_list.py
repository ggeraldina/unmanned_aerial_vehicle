from .utils import is_intersecting_rectangles
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
        update_tracker = False
        amount_del_trackers = 0
        tracker.init(frame, box)
        x1, y1, w, h = box
        x2, y2 = x1 + w, y1 + h
        for i, current_box in enumerate(self._current_boxes):
            x1_2, y1_2, w_2, h_2 = current_box
            x2_2, y2_2 = x1_2 + w_2, y1_2 + h_2
            if is_intersecting_rectangles((x1, y1, x2, y2), (x1_2, y1_2, x2_2, y2_2)):
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
        x1, y1, w, h = box
        x2, y2 = x1 + w, y1 + h        
        for i, current_box in enumerate(self._current_boxes):
            x1_2, y1_2, w_2, h_2 = current_box
            x2_2, y2_2 = x1_2 + w_2, y1_2 + h_2
            if is_intersecting_rectangles((x1, y1, x2, y2), (x1_2, y1_2, x2_2, y2_2)):
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

            