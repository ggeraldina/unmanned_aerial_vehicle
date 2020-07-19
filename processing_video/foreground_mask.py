def compute_foreground_mask(place_mask, object_mask):
    place_mask = move_horizontally(place_mask, object_mask)
    place_mask = move_vertically(place_mask, object_mask)
    return place_mask

def move_horizontally(place_mask, object_mask):
    height, width = place_mask.shape
    radius = 10
    for h in range(height):
        for w in  range(width - radius):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                for i in range(1, radius + 1):
                    if object_mask[h, w + i] == 1:
                        place_mask[h, w + i] = 1
        for w in range(width - radius, 0, -1):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                for i in range(1, radius + 1):
                    if object_mask[h, w - i] == 1:
                        place_mask[h, w - i] = 1
    return place_mask


def move_vertically(place_mask, object_mask):
    height, width = place_mask.shape
    radius = 10
    for w in range(width):
        for h in range(height - radius):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                for i in range(1, radius + 1):
                    if object_mask[h + i, w] == 1:
                        place_mask[h + i, w] = 1
        for h in range(height - radius, 0, -1):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                for i in range(1, radius + 1):
                    if object_mask[h - i, w] == 1:
                        place_mask[h - i, w] = 1
    return place_mask

