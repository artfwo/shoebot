from random import randint

size(1000,1000)

colormode(HSB)
colorrange(255)

rows = 9
cols = 9

def block(x,y,z): 
    '''
    draw an isometric square prism; x,y are the coordinates of 
    the BOTTOM-CENTER corner, z is the height
    '''
    #TODO : variables for width+depth instead of fixed value
    
    # no strokes in the inside
    nostroke()
    
    # every building will have a random hue

    hue = randint(0,255)
    
    # LEFT FACE
    # first, set the color
    c = color(hue,40,120)
    fill(c)
    # and draw the path
    beginpath(x,y)
    lineto(x-20,y-10)
    lineto(x-20,y-10-z)
    lineto(x,y-z)
    endpath()

    # RIGHT FACE
    c = color(hue,40,80)
    fill(c)
    beginpath(x,y)
    lineto(x+20,y-10)
    lineto(x+20,y-10-z)
    lineto(x,y-z)
    endpath()

    # TOP FACE
    c = color(hue,40,40)
    fill(c)
    beginpath(x,y-z)
    lineto(x+20,y-10-z)
    lineto(x,y-20-z)
    lineto(x-20,y-10-z)
    endpath()

    # CONTOUR
    # now, we'll make a stroke around the faces
    # set the color
    c = color(hue,40,80)
    # set the stroke
    stroke(c)
    # and unset fill
    nofill()
    # draw the path
    beginpath(x,y)
    lineto(x-20,y-10)
    lineto(x-20,y-10-z)
    lineto(x,y-20-z)
    lineto(x+20,y-10-z)
    lineto(x+20,y-10)
    endpath()

def setup():
    # white background
    background(1,1,1)
    
    # start from 100,100
    translate(100,100)
    # and draw the blocks
    for x,y in grid(rows,cols,100,100):
        # height of each block is determined by x,y coordinates
        z = (x+y)/25
        # draw it
        block(x,y,z)

setup()
