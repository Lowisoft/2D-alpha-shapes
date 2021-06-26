# 2D Alpha Shapes Visualizer
version 1.0
made by Loris Wilwert (2021)
for Selected Topics in Computational Geometry (S_ATDAG)

### REQUIRED LIBRARIES
* pygame
* scipy
* functools
* numpy
* copy
* math


### DESCRIPTION
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

### COMPLEXITY
Let n be the number of drawn points.
The computation of the Delaunay triangulation by the "scipy" library needs O(n * log(n)) time, which is optimal.
However, we need O(n^2) time for the construction of the alpha shapes, because the Delaunay triangulation contains O(n) 
simplices/triangles and for every edge of a simplex (= constant amount) we need O(n) time to check if the edge is part 
of the alpha shapes (by looping through the n points).
So for alpha > 0 and for alpha < 0 we end up with a time complexity of O(n^2) which is a bit slower than the optimal
complexity of O(n * log(n)). For alpha = 0, we use the Graham scan, which has a time complexity of O(n * log(n)).
In terms of space complexity, the program has the optimal complexity of O(n). 

### RESTRICTIONS
The program only visualizes the edges of the alpha shapes, but it neither computes the interior/exterior faces nor 
the set of alpha extreme points. 

### USAGE
Command | Description
------------ | -------------
Left mouse click | Set a point on the canvas
Right mouse click (on a point) | Delete a point from the canvas
Key C | Clear all points from the canvas
Key T | Toggle the Delaunay triangulation (only for alpha > 0 and for alpha < 0)
Key D | Toggle the generalized disks used for the calculation of the alpha shape (only for alpha > 0 and for alpha < 0)
Key 0 |  Set alpha to 0
Key 1 | Set alpha to a predefined negative value
Key 2 |  Set alpha to a predefined positive value
Left Arrow | Decrease the alpha value by a predefined step
Right Arrow | Increase the alpha value by a predefined step
