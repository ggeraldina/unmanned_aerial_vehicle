def compute_foreground_mask(place_mask, object_mask):
    place_mask = move_horizontally(place_mask, object_mask)
    place_mask = move_vertically(place_mask, object_mask)
    return place_mask

def move_horizontally(place_mask, object_mask):
    height, width = place_mask.shape
    for h in range(height):
        for w in  range(width - 1):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                if object_mask[h, w + 1] == 1:
                    place_mask[h, w + 1] = 1
        for w in range(width - 1, 0, -1):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                if object_mask[h, w + 1] == 1:
                    place_mask[h, w + 1] = 1
    return place_mask


def move_vertically(place_mask, object_mask):
    height, width = place_mask.shape
    for w in range(width):
        for h in range(height - 1):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                if object_mask[h + 1, w] == 1:
                    place_mask[h + 1, w] = 1
        for h in range(height - 1, 0, -1):
            if place_mask[h, w] == 1 and object_mask[h, w]:
                if object_mask[h + 1, w] == 1:
                    place_mask[h + 1, w] = 1
    return place_mask

