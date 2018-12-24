
transform_k_range = (0.8, 1.2)
MARKED = (0, 0, 0)
NON_MARKED = (255, 255, 255)


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
                pixels[(x, y)] = NON_MARKED
            else:
                pixels[(x, y)] = MARKED

    return image


def _get_largest_cluster_bounds(clusters, row_height):
    for i in range(len(clusters)):
        rect_count, bounds = clusters[i]
        if not rect_count:
            continue
        for j in range(i + 1, len(clusters)):
            other_rect_count, other_bounds = clusters[j]
            if not other_rect_count:
                continue
            if bounds[1][1] + row_height == other_bounds[0][1] and (
                other_bounds[0][0] < bounds[0][0] < other_bounds[1][0]
                or other_bounds[0][0] < bounds[1][0] < other_bounds[1][0]
            ):
                clusters[i][0] = rect_count + other_rect_count
                clusters[i][1] = (
                    (min(bounds[0][0], other_bounds[0][0]), bounds[0][1]),
                    (max(bounds[1][0], other_bounds[1][0]), other_bounds[1][1])
                )
                clusters[j] = clusters[i]
                break
    return max(clusters, key=lambda cluster: cluster[0])[1]


def recognize(image, rect_size, step_percent=0.5):
    size = image.size
    pixels = image.load()

    clusters = []
    rect_count = 0
    lower_left = (0, 0)
    upper_right = tuple(size)

    row_limit = size[1] // rect_size
    col_limit = size[0] // rect_size

    step_count = rect_size ** 2 * step_percent
    row_end_len = size[0] - col_limit * rect_size
    row_end_step_count = rect_size * row_end_len * step_percent
    for row in range(row_limit):
        for col in range(col_limit):
            count = 0
            for y in range(row * rect_size, (row + 1) * rect_size):
                for x in range(col * rect_size, (col + 1) * rect_size):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if count < step_count:
                # if rect_count > 1:
                clusters.append([rect_count, (lower_left, upper_right)])
                lower_left = col * rect_size, row * rect_size
                upper_right = lower_left[0] + rect_size, lower_left[1] * rect_size
                rect_count = 1
            else:
                upper_right = (col + 1) * rect_size, (row + 1) * rect_size
                rect_count += 1
        # process the end of the rows if width is not a multiple of the rect size (code duplication is intentional)
        if row_end_len:
            count = 0
            for y in range(row * rect_size, (row + 1) * rect_size):
                for x in range(col_limit * rect_size, size[0]):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if count < row_end_step_count:
                # if rect_count > 1:
                clusters.append([rect_count, (lower_left, upper_right)])
                lower_left = col_limit * rect_size, row * rect_size
                upper_right = size[0], lower_left[1] + rect_size
                rect_count = 1
            else:
                upper_right = size[0], (row + 1) * rect_size
                rect_count += 1
    # process the last row if height is not a multiple of the rect size (code duplication is intentional)
    last_row_height = size[1] - row_limit * rect_size
    if last_row_height:
        last_row_step_count = last_row_height * rect_size * step_percent
        for col in range(col_limit):
            count = 0
            for y in range(row_limit * rect_size, size[1]):
                for x in range(col * rect_size, (col + 1) * rect_size):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if count < last_row_step_count:
                # if rect_count > 1:
                clusters.append([rect_count, (lower_left, upper_right)])
                lower_left = col * rect_size, row_limit * rect_size
                upper_right = lower_left[0] + rect_size, size[1]
                rect_count = 1
            else:
                upper_right = (col + 1) * rect_size, size[1]
                rect_count += 1
        # process the end of the last row if width is not a multiple of the rect size (code duplication is intentional)
        if row_end_len:
            last_row_end_step_count = last_row_height * row_end_len * step_percent
            count = 0
            for y in range(row_limit * rect_size, size[1]):
                for x in range(col_limit * rect_size, size[0]):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if count < last_row_end_step_count:
                # if rect_count > 1:
                clusters.append([rect_count, (lower_left, upper_right)])
                lower_left = col_limit * rect_size, row_limit * rect_size
                upper_right = size
                rect_count = 1
            else:
                upper_right = size
                rect_count += 1
        # if rect_count > 1:
        clusters.append([rect_count, (lower_left, upper_right)])

    if not clusters:
        return lower_left, upper_right
    return _get_largest_cluster_bounds(clusters, rect_size)
