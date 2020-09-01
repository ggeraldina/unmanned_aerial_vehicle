def is_intersecting_rectangles(first_rectangle, second_rectangle):
    """ Пересекаются ли прямоугольники 

        Parameters
        ----------
        first_rectangle : (int, int, int, int)
            Координаты прямоугольника (x1, y1, x2, y2)
        second_rectangle : (int, int, int, int)
            Координаты прямоугольника (x1, y1, x2, y2)

        Returns
        -------
        True / False - пересекаются ли прямоугольники
    """
    r1_x1, r1_y1, r1_x2, r1_y2 = first_rectangle
    r2_x1, r2_y1, r2_x2, r2_y2 = second_rectangle
    if r1_x1 > r2_x2 or r1_x2 < r2_x1 or r1_y1 > r2_y2 or r1_y2 < r2_y1:
        return False
    return True


def is_intersecting_boxes(first_box, second_box):
    """ Пересекаются ли области 

        Parameters
        ----------
        first_rectangle : (int, int, int, int)
            Координаты области  (x1, y1, w, h)
        second_rectangle : (int, int, int, int)
            Координаты области (x1, y1, w, h)

        Returns
        -------
        True / False - пересекаются ли области
    """
    r1_x1, r1_y1, r1_w, r1_h = first_box
    r2_x1, r2_y1, r2_w, r2_h = second_box
    if r1_x1 > r2_x1 + r2_w or r1_x1 + r1_w < r2_x1 or r1_y1 > r2_y1 + r2_h or r1_y1 + r1_h < r2_y1:
        return False
    return True
