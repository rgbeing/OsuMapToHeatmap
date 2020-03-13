# Read a .osu file
from pprint import pprint
from point import Point
from slider import *

# Plot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

CELL_COL_NUM = 15
CELL_ROW_NUM = 11
CELL_WIDTH = 513 / CELL_COL_NUM
CELL_HEIGHT = 385 / CELL_ROW_NUM

dat = [[0 for j in range(CELL_COL_NUM)] for i in range(CELL_ROW_NUM)]

def isValidCoord(upper, value):
    return value < upper and value >= 0

def addData(line):
    obj_type = int(line.split(',')[3])

    # Abort spinner
    if obj_type & 8 > 0:
        return
    elif obj_type & 2 > 0:
        addSlider(line)
    elif obj_type & 1 > 0:
        addCircle(line)

def addCircle(line):
    line = line.split(',')

    # x, y coordinate
    x, y = int(line[0]), int(line[1])

    # compute a block the circle is contained in
    block_x = int(x / CELL_WIDTH)
    block_y = int(y / CELL_HEIGHT)

    # add the object into the block
    if isValidCoord(CELL_COL_NUM, block_x) and isValidCoord(CELL_ROW_NUM, block_y):
        dat[block_y][block_x] += 1

def addSlider(line):
    slider_type_dict = {'B': BezierSlider(),
                        'L': LinearSlider(),
                        'C': CatmullSlider()}

    slider_type = (line.split(',')[5]).split('|')[0]
    # Not support perfect-circle and catmul slider for now
    if slider_type in ['P']:
        addCircle(line)
        return
    
    slider_obj = slider_type_dict[slider_type]
    slider_obj.parseSliderString(line)

    head = slider_obj.pos
    tail = slider_obj.getEndPoint()

    for pt in [head, tail]:
        x, y = pt.x, pt.y

        block_x = int(x / CELL_WIDTH)
        block_y = int(y / CELL_HEIGHT)

        if isValidCoord(CELL_COL_NUM, block_x) and isValidCoord(CELL_ROW_NUM, block_y):
            dat[block_y][block_x] += 1


if __name__ == "__main__":
    # Read a osu file
    file_location = input()

    with open(file_location, 'r', encoding='UTF8') as file:
        while True:
            objstr = file.readline().strip()
            if objstr == "[HitObjects]":
                break
        
        while True:
            objstr = file.readline().strip()
            if objstr == "":
                break

            addData(objstr)


    # Plot
    df = pd.DataFrame(dat)
    print(df)

    # annot: a number on box | cmap: color | ticklabels: a number on axes
    ax = sns.heatmap(df, annot=True, fmt='d', cmap='RdYlGn_r', xticklabels=False, yticklabels=False)
    # Put a title of heatmap
    plt.title(file_location, loc='right', fontsize=12)
    plt.show()
