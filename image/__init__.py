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


def _get_largest_cluster_bounds(clusters, row_height, last_row_height):
    for row in range(len(clusters)):
        row_clusters = clusters[row]
        for i in range(len(row_clusters)):
            cl_info, x_bounds = row_clusters[i][:2]
            rect_count, pixel_count = cl_info
            if len(row_clusters[i]) is not 3:
                row_clusters[i].append(i)
            for other_row in range(row + 1, len(clusters)):
                for j in range(len(clusters[other_row])):
                    other_cl_info, other_x_bounds = clusters[other_row][j][:2]
                    other_rect_count, other_pixel_count = other_cl_info
                    if (
                            other_x_bounds[0] <= x_bounds[0] < other_x_bounds[1]
                            or other_x_bounds[0] < x_bounds[1] <= other_x_bounds[1]
                    ):
                        cl_info[0] = rect_count + other_rect_count
                        cl_info[1] = pixel_count + other_pixel_count
                        row_clusters[i][1] = (
                            min(x_bounds[0], other_x_bounds[0]),
                            max(x_bounds[1], other_x_bounds[1])
                        )
                        row_clusters[i][2] = other_row
                        clusters[other_row][j] = row_clusters[i]
    largest, largest_i, ratio = [0], -1, 0
    for i in range(len(clusters)):
        for j in range(len(clusters[i])):
            other_ratio = clusters[i][j][0][1] / clusters[i][j][0][0]
            if other_ratio > ratio:
                largest = clusters[i][j]
                largest_i = i
                ratio = other_ratio
    if largest_i < 0:
        return None
    lower_y = largest_i * row_height
    upper_y = ((largest[2] + 1) * row_height) \
        if not last_row_height or largest[2] is len(clusters) - 1 \
        else ((largest[2] * row_height) + last_row_height)
    return (largest[1][0], lower_y), (largest[1][1], upper_y)

    # for i in range(len(row_clusters)):
    #     rect_count, bounds = row_clusters[i]
    #     if not rect_count:
    #         continue
    #     for other_row in range(i + 1, len(row_clusters)):
    #         other_rect_count, other_x_bounds = row_clusters[other_row]
    #         if not other_rect_count:
    #             continue
    #         if bounds[1][1] + row_height == other_x_bounds[0][1] and (
    #             other_x_bounds[0][0] < bounds[0][0] < other_x_bounds[1][0]
    #             or other_x_bounds[0][0] < bounds[1][0] < other_x_bounds[1][0]
    #         ):
    #             row_clusters[i][0] = rect_count + other_rect_count
    #             row_clusters[i][1] = (
    #                 (min(bounds[0][0], other_x_bounds[0][0]), bounds[0][1]),
    #                 (max(bounds[1][0], other_x_bounds[1][0]), other_x_bounds[1][1])
    #             )
    #             row_clusters[other_row] = row_clusters[i]
    #             break
    # return max(row_clusters, key=lambda cluster: cluster[0])[1]


def recognize(image, rect_size, step_percent=0.5):
    size = image.size
    pixels = image.load()

    row_limit = size[1] // rect_size
    col_limit = size[0] // rect_size

    step_count = rect_size ** 2 * step_percent
    row_end_len = size[0] - col_limit * rect_size
    row_end_step_count = rect_size * row_end_len * step_percent
    last_row_height = size[1] - row_limit * rect_size

    row_clusters = [None] * (row_limit if not last_row_height else row_limit + 1)
    # lower_left = (0, 0)
    # upper_right = size
    for row in range(row_limit):
        row_clusters[row] = []
        left_x, right_x = 0, 0
        rect_count = 0
        total_count = 0
        # lower_left = 0, row * rect_size
        for col in range(col_limit):
            count = 0
            for y in range(row * rect_size, (row + 1) * rect_size):
                for x in range(col * rect_size, (col + 1) * rect_size):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if right_x and count < step_count:
                if total_count > 1:
                    row_clusters[row].append([[rect_count, total_count], (left_x, right_x)])
                left_x = col * rect_size
                right_x = left_x + rect_size
                # lower_left = col * rect_size, row * rect_size
                # upper_right = lower_left[0] + rect_size, lower_left[1] * rect_size
                total_count = count
                rect_count = 1
            else:
                right_x = (col + 1) * rect_size
                # upper_right = (col + 1) * rect_size, (row + 1) * rect_size
                total_count += count
                rect_count += 1
        # process the end of the rows if width is not a multiple of the rect size (code duplication is intentional)
        if row_end_len:
            count = 0
            for y in range(row * rect_size, (row + 1) * rect_size):
                for x in range(col_limit * rect_size, size[0]):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if count < row_end_step_count:
                if total_count > 1:
                    row_clusters[row].append([[rect_count, total_count], (left_x, right_x)])
                left_x = col_limit * rect_size
                right_x = size[0]
                # row_clusters[row].append([rect_count, (lower_left, upper_right)])
                # lower_left = col_limit * rect_size, row * rect_size
                # upper_right = size[0], lower_left[1] + rect_size
                total_count = count
                rect_count = 1
            else:
                right_x = size[0]
                # upper_right = size[0], (row + 1) * rect_size
                total_count += count
                rect_count += 1
        row_clusters[row].append([[rect_count, total_count], (left_x, right_x)])
    # process the last row if height is not a multiple of the rect size (code duplication is intentional)
    if last_row_height:
        last_row_step_count = last_row_height * rect_size * step_percent
        row_clusters[row_limit] = []
        left_x, right_x = 0, 0
        rect_count = 0
        total_count = 0
        for col in range(col_limit):
            count = 0
            for y in range(row_limit * rect_size, size[1]):
                for x in range(col * rect_size, (col + 1) * rect_size):
                    if pixels[(x, y)] == MARKED:
                        count += 1
            if right_x and count < last_row_step_count:
                # if rect_count > 1:
                # row_clusters[row_limit].append([rect_count, (lower_left, upper_right)])
                if total_count > 1:
                    row_clusters[row_limit].append([[rect_count, total_count], (left_x, right_x)])
                left_x = col * rect_size
                right_x = left_x + rect_size
                # lower_left = col * rect_size, row_limit * rect_size
                # upper_right = lower_left[0] + rect_size, size[1]
                total_count = count
                rect_count = 1
            else:
                # upper_right = (col + 1) * rect_size, size[1]
                right_x = (col + 1) * rect_size
                total_count += count
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
                if total_count > 1:
                    row_clusters[row_limit].append([[rect_count, total_count], (left_x, right_x)])
                left_x = col_limit * rect_size
                right_x = left_x + rect_size
                # row_clusters[row_limit].append([rect_count, (lower_left, upper_right)])
                # lower_left = col_limit * rect_size, row_limit * rect_size
                # upper_right = size
                total_count = count
                rect_count = 1
            else:
                right_x = size[0]
                # upper_right = size
                total_count += count
                rect_count += 1
            # if rect_count > 1:
            row_clusters[row_limit].append([[rect_count, total_count], (left_x, right_x)])
            # row_clusters[row_limit].append([rect_count, (lower_left, upper_right)])

    if not row_clusters:
        return None
    return _get_largest_cluster_bounds(row_clusters, rect_size, last_row_height)
