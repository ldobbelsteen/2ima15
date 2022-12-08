from PIL import Image, ImageDraw
import json


def drawPolygon(polygon, solution={"polygons": []}):
    
    outer_boundary_xy = [(p["x"], p["y"]) for p in polygon["outer_boundary"]]
    holes_xy = [[(p["x"], p["y"]) for p in h] for h in polygon["holes"]]
    solution_xy = [[(p["x"], p["y"]) for p in c] for c in solution["polygons"]]

    # convert fraction representation to decimal numbers
    solution_xy = [[(p[0]["num"]/p[0]["den"], p[1]) if isinstance(p[0], dict)
                    else p for p in c] for c in solution_xy]
    solution_xy = [[(p[0], p[1]["num"]/p[1]["den"]) if isinstance(p[1], dict)
                    else p for p in c] for c in solution_xy]

    min_x = min([p[0] for p in outer_boundary_xy])
    max_x = max([p[0] for p in outer_boundary_xy])
    min_y = min([p[1] for p in outer_boundary_xy])
    max_y = max([p[1] for p in outer_boundary_xy])
    # Translate coordinates such that min x and min y are 0
    outer_boundary_xy = [(p[0] - min_x, p[1] - min_y) for p in outer_boundary_xy]
    holes_xy = [[(p[0] - min_x, p[1] - min_y) for p in h] for h in holes_xy]
    # Set width and height to width and height of polygon
    width = (max_x - min_x) * 5    # * 5 for better resolution
    height = (max_y - min_y) * 5
    size = (width, height)
    # Flip y-axis such that 0,0 is now bottom left in our visualization
    outer_boundary_xy = [(p[0]*5, height - p[1]*5) for p in outer_boundary_xy]
    holes_xy = [[(p[0]*5, height - p[1]*5) for p in h] for h in holes_xy]

    # Draw polygons                                                   
    img = Image.new("RGB", size, "white") 
    img1 = ImageDraw.Draw(img)  
    img1.polygon(outer_boundary_xy, fill="#eeeeff", outline="blue")
    for h_xy in holes_xy:
        img1.polygon(h_xy, fill="white", outline="blue")
    for c_xy in solution_xy:
        img1.polygon(c_xy, fill="#ffeeee", outline="red")
    img.show()

f = open("instances_v2\instances\ccheese142.instance.json")
polygon = json.load(f)
drawPolygon(polygon)
