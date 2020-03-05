# Read a .osu file
from pprint import pprint
from point import Point
from slider import *

# Plot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

dat = [[0 for j in range(16)] for i in range(12)]

def isValidCoord(upper, value):
    return value < upper and value >= 0

def addData(line):
    obj_type = int(line.split(',')[3])

    # Abort if spinner
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
    block_x = int(x / 32.06)
    block_y = int(y / 32.08)

    # add the object into the block
    if isValidCoord(16, block_x) and isValidCoord(12, block_y):
        dat[block_y][block_x] += 1

def addSlider(line):
    slider_type_dict = {'B': BezierSlider(),
                        'L': LinearSlider()}

    slider_type = (line.split(',')[5]).split('|')[0]
    # Not support perfect-circle and catmul slider for now
    if slider_type in ['P', 'C']:
        addCircle(line)
        return
    
    slider_obj = slider_type_dict[slider_type]
    slider_obj.parseSliderString(line)

    head = slider_obj.pos
    tail = slider_obj.getEndPoint()

    for pt in [head, tail]:
        x, y = pt.x, pt.y

        block_x = int(x / 32.06)
        block_y = int(y / 32.08)

        if isValidCoord(16, block_x) and isValidCoord(12, block_y):
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
