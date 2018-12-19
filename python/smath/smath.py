import math
import numpy as np


class Math:
    @staticmethod
    def __create_point(orientation, center_x, center_y, angle, direction, is_width):
        if direction:
            x = orientation / 2 * math.cos(math.radians(angle - 90 if is_width else angle)) + center_x
            y = orientation / 2 * math.sin(math.radians(angle - 90 if is_width else angle)) + center_y
        else:
            x = center_x - orientation / 2 * math.cos(math.radians(angle - 90 if is_width else angle))
            y = center_y - orientation / 2 * math.sin(math.radians(angle - 90 if is_width else angle))

        return x, y

    @staticmethod
    def create_rectangle(center_x, center_y, width, height, angle):
        x1, y1 = Math.__create_point(width, center_x, center_y, angle, True, True)
        x2, y2 = Math.__create_point(width, center_x, center_y, angle, False, True)
        x3, y3 = Math.__create_point(height, center_x, center_y, angle, True, False)
        x4, y4 = Math.__create_point(height, center_x, center_y, angle, False, False)

        tlc = (x2 - center_x + x4, y2 - center_y + y4)
        trc = (x1 - center_x + x4, y1 - center_y + y4)
        brc = (x1 - center_x + x3, y1 - center_y + y3)
        blc = (x2 - center_x + x3, y2 - center_y + y3)

        return tlc, blc, brc, trc

    @staticmethod
    def aabb_in_aabb(aabb1, aabb2):
        return aabb1[0][0] < aabb2[0][0] + aabb2[3][0] - aabb2[0][0] and \
               aabb1[0][0] + aabb1[3][0] - aabb1[0][0] > aabb2[0][0] and \
               aabb1[0][1] < aabb2[0][1] + aabb2[1][1] - aabb2[0][1] and \
               aabb1[0][1] + aabb1[1][1] - aabb1[0][1] > aabb2[0][1]

    @staticmethod
    def center_of_polygon(polygon):
        if len(polygon) > 0:
            x_values = [vertex[0] for vertex in polygon]
            y_values = [vertex[1] for vertex in polygon]

            return sum(x_values) / len(polygon), sum(y_values) / len(polygon)

        return -1, -1

    @staticmethod
    def stretch_polygon_by_percent(a, b, percent):
        x = (b[0] - a[0]) * percent + b[0]
        y = (b[1] - a[1]) * percent + b[1]

        return x, y

    @staticmethod
    def get_perpendicular_vector(v):
        return -v[1], v[0]

    @staticmethod
    def vector_norm(v):
        return math.sqrt(Math.dot(v, v))

    @staticmethod
    def normalize_vector(v):
        n = float(Math.vector_norm(v))

        if n != 0:
            return [float(v[i]) / n for i in range(len(v))]
        else:
            return [-1 for i in range(len(v))]

    @staticmethod
    def cross(u, v):
        return u[0] * v[1] - v[0] * u[1]

    @staticmethod
    def intersection(p, q, r, s):
        x = (r[0] - p[0], r[1] - p[1])
        d1 = (q[0] - p[0], q[1] - p[1])
        d2 = (s[0] - r[0], s[1] - r[1])

        cross1 = Math.cross(x, d2)
        cross2 = Math.cross(d1, d2)

        if cross2 == 0:
            return False, None
        else:
            t1 = cross1 / cross2

            if t1 == 0:
                return False, None

            return True, (p[0] + d1[0] * t1, p[1] + d1[1] * t1)

    @staticmethod
    def shapify(line):
        shape, shape_part_one, shape_part_two = [], [], []

        p = line[0]

        for i in range(1, len(line), 2):
            q = line[i]

            pq = Math.get_perpendicular_vector((q[0] - p[0], q[1] - p[1]))
            pq = Math.normalize_vector(pq)

            shape_part_one.append((p[0] - pq[0] * 35, p[1] - pq[1] * 35))
            shape_part_two.append((p[0] + pq[0] * 35, p[1] + pq[1] * 35))

            p = q

        for s in shape_part_one:
            shape.append(s)

        for s in reversed(shape_part_two):
            shape.append(s)

        if len(shape_part_one) > 0:
            shape.append(shape_part_one[0])

        if len(shape_part_two) > 0:
            shape.append(shape_part_two[0])

        shape_part_one.append(shape_part_one[0])
        shape_part_two.append(shape_part_two[0])

        return shape, shape_part_one, shape_part_two

    @staticmethod
    def resample_points(points, num_desired_points=64):
        I = Math.path_length(points) / (num_desired_points - 1)
        D = 0.0

        new_points = [points[0]]

        i = 1

        while i < len(points):
            d = Math.vector_norm((points[i - 1][0] - points[i][0], points[i - 1][1] - points[i][1]))

            if (D + d) >= I:
                qx = points[i - 1][0] + ((I - D) / d) * (points[i][0] - points[i - 1][0])
                qy = points[i - 1][1] + ((I - D) / d) * (points[i][1] - points[i - 1][1])
                new_points.append((qx, qy))
                points.insert(i, (qx, qy))

                D = 0.0
            else:
                D += d

            i += 1

        if len(new_points) == num_desired_points - 1:
            new_points.append(points[-1])

        return new_points

    @staticmethod
    def path_length(points):
        d = 0.0

        for i in range(1, len(points)):
            d += Math.vector_norm((points[i - 1][0] - points[i][0], points[i - 1][1] - points[i][1]))

        return d

    @staticmethod
    def rotate_palette(p, q, angle):
        ox, oy = p[0], p[1]
        px, py = q[0], q[1]

        math.radians(angle)

        qx = ox + math.cos(math.radians(angle)) * (px - ox) - math.sin(
            math.radians(angle)) * (py - oy)
        qy = oy + math.sin(math.radians(angle)) * (px - ox) + math.cos(
            math.radians(angle)) * (py - oy)

        return qx, qy

    @staticmethod
    def rotate(p, q, angle):
        ox, oy = p[0], p[1]
        px, py = q[0], q[1]

        math.radians(angle + 90)  # ?

        qx = ox + math.cos(math.radians(angle)) * (px - ox) - math.sin(math.radians(angle)) * (py - oy)
        qy = oy + math.sin(math.radians(angle)) * (px - ox) + math.cos(math.radians(angle)) * (py - oy)

        return qx, qy

    @staticmethod
    def sufficient_shape_area(shape, threshold=15000):
        area = 0.0

        for i in range(len(shape)):
            j = (i + 1) % len(shape)
            area += shape[i][0] * shape[j][1]
            area -= shape[j][0] * shape[i][1]

        area = abs(area) / 2.0

        return threshold < area

    @staticmethod
    def polygon_aabb(polygon):
        if len(polygon) > 0:
            minx, miny = float("inf"), float("inf")
            maxx, maxy = float("-inf"), float("-inf")

            for x, y in polygon:
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                elif y > maxy:
                    maxy = y

            return [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)]

        return None

    @staticmethod
    def get_arrow_tip_part(p, q, angle, part_stretch_factor):
        pr = Math.rotate(q, p, angle)
        qr = (p[0] - pr[0],  p[1] - pr[1])

        Math.normalize_vector(qr)

        qr = (qr[0] * -part_stretch_factor + p[0], qr[1] * -part_stretch_factor + p[1])

        return [qr, q]

    @staticmethod
    def get_arrow_tip(p, q, angle, part_stretch_factor):
        return Math.get_arrow_tip_part(p, q, angle, part_stretch_factor), Math.get_arrow_tip_part(p, q, 360 - angle, part_stretch_factor)

    @staticmethod
    def to_movement_arrow(p, is_change_in_x, is_change_positive):
        A = 10
        B = 20
        C = 55

        p11 = (p[0] + (0 if is_change_in_x else -A), p[1] + (-A if is_change_in_x else 0))
        p21 = (p[0] + (0 if is_change_in_x else A), p[1] + (A if is_change_in_x else 0))
        p12 = (p11[0] + ((B if is_change_positive else -B) if is_change_in_x else 0), p11[1] + ((B if is_change_positive else -B) if not is_change_in_x else 0))
        p22 = (p21[0] + ((B if is_change_positive else -B) if is_change_in_x else 0), p21[1] + ((B if is_change_positive else -B) if not is_change_in_x else 0))
        p3 = (p[0] + ((C if is_change_positive else -C) if is_change_in_x else 0), p[1] + ((C if is_change_positive else -C) if not is_change_in_x else 0))

        arrow_tip1, arrow_tip2 = Math.get_arrow_tip(p, p3, 30, 0.75)

        return {'upper': [p11, p12], 'lower': [p21, p22], 'angle_one': arrow_tip1, 'angle_two': arrow_tip2}

    @staticmethod
    def movement_indication(aabb):
        p, q, r, s = aabb

        return [
            Math.to_movement_arrow((p[0] - 10, p[1] + ((q[1] - p[1]) / 2)), True, False),
            Math.to_movement_arrow((q[0] + ((r[0] - q[0]) / 2), q[1] + 10), False, True),
            Math.to_movement_arrow((r[0] + 10, s[1] + ((r[1] - s[1]) / 2)), True, True),
            Math.to_movement_arrow((p[0] + ((s[0] - p[0]) / 2), p[1] - 10), False, False)
        ]

    @staticmethod
    def dot(u, v):
        return sum((a * b) for a, b in zip(u, v))

    @staticmethod
    def angle_degrees(u, v):
        u_u = Math.normalize_vector(u)
        v_u = Math.normalize_vector(v)

        return np.arccos(np.clip(np.dot(u_u, v_u), -1.0, 1.0))

    @staticmethod
    def compute_circle(x, y, r):
        temp1 = []
        temp2 = []

        for x_ in range(-r, r):
            y_ = int(math.sqrt(int(r * r) - x_ * x_) + 0.5)

            temp1.append((x + x_, y + y_))
            temp2.append((x + x_, y - y_))

        return temp1 + list(reversed(temp2))

    @staticmethod
    def curve_median_point(curve):
        if len(curve) % 2 == 1:
            return curve[len(curve) // 2]
        else:
            a = (curve[len(curve) // 2 - 1][0], curve[len(curve) // 2 - 1][1])
            b = (curve[len(curve) // 2 + 1][0], curve[len(curve) // 2 + 1][1])

            return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)

    @staticmethod
    def palette_circle_extension(curve, parent):
        circle_center = parent.center
        m = Math.curve_median_point(curve)
        v = (m[0] - circle_center[0], m[1] - circle_center[1])

        d = Math.vector_norm(v) * 1.5
        vn = Math.normalize_vector(v)

        p = (vn[0] * d + circle_center[0], vn[1] * d + circle_center[1])

        temp = []

        for r in parent.roi:
            if r == m:
                temp.append(p)
            else:
                v = (r[0] - circle_center[0], r[1] - circle_center[1])

                d = Math.vector_norm(v) * 1.5
                vn = Math.normalize_vector(v)
                q = (vn[0] * d + circle_center[0], vn[1] * d + circle_center[1])

                temp.append(q)

        return m, temp
