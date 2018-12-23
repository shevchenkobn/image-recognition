
transform_k_range = (0.8, 1.2)


def _average_pixel(pixel):
    return sum(pixel) / 3


def transform_image(image, k):
    image = image.copy()
    pixels = image.load()
    size = image.size

    pixel_sum = 0
    for y in range(size[1]):
        average_pixels = tuple(
            map(lambda x: _average_pixel(pixels[(x, y)]), range(size[0]))
        )
        max_average_pixel = max(average_pixels)
        for x in range(size[0]):
            pixel = average_pixels[x]
            pixel_sum += pixel
            if pixel_sum >= k * max_average_pixel:
                pixel_sum -= k * max_average_pixel
                pixels[(x, y)] = (255, 255, 255)
            else:
                pixels[(x, y)] = (0, 0, 0)

    return image


def recognize(image):
    return (1, 1), image.size
