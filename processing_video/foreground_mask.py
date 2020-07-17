from cv2 import bitwise_and

def compute_foreground_mask(place_mask, object_mask):
    return bitwise_and(object_mask, place_mask)