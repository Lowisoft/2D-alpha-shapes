import pygame, sys
from pygame.locals import *
from scipy.spatial import Delaunay
from functools import cmp_to_key
import numpy as np
from copy import deepcopy
from math import sqrt

'''
---------- 2D Alpha Shapes Visualizer  ----------
version 1.0
made by Loris Wilwert (2021)
for Selected Topics in Computational Geometry (S_ATDAG)

--- REQUIRED LIBRARIES ---
pygame, scipy, functools, numpy, copy, math


--- DESCRIPTION ---
This program visually shows 2D alpha shapes for different alpha values.
Since the alpha shape for positive resp. negative alpha is a subgraph of the furthest resp. closest Delaunay 
triangulation, we first compute the triangulation by using the "scipy" library.
Then we loop through the different edges of the triangles, construct for each edge the two discs with radius 1/|alpha| 
and with the endpoints of the edge on its boundary. 
Next we check for both discs, if every  point (for alpha > 0) or if no point (for alpha < 0) lies inside the discs.
If we find such a disc (one is sufficient), then the disc is a generalized disk, the endpoints of the edge are alpha 
neighbors and the edge is part of the alpha shape.
For alpha = 0, we use the Graham scan algorithm to determine the convex hull, which is equal to the 0-shape.
The program uses "pygame" for an underling visualizer, although a switch to another GUI would not require too much effort.

--- COMPLEXITY ---
Let n be the number of drawn points.
The computation of the Delaunay triangulation by the "scipy" library needs O(n * log(n)) time, which is optimal.
However, we need O(n^2) time for the construction of the alpha shapes, because the Delaunay triangulation contains O(n) 
simplices/triangles and for every edge of a simplex (= constant amount) we need O(n) time to check if the edge is part 
of the alpha shapes (by looping through the n points).
So for alpha > 0 and for alpha < 0 we end up with a time complexity of O(n^2) which is a bit slower than the optimal
complexity of O(n * log(n)). For alpha = 0, we use the Graham scan, which has a time complexity of O(n * log(n)).
In terms of space complexity, the program has the optimal complexity of O(n). 

--- RESTRICTIONS ---
The program only visualizes the edges of the alpha shapes, but it neither computes the interior/exterior faces nor 
the set of alpha extreme points. 

--- USAGE ---
Left mouse click:                   Set a point on the canvas
Right mouse click (on a point):     Delete a point from the canvas
Key C:                              Clear all points from the canvas
Key T:                              Toggle the Delaunay triangulation (only for alpha > 0 and for alpha < 0)
Key D:                              Toggle the generalized disks used for the calculation of the alpha shape (only for alpha > 0 and for alpha < 0)
Key 0:                              Set alpha to 0
Key 1:                              Set alpha to a predefined negative value
Key 2:                              Set alpha to a predefined positive value
Left Arrow:                         Decrease the alpha value by a predefined step
Right Arrow:                        Increase the alpha value by a predefined step

'''

# ---------- INITIALIZATION ---------- #
pygame.init()
SCREEN_WIDTH = 1777
SCREEN_HEIGHT = 1000
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("2D Alpha Shapes")
screen.fill(Color("white"))
clock = pygame.time.Clock()


# ---------- VARIABLES ---------- #
done = False
FPS = 30
POINT_RADIUS = 7
LINE_WIDTH = 3
NEGATIVE_ALPHA_VALUE = -0.02
POSITIVE_ALPHA_VALUE = 0.005
STEP = 0.001
points_list = []
nbr_of_points = 0
show_triangulation = False
show_generalized_disks = False
must_be_updated = True
alpha = 0


# ---------- VERIFY IF MOUSE IS ON A POINT ---------- #
def verify_mouse(coords):
    for point in points_list:
        if sqrt((point[0] - coords[0])**2 + (point[1] - coords[1])**2) <= POINT_RADIUS:
            return point
    return None


# ---------- DRAW TRIANGULATION ON CANVAS ---------- #
def draw_triangulation(triangles):
    for t in triangles:
        for i in range(0, 3):
            pygame.draw.line(screen, Color(255, 210, 211), tuple(t[i]), tuple(t[(i + 1)%3]), LINE_WIDTH)


# ---------- DRAW ALPHA VALUE ON CANVAS ---------- #
def draw_alpha_value():
    font = pygame.font.SysFont("Calibri", 30)
    msg = 'α = ' + str(round(alpha, 5))
    text = font.render(msg, True, Color("black"))
    screen.blit(text, (15, SCREEN_HEIGHT - text.get_height() - 15))


def adjust_y_coord(p):
    return [p[0], SCREEN_HEIGHT - p[1]]


def sort_by_y(p):
    return p[1]


# https://docs.python.org/3/howto/sorting.html
def sort_by_angle(p1, p2):
    angle_diff = p1[0] * p2[1] - p1[1] * p2[0]
    if angle_diff > 0:
        return -1
    elif angle_diff == 0 and abs(p1[0]) > abs(p2[0]):
        return -1
    return 1


# ---------- BUILD CONVEX HULL (WITH GRAHAM SCAN) ---------- #
# complexity: O(n * log(n))
# https://en.wikipedia.org/wiki/Graham_scan
def convex_hull(points):
    # adjust y coordinates (because pygame sets (0, 0) in the top left corner)
    for i in range(0, len(points)):
        points[i] = adjust_y_coord(points[i])

    # sort points by y
    points = sorted(points, key=sort_by_y)
    # get point with lowest y coordinate
    p0 = [points[0][0], points[0][1]]

    # move the center of the coordinate system to p0
    for p in points:
        p[0] -= p0[0]
        p[1] -= p0[1]

    # sort points by angle
    points = points[0:1] + sorted(points[1:], key=cmp_to_key(sort_by_angle))

    # move the center of the coordinate system back to (0,0)
    for p in points:
        p[0] += p0[0]
        p[1] += p0[1]

    hull = [p0, points[1]]

    # execute graham scan
    i = 2
    while i <= len(points):
        A, B = hull[len(hull) - 2], hull[len(hull) - 1]
        # calculate if points[i] lies on the left or on the right side of the vector A->B
        pos = (B[0] - A[0]) * (points[i % len(points)][1] - A[1]) - (points[i % len(points)][0] - A[0]) * (B[1] - A[1])
        if pos < 0:
            # points[i] lies on the right side => last point of the hull must be removed
            hull.pop()
        else:
            if pos > 0:
                # points[i] lies on the left side => add points[i] to the hull
                hull.append(points[i % len(points)])
            # otherwise points[i] lies on the vector A->B and can be neglected
            i += 1

    # draw edges of hull (by re-adjusting the y coordinate)
    for i in range(0, len(hull) - 1):
        pygame.draw.line(screen, Color(0, 162, 255), adjust_y_coord(hull[i]), adjust_y_coord(hull[i+1]), LINE_WIDTH)


# ---------- BUILD ALPHA SHAPE ---------- #
# complexity: O(n^2)
# https://math.stackexchange.com/questions/1781438/finding-the-center-of-a-circle-given-two-points-and-a-radius-algebraically
def alpha_shape(triangles):
    points_with_center = []
    considered_edges = []
    radius = abs(1 / alpha)
    # loop through triangles
    for t in triangles:
        # loop through edges of the triangle t
        for i in range(0, 3):
            # endpoints of the edge
            p1, p2 = t[i].tolist(), t[(i + 1) % 3].tolist()
            # check if we do not have already considered this edge
            if [p1, p2] not in considered_edges and [p2, p1] not in considered_edges:
                # add the edge to considered_edges
                considered_edges.append([p1, p2])
                # calculate the half distance between p1 and p2
                xa, ya = (p2[0] - p1[0])/2, (p2[1] - p1[1])/2
                half_dist_btw_points = sqrt(xa**2 + ya**2)
                # check if we can construct a disc with both points on its boundary
                # if not, then both points are not alpha neighbors
                if half_dist_btw_points <= radius:
                    # calculate the mid point of p1 and p2
                    mid = [p1[0] + xa, p1[1] + ya]
                    # calculate the centers of the two discs with both points on their boundary
                    half_dist_btw_centers = sqrt(radius**2 - half_dist_btw_points**2)
                    c1 = [mid[0] + half_dist_btw_centers * ya / half_dist_btw_points,
                          mid[1] - half_dist_btw_centers * xa / half_dist_btw_points]
                    c2 = [mid[0] - half_dist_btw_centers * ya / half_dist_btw_points,
                          mid[1] + half_dist_btw_centers * xa / half_dist_btw_points]
                    # check if we have not already calculated the disc c1 before
                    if (p1, p2, c1) not in points_with_center and (p2, p1, c1) not in points_with_center:
                        # add the endpoints with the center of the disc c1 to our list
                        points_with_center.append((p1, p2, c1))
                    # check if we have not already calculated the disc c2 before
                    if (p1, p2, c2) not in points_with_center and (p2, p1, c2) not in points_with_center:
                        # add the endpoints with the center of the disc c2 to our list
                        points_with_center.append((p1, p2, c2))

    # loop through the discs and associated endpoints of edge
    for p_with_c in points_with_center:
        # center of disc
        c = p_with_c[2]
        is_valid = True
        if alpha > 0:
            # for positive alpha, check if the disc does not contain a point, because then
            # the disc is not a generalized disk
            for x in points_list:
                distance = sqrt((x[0] - c[0]) ** 2 + (x[1] - c[1]) ** 2)
                if distance > radius + POINT_RADIUS/4:
                    is_valid = False
        else:
            # for negative alpha, check if the disc contains a point, because then
            # the disc is not a generalized disk
            for x in points_list:
                distance = sqrt((x[0] - c[0]) ** 2 + (x[1] - c[1]) ** 2)
                if distance < radius - POINT_RADIUS/4:
                    is_valid = False
        if is_valid:
            # the disc is a generalized disk
            neighbor_1 = p_with_c[0]
            neighbor_2 = p_with_c[1]
            if show_generalized_disks:
                pygame.draw.circle(screen, Color(210, 183, 255), tuple(c), radius, LINE_WIDTH)
            pygame.draw.line(screen, Color(0, 162, 255), tuple(neighbor_1), tuple(neighbor_2), LINE_WIDTH)


while not done:
    # ---------- DRAW ON CANVAS ---------- #
    if nbr_of_points != len(points_list) or must_be_updated:
        nbr_of_points = len(points_list)
        must_be_updated = False
        screen.fill(Color("white"))
        # draw the value of alpha on the canvas
        draw_alpha_value()
        if (alpha > 0 and len(points_list) >= 4) or (alpha <= 0 and len(points_list) >= 3):
            if alpha == 0:
                # ---------- CREATE CONVEX HULL ---------- #
                convex_hull(deepcopy(points_list))
            else:
                # ---------- CREATE ALPHA SHAPE ---------- #
                numpy_points_list = np.asarray(points_list)
                is_furthest_side = alpha > 0
                # create triangulation
                triangulation = Delaunay(numpy_points_list, is_furthest_side)
                triangles = numpy_points_list[triangulation.simplices]
                if show_triangulation:
                    # draw triangulation on canvas
                    draw_triangulation(triangles)
                # verify edges
                alpha_shape(triangles)

        # ---------- DRAW ALL POINTS ---------- #
        for point in points_list:
            pygame.draw.circle(screen, Color(44, 53, 95), (point[0], point[1]), POINT_RADIUS)

    # ---------- EVENT HANDLER ---------- #
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True
        if event.type == KEYDOWN:
            # ---------- CLEAR ALL POINTS ---------- #
            if event.key == K_c:
                points_list = []
            # ---------- TOGGLE TRIANGULATION ---------- #
            elif event.key == K_t:
                show_triangulation = not show_triangulation
                must_be_updated = True
            # ---------- TOGGLE GENERALIZED DISKS ---------- #
            elif event.key == K_d:
                show_generalized_disks = not show_generalized_disks
                must_be_updated = True
            # ---------- SET ALPHA TO 0 ---------- #
            elif (event.key == K_0 or event.key == K_KP0) and alpha != 0:
                alpha = 0
                must_be_updated = True
            # ---------- SET ALPHA TO NEGATIVE ALPHA VALUE ---------- #
            elif (event.key == K_1 or event.key == K_KP1) and alpha != NEGATIVE_ALPHA_VALUE:
                alpha = NEGATIVE_ALPHA_VALUE
                must_be_updated = True
            # ---------- SET ALPHA TO A POSITIVE ALPHA VALUE ---------- #
            elif (event.key == K_2 or event.key == K_KP2) and alpha != POSITIVE_ALPHA_VALUE:
                alpha = POSITIVE_ALPHA_VALUE
                must_be_updated = True
            # ---------- INCREASE ALPHA ---------- #
            elif event.key == K_RIGHT:
                alpha += STEP
                must_be_updated = True
            # ---------- DECREASE ALPHA ---------- #
            elif event.key == K_LEFT:
                alpha -= STEP
                must_be_updated = True
        if event.type == MOUSEBUTTONDOWN:
            coords = pygame.mouse.get_pos()
            # ---------- ADD POINT ---------- #
            if event.button == 1:
                points_list.append([coords[0], coords[1]])
            # ---------- REMOVE POINT ---------- #
            elif event.button == 3:
                point = verify_mouse(coords)
                if point is not None:
                    points_list.remove(point)

    # ---------- UPDATE CANVAS ---------- #
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
