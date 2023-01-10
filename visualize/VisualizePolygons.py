from PIL import Image, ImageDraw
import json


def drawPolygon(polygon, solution={"polygons": []}, resolution=10, name="polygon_drawing"):
    """
    Visualizes the polygon, the format should be confrom the specification of the challenge:
    https://cgshop.ibr.cs.tu-bs.de/competition/cg-shop-2023/#instance-format
    """
    
    outer_boundary_xy = [(p["x"], p["y"]) for p in polygon["outer_boundary"]]
    holes_xy = [[(p["x"], p["y"]) for p in h] for h in polygon["holes"]]
    solution_xy = [[(p["x"], p["y"]) for p in c] for c in solution["polygons"]]

    # convert fraction representation to decimal numbers
    solution_xy = [[(p[0]["num"]/p[0]["den"], p[1]) if isinstance(p[0], dict)
                    else p for p in c] for c in solution_xy]
    solution_xy = [[(p[0], p[1]["num"]/p[1]["den"]) if isinstance(p[1], dict)
                    else p for p in c] for c in solution_xy]

    # Translate coordinates such that min x and min y are 0
    min_x = min([p[0] for p in outer_boundary_xy])
    max_x = max([p[0] for p in outer_boundary_xy])
    min_y = min([p[1] for p in outer_boundary_xy])
    max_y = max([p[1] for p in outer_boundary_xy])
    outer_boundary_xy = [(p[0] - min_x, p[1] - min_y) for p in outer_boundary_xy]
    holes_xy = [[(p[0] - min_x, p[1] - min_y) for p in h] for h in holes_xy]
    solution_xy = [[(p[0] - min_x, p[1] - min_y) for p in h] for h in solution_xy]

    # Set width and height to width and height of polygon
    width = (max_x - min_x) * resolution
    height = (max_y - min_y) * resolution
    size = (width, height)
    # Flip y-axis such that 0,0 is now bottom left in our visualization
    outer_boundary_xy = [(p[0]*resolution, height - p[1]*resolution) for p in outer_boundary_xy]
    holes_xy = [[(p[0]*resolution, height - p[1]*resolution) for p in h] for h in holes_xy]
    solution_xy = [[(p[0]*resolution, height - p[1]*resolution) for p in h] for h in solution_xy]

    # Draw polygons                                                   
    img = Image.new("RGB", size, "white") 
    img1 = ImageDraw.Draw(img)  
    img1.polygon(outer_boundary_xy, fill="#eeeeff", outline="blue")
    for h_xy in holes_xy:
        img1.polygon(h_xy, fill="white", outline="blue")
    for c_xy in solution_xy:
        img1.polygon(c_xy, fill="#ffeeee", outline="red")
    img.save(name + ".png")


# For testing purposes:
if __name__ == "__main__":
    f = open("..\instances\ccheese142.instance.json")
    polygon = json.load(f)
    drawPolygon(polygon)
