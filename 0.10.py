import pygame, Access, shapely.geometry, sys, numpy, scipy.stats, openpyxl, os
from datetime import datetime
from PIL import Image, ImageDraw

'''
Current key bindings:
left-click: creates a box (finished on lift)
shift left-click: selects a point (on lift)
left arrow: move left
right arrow: move right
up arrow: move up
down arrow: move down
t: list number of images on screen
h: toggles images visability
g: find pairs from images
f: toggles pairs visability
y: toggle background visability
u: toggle movement data
r: breakdown of overlap data
'''

pygame.init()
largest = [840,420]
screen = pygame.display.set_mode((1040,420))
sidescreen = pygame.Surface((200,420))
pygame.display.set_caption('CTX Explorer')
Image.MAX_IMAGE_PIXELS = 500000000

colors = {
    'white':pygame.color.Color('#FFFFFF'),
    'black':pygame.color.Color('#000000'),
    'light':pygame.color.Color('#d9d9d9'),
    'midde':pygame.color.Color('#b3b3b3'),
    'darke':pygame.color.Color('#8c8c8c'),
    'green':pygame.color.Color('#00FF0020'),
    'bdark':pygame.color.Color('#00000020'),
    'wback':pygame.color.Color('#FFFFFF40'),
    'gdark':pygame.color.Color('#008000'),
    'redde':pygame.color.Color('#400000'),
    'blank':pygame.color.Color('#00000000'),
    'masks':pygame.color.Color('#FF00FF')
}
my_cursor_drawings = {
    'pointhand':(
        "     XX                 ",
        "    X..X                ",
        "    X..X                ",
        "    X..X                ",
        "    X..X                ",
        "    X..XXX              ",
        "    X..X..XXX           ",
        "    X..X..X..XX         ",
        "    X..X..X..X.X        ",
        "XXX X..X..X..X..X       ",
        "X..XX........X..X       ",
        "X...X...........X       ",
        " X..............X       ",
        "  X.............X       ",
        "  X.............X       ",
        "   X............X       ",
        "   X...........X        ",
        "    X..........X        ",
        "    X..........X        ",
        "     X........X         ",
        "     X........X         ",
        "     XXXXXXXXXX         ",
        "                        ",
        "                        "
    ),
    'arrow':(
        "X               ",
        "XX              ",
        "X.X             ",
        "X..X            ",
        "X...X           ",
        "X....X          ",
        "X.....X         ",
        "X......X        ",
        "X.......X       ",
        "X........X      ",
        "X.........X     ",
        "X..........X    ",
        "X......XXXXX    ",
        "X...X..X        ",
        "X..X X..X       ",
        "X.X  X..X       ",
        "XX    X..X      ",
        "      X..X      ",
        "       XX       ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                "
    ),
    'hand':(
        "        XX              ",
        "     XXX..X             ",
        "    X..X..XXX           ",
        "    X..X..X..X          ",
        "    X..X..X..XXX        ",
        "    X..X..X..X..X       ",
        "    X..X..X..X..X       ",
        "    X..X..X..X..X       ",
        "    X..X..X..X..X       ",
        "XXX X..X..X..X..X       ",
        "X..XX........X..X       ",
        "X...X...........X       ",
        " X..............X       ",
        "  X.............X       ",
        "  X.............X       ",
        "   X............X       ",
        "   X...........X        ",
        "    X..........X        ",
        "    X..........X        ",
        "     X........X         ",
        "     X........X         ",
        "     XXXXXXXXXX         ",
        "                        ",
        "                        "
    ),
    'handgrab':(
        "                        ",
        "                        ",
        "                        ",
        "                        ",
        "                        ",
        "                        ",
        "                        ",
        "     XX XX              ",
        "    X..X..XXX           ",
        "    X..X..X..XXX        ",
        "  XXX..X..X..X..X       ",
        " X..X........X..X       ",
        " X..............X       ",
        " X..............X       ",
        "  X.............X       ",
        "  X.............X       ",
        "   X...........X        ",
        "    X..........X        ",
        "    X..........X        ",
        "     X........X         ",
        "     X........X         ",
        "     XXXXXXXXXX         ",
        "                        ",
        "                        "
    )
}
my_cursors = {
    ## Cursor size, hotspot, xor masks, and masks
    'pointhand':[(24,24),(5,1)]+list(pygame.cursors.compile(my_cursor_drawings['pointhand'],black='X',white='.',xor='or')),
    'arrow':[(16,24),(0,0)]+list(pygame.cursors.compile(my_cursor_drawings['arrow'],black='X',white='.',xor='or')),
    'hand':[(24,24),(5,1)]+list(pygame.cursors.compile(my_cursor_drawings['hand'],black='X',white='.',xor='or')),
    'handgrab':[(24,24),(5,1)]+list(pygame.cursors.compile(my_cursor_drawings['handgrab'],black='X',white='.',xor='or'))
}

#pygame.mouse.set_cursor(*my_cursors['hand'])
pygame.mouse.set_cursor(*my_cursors['arrow'])
clock = pygame.time.Clock()
backdrop = shapely.geometry.Polygon([(0,0),(840,0),(840,420),(0,420)])
see_through = pygame.Surface((1000,1000)).convert_alpha()
pix = [largest[0]/360,largest[1]/180]
inv_pix = [1/pix[0],1/pix[1]]

## ---- Data Boxes Etc. ---- ##

## Holds necessary data for formatting on output
class OutData:
    def __init__(self, data):
        parents = data.getParents()
        quick_sql = '''select
            upper_left_longitude,upper_left_latitude,
            upper_right_longitude,upper_right_latitude,
            lower_left_longitude,lower_left_latitude,
            lower_right_longitude,lower_right_latitude
            from Data where product_id in (?,?)'''
        coordinates = Access.executeCTX(quick_sql,(parents[0],parents[1]))
        primary_co = []
        for pair in data.getRawPoly().exterior.coords[::-1]:
            for co in pair:
                primary_co.append(str(round(co,4)))
        self.contained = {
            'Coordinates': ' '.join(primary_co),
            'Parent1': '\n'+parents[0],
            'Coordinates1': ' '.join([str(co) for co in coordinates[0]]),
            'Location1': 'Unavailable',
            'Parent2': '\n'+parents[1],
            'Coordinates2': ' '.join([str(co) for co in coordinates[1]]),
            'Location2': 'Unavailable\n'
        }
    def get(self):
        return ' '.join(self.contained[value] for value in self.contained)

## ---- ---- ##

## Holds the background image
class Picture:
    def __init__(self):
        self.img = Image.open('mola-LARGEST.jpg')
        self.big_size = self.img.size
        self.center = [largest[0]/2,largest[1]/2]
        got_img = self.img.resize(largest)
        im_mode = got_img.mode
        im_size = got_img.size
        im_data = got_img.tobytes()
        self.image = pygame.image.fromstring(im_data,im_size,im_mode)
    def redraw(self,scale,cent):
        big = [largest[0]*scale,largest[1]*scale]
        new_p = [int(0-cent[0]),int(0-cent[1])]
        wid = (self.big_size[0]/scale)/2
        hig = (self.big_size[1]/scale)/2
        centa = ((self.center[0]-new_p[0])/big[0])*self.big_size[0]
        centb = ((self.center[1]-new_p[1])/big[1])*self.big_size[1]
        got_img = self.img.crop((int(centa-wid),int(centb-hig),int(centa+wid),int(centb+hig)))
        got_img = got_img.resize(largest)
        im_mode = got_img.mode
        im_size = got_img.size
        im_data = got_img.tobytes()
        self.image = pygame.image.fromstring(im_data,im_size,im_mode)
    def update(self):
        screen.blit(self.image,[0,0])

class PolyDrawn:
    def __init__(self,original,adjusted):
        self.original_points = [original]
        self.adjusted_points = [adjusted]
    def addPoint(self,original,adjusted):
        self.original_points.append(original)
        self.adjusted_points.append(adjusted)
    def modify(self,scale,cent):
        for index in range(len(self.original_points)):
            new_point = [
                int((self.original_points[index][0]*scale)-cent[0]),
                int((self.original_points[index][1]*scale)-cent[1])
            ]
            self.adjusted_points[index] = new_point
    def getPoly(self):
        return self.adjusted_points
    def update(self):
        if len(self.adjusted_points) > 1:
            pygame.draw.polygon(screen,colors['black'],self.adjusted_points,1)
        else:
            pygame.draw.circle(screen,colors['black'],self.adjusted_points[0],1)

## ---- UI Classes ---- ##

## Class for block boundaries on the screen
class Block:
    def __init__(self,place,area,primary,secondary):
        self.primary = primary
        self.secondary = secondary
        ## Width, height
        self.area = area
        ## Topleft
        self.place = place
        self.rectangle = pygame.Rect(place,area)
    def update(self,backdrop):
        pygame.draw.rect(backdrop,self.primary,self.rectangle)
        pygame.draw.rect(backdrop,self.secondary,self.rectangle,1)

## Text box class
class Text:
    def __init__(self,text,position,size=10,color='black'):
        self.font = pygame.font.Font('C:\\Windows\\Fonts\\calibril.ttf',size)
        self.text = text
        self.colour = colors[color]
        self.render = self.font.render(text,True,self.colour)
        self.rect = self.render.get_rect()
        self.rect.topleft = position
        self.position = position
    def edit(self,new_text):
        self.text = new_text
        self.render = self.font.render(self.text,True,self.colour)
        self.rect = self.render.get_rect()
        self.rect.topleft = self.position
    def changeColor(self,new_color):
        self.colour = colors[new_color]
        self.render = self.font.render(self.text,True,self.colour)
    def limit(self,maximum):
        while self.rect.width > maximum:
            self.text = self.text[:-1]
            self.render = self.font.render(self.text,True,self.colour)
            self.rect = self.render.get_rect()
            self.rect.topleft = self.position
    def getText(self):
        return self.text
    def update(self,backdrop):
        backdrop.blit(self.render,self.rect)

## Input box
class InputBox(Text):
    def __init__(self,text,position,width,size=15):
        super().__init__(text,position,size,'darke')
        self.start_text = text
        self.this_text = ''
        self.width = width
        self.border_rect = pygame.Rect(self.rect.left-2,self.rect.top-2,self.width+5,self.rect.height+3)
    def accept(self,given):
        if given in ['0','[0]']:
            self.this_text += '0'
        elif given in ['1','[1]']:
            self.this_text += '1'
        elif given in ['2','[2]']:
            self.this_text += '2'
        elif given in ['3','[3]']:
            self.this_text += '3'
        elif given in ['4','[4]']:
            self.this_text += '4'
        elif given in ['5','[5]']:
            self.this_text += '5'
        elif given in ['6','[6]']:
            self.this_text += '6'
        elif given in ['7','[7]']:
            self.this_text += '7'
        elif given in ['8','[8]']:
            self.this_text += '8'
        elif given in ['9','[9]']:
            self.this_text += '9'
        elif given in ['-','[-]']:
            if self.this_text == '':
                self.this_text += '-'
        elif given in ['.','[.]']:
            if self.this_text == '' or self.this_text == '-':
                self.this_text += '0.'
            elif '.' not in self.this_text:
                self.this_text += '.'
        elif given in ['backspace']:
            if self.this_text != '':
                self.this_text = self.this_text[:-1]
    def upText(self,given):
        self.accept(given)
        if self.this_text != '':
            self.edit(self.this_text)
            self.limit(self.width)
            self.this_text = self.text
            self.changeColor('black')
        if self.this_text == '':
            self.edit(self.start_text)
            self.changeColor('darke')
    def update(self,backdrop):
        pygame.draw.rect(backdrop,colors['midde'],self.border_rect)
        pygame.draw.rect(backdrop,colors['darke'],self.border_rect,1)
        backdrop.blit(self.render,self.rect)

## Basic button box
class Button(Text):
    def __init__(self,text,position,function):
        super().__init__(text,position,15)
        self.function = function
        self.border_rect = pygame.Rect(self.rect.left-2,self.rect.top-2,self.rect.width+5,self.rect.height+3)
    def getFunc(self):
        return self.function
    def update(self,backdrop):
        pygame.draw.rect(backdrop,colors['midde'],self.border_rect)
        pygame.draw.rect(backdrop,colors['darke'],self.border_rect,1)
        backdrop.blit(self.render,self.rect)

## Holds all information in the sidebar
class SideBar:
    def __init__(self):
        self.current_typer = None
        self.holding = [
            Block((0,0),(200,420),colors['light'],colors['darke']),
            Text('Zoom: 1.0',(10,390)),
            Text('FPS: ',(10,405)),
            Text('Coordinates: ',(10,375)),
            Text('Parent 1: ',(10,10)),
            Text('Parent 2: ',(10,25)),
            Button('Clear list',(10,40),clearList),
            Button('Get list',(10,60),getList),
            Button('Get from selection',(10,80),selectList),
            InputBox('North',(10,120),100),
            InputBox('West',(10,140),100),
            Button('Go to point',(10,160),'mover'),
            Text('Use - for South',(10,180)),
            Text('Mouse: ',(10,360)),
            Button('Get image',(10,20),getImage)
        ]
    def checkCollision(self,point):
        point = [point[0]-840,point[1]]
        for item in self.holding:
            if type(item) == Button:
                if item.rect.collidepoint(point):
                    return item.getFunc()
            if type(item) == InputBox:
                if item.border_rect.collidepoint(point):
                    self.current_typer = self.holding.index(item)
                    return 'typer'
    def fetchData(self,inde):
        return self.holding[inde].getText()
    def takeText(self,key):
        self.holding[self.current_typer].upText(key)
    def update(self):
        for item in self.holding:
            item.update(sidescreen)

## Stand in function, does nothing, just shows a button works
def standIn():
    print('CLICKED')

def getImage():
    new_image = Image.open('mola-BIG.jpg')
    big_size = new_image.size
    width = big_size[0]/current_zoom
    height = big_size[1]/current_zoom
    img_x = big_size[0]*(start_cent[0]/840)
    img_y = big_size[1]*(start_cent[1]/840)
    left = img_x-(width/2)
    top = img_y-(height/2)
    print(left,top,width,height)
    new_image = new_image.crop((left,top,left+width,top+height))
    new_image.save('VIEWING-SPACE.jpg')

## Outputs the data inside the current list
def getList():
    with open(('Pairing '+str(datetime.now())[:-7].replace(':','-')+'.txt'),'w') as theFile:
        for item in current_list:
            print(item.get(),file=theFile)

## Destroys all data in the current list
def clearList():
    del current_list[:]

def makeImage(image1_data,image2_data):
    ## Data passed as:
    ## [name,points(numpy array)]
    img = back_image.img
    img_size = img.size
    
    ## Furthest points of data
    pre_top = min(image1_data[1][1].min(),image2_data[1][1].min())
    pre_bottom = max(image1_data[1][1].max(),image2_data[1][1].max())
    pre_left = min(image1_data[1][0].min(),image2_data[1][0].min())
    pre_right = max(image1_data[1][0].max(),image2_data[1][0].max())
    ## Getting all points as percentage values of width and height
    pre_height = pre_bottom-pre_top
    pre_width = pre_right-pre_left
    image1_data[1][1] = (image1_data[1][1]-pre_top)/pre_height
    image1_data[1][0] = (image1_data[1][0]-pre_left)/pre_width
    image2_data[1][1] = (image2_data[1][1]-pre_top)/pre_height
    image2_data[1][0] = (image2_data[1][0]-pre_left)/pre_width

    ## Ajusted values of data points for actual image
    adj_top = int(((pre_top)/largest[1])*img_size[1])
    adj_bottom = int(((pre_bottom)/largest[1])*img_size[1])
    adj_left = int(((pre_left)/largest[0])*img_size[0])
    adj_right = int(((pre_right)/largest[0])*img_size[0])
    adj_height = adj_bottom-adj_top
    adj_width = adj_right-adj_left
    tuned = min(adj_height,adj_width)
    extra_pixels = tuned*0.5
    one_side = extra_pixels/2
    #img = img.crop((adj_left,adj_top,adj_right,adj_bottom))
    img = img.crop((adj_left-one_side,adj_top-one_side,adj_right+one_side,adj_bottom+one_side))

    ## Resizing the image maintaining aspect ratio
    ## Tried to use thumbnail but only made small images
    base_size = img.size
    multiplier = 1
    if base_size[0] <= 2*base_size[1]:
        multiplier = 420/base_size[1]
    else:
        multiplier = 840/base_size[0]
    new_extra = int(one_side*multiplier)
    new_double = new_extra*2
    new_size = (int(base_size[0]*multiplier),int(base_size[1]*multiplier))
    img = img.resize(new_size)

    ## Getting actual values of points
    image1_data[1][1] = (image1_data[1][1]*(new_size[1]-new_double))+new_extra
    image1_data[1][0] = (image1_data[1][0]*(new_size[0]-new_double))+new_extra
    image2_data[1][1] = (image2_data[1][1]*(new_size[1]-new_double))+new_extra
    image2_data[1][0] = (image2_data[1][0]*(new_size[0]-new_double))+new_extra
    ## Moving data around...
    image1_data[1] = image1_data[1].transpose()
    image1_data[1][[2,3]] = image1_data[1][[3,2]]
    image1_data[1] = list(image1_data[1].flatten())
    image2_data[1] = image2_data[1].transpose()
    image2_data[1][[2,3]] = image2_data[1][[3,2]]
    image2_data[1] = list(image2_data[1].flatten())

    ## Add data polygons to image
    img_drawing = ImageDraw.Draw(img,'RGBA')
    img_drawing.polygon(image1_data[1],'#FFFFFF20','black')
    img_drawing.polygon(image2_data[1],'#FFFFFF20','black')

    ## Save image
    img_name = image1_data[0]+'__'+image2_data[0]+'.jpg'
    img.save('temporary/'+img_name)
    img.close()

    ## Return image name for excel
    return img_name

## Selects points from within the box
def selectList():
    print('Started')
    current_list = ''
    image_list = []
    image_text = ''
    ## If there is a drawer to use
    if drawer != None:
        pair_number = 1
        pair_column = 2
        image_row = 2
        overlap_row = 2
        ## Get the excel sheet to be editing
        workbook = openpyxl.Workbook()
        workbook.active.title = 'Pairs'
        workbook.create_sheet('Images')
        workbook.create_sheet('Overlap Coordinates')
        column_width = 8.5
        pair_sheet = workbook['Pairs']
        image_sheet = workbook['Images']
        coord_sheet = workbook['Overlap Coordinates']
        labels = ['Pair number','Image name','Pixel width','Emission angle','Latitude','Longitude']
        for i in range(len(labels)):
            pair_sheet.cell(i+1,1).value = labels[i]
        image_sheet.cell(1,1).value = 'Image name'
        image_sheet.cell(1,2).value = 'Download link'
        images = []
        colabels = ['Pair number','Image 1','Image 2','X1','Y1','X2','Y2','X3','Y3','X4','Y4','X5','Y5','X6','Y6','X7','Y7','X8','Y8']
        for i in range(len(colabels)):
            coord_sheet.cell(1,i+1).value = colabels[i]
        ## Make polygon from drawn shape
        draw_poly = shapely.geometry.Polygon(drawer.getPoly())
        group_count = 0
        ## For each group of boxes with n points
        for grouping in over_box_copies:
            poly_count = 0
            ## For each box in said group
            for box in grouping:
                ## Get a polygon shape
                the_copy = shapely.geometry.Polygon(numpy.transpose(box))
                ## Intersects with the drawer?
                if the_copy.intersects(draw_poly):
                    pair_letter = openpyxl.utils.get_column_letter(pair_column)
                    pair_row = 2
                    overlap_column = 1
                    pair_sheet.column_dimensions[pair_letter].width = column_width
                    pair_sheet.cell(1,pair_column).value = pair_number
                    pair_sheet.merge_cells(start_row=1,start_column=pair_column,end_row=1,end_column=pair_column+1)
                    coord_sheet.cell(overlap_row,overlap_column).value = pair_number
                    overlap_column += 1
                    ## Get names
                    pair_names = over_name_copies[group_count][poly_count]
                    shape1 = pair_names[0]
                    pair_sheet.cell(pair_row,pair_column).value = shape1
                    coord_sheet.cell(overlap_row,overlap_column).value = shape1
                    shape2 = pair_names[1]
                    pair_sheet.cell(pair_row,pair_column+1).value = shape2
                    coord_sheet.cell(overlap_row,overlap_column+1).value = shape2
                    pair_row += 1
                    overlap_column += 2
                    ## Find original index of this pair
                    original_place = scipy.stats.mode(numpy.where(over_names[group_count]==pair_names)[0])[0][0]
                    ## Fetch relevant data from the database
                    sql = 'select scaled_pixel_width,emission_angle,center_latitude,center_longitude,volume_id from Data where product_id=?'
                    shape1_data = Access.executeCTX(sql,(shape1,))[0]
                    shape2_data = Access.executeCTX(sql,(shape2,))[0]
                    for sh1, sh2 in zip(shape1_data[:-1],shape2_data[:-1]):
                        pair_sheet.cell(pair_row,pair_column).value = sh1
                        pair_sheet.cell(pair_row,pair_column+1).value = sh2
                        pair_row += 1
                    ## Get the index and data of the composing images
                    original_shape1 = numpy.where(names==shape1)[0][0]
                    original_shape1_data = boxes[original_shape1]
                    original_shape2 = numpy.where(names==shape2)[0][0]
                    original_shape2_data = boxes[original_shape2]
                    ## Make the image and put into excel
                    made_image_name = makeImage([shape1,numpy.copy(original_shape1_data)],[shape2,numpy.copy(original_shape2_data)])
                    made_image = Image.open('temporary/'+made_image_name)
                    made_size = made_image.size
                    made_image.close()
                    multiplier = ((column_width*2)*7)/made_size[0]
                    excel_image = openpyxl.drawing.image.Image('temporary/'+made_image_name)
                    excel_image.width = made_size[0]*multiplier
                    excel_image.height = made_size[1]*multiplier
                    excel_image.anchor = pair_letter+str(pair_row)
                    pair_sheet.add_image(excel_image)
                    ## Add name and web link if not already in file
                    if shape1 not in image_list:
                        images.append([shape1,'https://pds-imaging.jpl.nasa.gov/data/mro/ctx/'+shape1_data[4].lower()+'/data/'+shape1+'.IMG'])
                        image_list.append(shape1)
                    if shape2 not in image_list:
                        images.append([shape2,'https://pds-imaging.jpl.nasa.gov/data/mro/ctx/'+shape2_data[4].lower()+'/data/'+shape2+'.IMG'])
                        image_list.append(shape2)
                    ## Make a string out of the points of the pair
                    points = numpy.transpose(over_boxes[group_count][original_place])
                    points_string = str(len(points)-1)+' '
                    for point in points[:-1]:
                        point_x = 180-(point[0]*inv_pix[0])
                        point_y = 90-(point[1]*inv_pix[1])
                        coord_sheet.cell(overlap_row,overlap_column).value = point_x
                        coord_sheet.cell(overlap_row,overlap_column+1).value = point_y
                        overlap_column += 2
                    overlap_row += 1
                    pair_column += 2
                    pair_number += 1
                poly_count += 1
            group_count += 1
    def imageKey(image_item):
        return image_item[0]
    images.sort(key=imageKey)
    for image_item in images:
        image_sheet.cell(image_row,1).value = image_item[0]
        image_sheet.cell(image_row,2).value = image_item[1]
        image_row += 1
    time_name = 'temporary/'+str(datetime.now())
    time_name = time_name.replace(' ','-')
    time_name = time_name.replace(':','-')
    time_name = time_name.replace('.','-')
    time_name += '.xlsx'
    workbook.save(filename=time_name)
    workbook.close()
    for filename in os.listdir('temporary'):
        if filename.endswith('.jpg'):
            os.remove('temporary/'+filename)
    print('Done')

def makePoly(points,col='black',pixel_width=1):
    pygame.draw.polygon(screen,colors[col],points,pixel_width)

def makeInvisiPoly(points,col='white'):
    new_surf = pygame.Surface(largest)
    new_surf.set_alpha(80)
    new_surf.fill(colors['masks'])
    new_surf.set_colorkey((255,0,255))
    pygame.draw.polygon(new_surf,colors[col],points)
    screen.blit(new_surf,(0,0))

def changeList(arr,zoom,move,remove=True):
    arr[:,0,:] = (arr[:,0,:]*zoom)-move[0]
    arr[:,1,:] = (arr[:,1,:]*zoom)-move[1]
    if remove:
        index = 0
        deleting = []
        for item in arr:
            x_check1 = (item[0,:]<=largest[0])
            x_check2 = (item[0,:]>=0)
            y_check1 = (item[1,:]<=largest[1])
            y_check2 = (item[1,:]>=0)
            if not (True in x_check1 and True in x_check2 and True in y_check1 and True in y_check2):
                deleting.append(index)
            index += 1
        return deleting
    else:
        return None

def changeCenters(arr,zoom,move):
    arr[:,0] = (arr[:,0]*zoom)-move[0]
    arr[:,1] = (arr[:,1]*zoom)-move[1]

## Displays a crosshair in the middle of the screen, just liked it
class CrossHair:
    def __init__(self):
        self.vertical = pygame.Rect(418,199,2,20)
        self.horizontal = pygame.Rect(409,208,20,2)
    def update(self):
        pygame.draw.rect(screen,colors['black'],self.vertical)
        pygame.draw.rect(screen,colors['black'],self.horizontal)

## ---- SQL Data Collection ---- ##

## Gets the data from the database
def getData():
    sql = 'select u_l_lo,u_l_la,u_r_lo,u_r_la,l_l_lo,l_l_la,l_r_lo,l_r_la from Data where product_id not like "%999W"'
    return Access.executeCTX2(sql,())

## Gets the raw data from the original database
def getRawData():
    sql = '''select
            upper_left_longitude,upper_left_latitude,
            upper_right_longitude,upper_right_latitude,
            lower_left_longitude,lower_left_latitude,
            lower_right_longitude,lower_right_latitude,
            product_id
            from Data where product_id not like "%999W"'''
            #in ('P09_004493_1808_XI_00N176W','F02_036456_1794_XN_00S176W','J04_046399_1810_XN_01N177W','P05_002792_1773_XI_02S177W')'''
    return Access.executeCTX(sql,())

data = getRawData()#[:10000]

## For all image data, the first axis denotes the image element in the list of all data
## The second axis denotes the x and y sides of all points, 0 being x, 1 being y
## The third axis represents which point is being looked at
## So to get the third points x position from the 52nd image we have [51,0,2]

boxes = numpy.array([[[item[0],item[2],item[4],item[6]],[item[1],item[3],item[5],item[7]]] for item in data])
names = numpy.array([item[8] for item in data])
boxes[:,0,:] = (boxes[:,0,:]+180)%360
locations = list(zip(numpy.where(boxes[:,0,2]<45)[0]))
for i in locations:
    if boxes[i,0,0] > 270:
        boxes[i,0,0] -= 360
    if boxes[i,0,1] > 270:
        boxes[i,0,1] -= 360
    if boxes[i,0,3] > 270:
        boxes[i,0,3] -= 360
boxes[:,0,:] = pix[0]*(360-boxes[:,0,:])
boxes[:,1,:] = pix[1]*(90-boxes[:,1,:])
box_copies = numpy.copy(boxes)
name_copies = numpy.copy(names)
over_boxes = [[],[],[],[],[],[]]
over_names = [[],[],[],[],[],[]]
over_centers = [[],[],[],[],[],[]]
over_box_copies = [[],[],[],[],[],[]]
over_name_copies = [[],[],[],[],[],[]]
over_center_copies = [[],[],[],[],[],[]]
total_bounds = []
total_centers = []

## ---- ---- ##

bar = SideBar()
cross = CrossHair()
back_image = Picture()

## Variables used in control during program loop
quitt = False
moved = False
resized = False
hidden = True
more_hidden = False
current_zoom = 1.0
start_cent = [largest[0]/2,largest[1]/2]
current_cent = [largest[0]/2,largest[1]/2]
changeover = False
find = False
parentals = ['none','none']
current_list = []
shifting = False
shifting_instance = 0
drawing_instance = 0
pressed = False
drawing = False
drawer = None
typing = False
back_vis = True
get_data = False
checked_pos = False
scroll_4 = False
scroll_5 = False
## x,y,z, where z is in/out
directions = [0,0,0]

while quitt == False:
    ## Runs through all events for any updates
    for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
            event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if shifting:
                    if shifting_instance != drawing_instance:
                        if pygame.mouse.get_pos()[0] <= 840:
                            drawing = True
                            m_pos = pygame.mouse.get_pos()
                            posy = [
                                (m_pos[0]+(current_cent[0]-(largest[0]/2)))/current_zoom,
                                (m_pos[1]+(current_cent[1]-(largest[1]/2)))/current_zoom
                            ]
                            drawer = PolyDrawn(posy,m_pos)
                            drawing_instance = shifting_instance
                    else:
                        if pygame.mouse.get_pos()[0] <= 840:
                            m_pos = pygame.mouse.get_pos()
                            posy = [
                                (m_pos[0]+(current_cent[0]-(largest[0]/2)))/current_zoom,
                                (m_pos[1]+(current_cent[1]-(largest[1]/2)))/current_zoom
                            ]
                            drawer.addPoint(posy,m_pos)
            if event.button == 4:
                scroll_4 = True
                directions[2] += 1
            if event.button == 5:
                scroll_5 = True
                directions[2] -= 1
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                #if shifting:
                #    drawing = False
                #    if drawer != None:
                #        drawer.pickUp(current_zoom,current_cent)
                pressed = True
        if event.type == pygame.QUIT:
            pygame.quit()
            quitt = True
        if event.type == pygame.KEYDOWN:
            if not typing:
                # ## Zoom in
                # if event.key == pygame.K_EQUALS:
                #     directions[2] += 1
                # ## Zoom out
                # if event.key == pygame.K_MINUS:
                #     directions[2] -= 1
                if event.key == pygame.K_LEFT:
                    directions[0] += 1
                if event.key == pygame.K_RIGHT:
                    directions[0] -= 1
                if event.key == pygame.K_UP:
                    directions[1] += 1
                if event.key == pygame.K_DOWN:
                    directions[1] -= 1
                if event.key == pygame.K_t:
                    print(len(box_copies))
                if event.key == pygame.K_h:
                    hidden = not hidden
                    if hidden == False:
                        changeover = True
                if event.key == pygame.K_g:
                    if current_zoom < 20:
                        print("Won't perform check at this zoom")
                    else:
                        find = True
                        changeover = True
                if event.key == pygame.K_f:
                    more_hidden = not more_hidden
                    if more_hidden == False:
                        changeover = True
                if event.key in [pygame.K_LSHIFT,pygame.K_RSHIFT]:
                    pygame.mouse.set_cursor(*my_cursors['pointhand'])
                    shifting = True
                    shifting_instance += 1
                if event.key == pygame.K_y:
                    back_vis = not back_vis
                if event.key == pygame.K_u:
                    get_data = not get_data
                if event.key == pygame.K_r:
                    print('Three points:',len(over_box_copies[0]))
                    print('Four points:',len(over_box_copies[1]))
                    print('Five points:',len(over_box_copies[2]))
                    print('Six points:',len(over_box_copies[3]))
                    print('Seven points:',len(over_box_copies[4]))
                    print('Eight points:',len(over_box_copies[5]))
                    print()
            else:
                bar.takeText(pygame.key.name(event.key))
        if event.type == pygame.KEYUP:
            if not typing:
                # if event.key == pygame.K_EQUALS:
                #     directions[2] -= 1
                # if event.key == pygame.K_MINUS:
                #     directions[2] += 1
                if event.key == pygame.K_LEFT:
                    directions[0] -= 1
                if event.key == pygame.K_RIGHT:
                    directions[0] += 1
                if event.key == pygame.K_UP:
                    directions[1] -= 1
                if event.key == pygame.K_DOWN:
                    directions[1] += 1
                if event.key in [pygame.K_LSHIFT,pygame.K_RSHIFT]:
                    pygame.mouse.set_cursor(*my_cursors['arrow'])
                    shifting = False

    ## Exits the program loop
    if quitt == True:
        break

    ## Checks if anything happened when the mouse clicked
    if pressed:
        mouse_pos = pygame.mouse.get_pos()
        '''
        ## If shift was held down, check if a data point was pressed
        if shifting:
            for box in over_buttons:
                if box.getMiniMe().collidepoint(mouse_pos):
                    current_list.append(OutData(box))
        '''
        ## Finds and gets the result of any button pressing
        result = bar.checkCollision(mouse_pos)
        if result == 'typer':
            typing = True
        elif result == 'mover':
            typing = False
            ## Set the zoom
            current_zoom = 50.0
            ## Reset the position
            start_cent = [largest[0]/2,largest[1]/2]
            current_cent = [int(start_cent[0]*current_zoom),int(start_cent[1]*current_zoom)]
            ## Get the points
            point = []
            try:
                xer = bar.fetchData(10)
                vlue = ((int(xer)+180)%360)-180
                point.append((int(xer)+180)%360)
            except ValueError:
                point.append(180)
            try:
                yer = bar.fetchData(9)
                point.append(int(yer))
            except ValueError:
                point.append(0)
            ## Calculate the distance to the desired point
            x = int(((pix[0]*(360-point[0]))*current_zoom)-current_cent[0])
            y = int(((pix[1]*(90-point[1]))*current_zoom)-current_cent[1])
            ## Adjust
            current_cent[0] += x
            start_cent[0] += x/current_zoom
            current_cent[1] += y
            start_cent[1] += y/current_zoom
            ## Announce the movement
            moved = True
        elif result != None:
            typing = False
            result()
        else:
            typing = False
    
    #if drawing:
    #    m_pos = pygame.mouse.get_pos()
    #    posy = [
    #        (m_pos[0]+(current_cent[0]-(largest[0]/2)))/current_zoom,
    #        (m_pos[1]+(current_cent[1]-(largest[1]/2)))/current_zoom
    #    ]
    #    drawer.recreate(posy)

    ## ZOOM!
    if directions[2] != 0:
        directions[2] = max(-1,min(1,directions[2]))
        if directions[2] == 1:
            current_zoom = current_zoom*1.05
        elif directions[2] == -1:
            if current_zoom != 1.0:
                current_zoom = current_zoom/1.05
            if current_zoom < 1.0:
                current_zoom = 1.0
        current_cent = [int(start_cent[0]*current_zoom),int(start_cent[1]*current_zoom)]
        moved = True
    ## Move up/down
    if directions[1] != 0:
        current_cent[1] -= 20*directions[1]
        start_cent[1] -= (20/current_zoom)*directions[1]
        moved = True
    ## Move left/right
    if directions[0] != 0:
        current_cent[0] -= 20*directions[0]
        start_cent[0] -= (20/current_zoom)*directions[0]
        moved = True

    ## Decides placement of data based on current zoom/position
    if moved or changeover:
        if moved:
            checked_pos = False
        #move_cent = [current_cent[0]-start_cent[0],current_cent[1]-start_cent[1]]
        move_cent = [current_cent[0]-largest[0]/2,current_cent[1]-largest[1]/2]
        if get_data:
            print(start_cent)
            print(current_cent)
            print(move_cent)
        back_image.redraw(current_zoom,move_cent)
        if drawer != None:
            drawer.modify(current_zoom,move_cent)
        if not more_hidden:
            index = 0
            over_box_copies = [[],[],[],[],[],[]]
            over_name_copies = [[],[],[],[],[],[]]
            over_center_copies = [[],[],[],[],[],[]]
            total_bounds = []
            total_centers = []
            for box_set in over_boxes:
                if type(box_set) != list:
                    over_box_copies[index] = numpy.copy(over_boxes[index])
                    deleting = changeList(over_box_copies[index],current_zoom,move_cent)
                    over_box_copies[index] = numpy.delete(over_box_copies[index],deleting,0)
                    over_name_copies[index] = numpy.delete(over_names[index],deleting)
                    over_center_copies[index] = numpy.delete(over_centers[index],deleting,0)
                    changeCenters(over_center_copies[index],current_zoom,move_cent)
                    total_bounds += [[item[:,i] for i in range(len(over_box_copies[index][0,0]))] for item in over_box_copies[index]]
                    total_centers += [[item[0],item[1]] for item in over_center_copies[index]]
                index += 1
        if not hidden or (find and not checked_pos):
            checked_pos = True
            box_copies = numpy.copy(boxes)
            deleting = changeList(box_copies,current_zoom,move_cent)
            box_copies = numpy.delete(box_copies,deleting,0)
            name_copies = numpy.delete(names,deleting)

    ## Finds all pairs from current images
    if find:
        find = False
        temping_over = [[],[],[],[],[],[]]
        index = 0
        over_boxes = [[],[],[],[],[],[]]
        over_names = [[],[],[],[],[],[]]
        over_centers = [[],[],[],[],[],[]]
        other_index = 0
        temping = []
        for box in box_copies:
            temping.append(shapely.geometry.Polygon((box[:,0],box[:,1],box[:,3],box[:,2])))
        ## Takes each image and checks it against all the other images
        for i in range(len(temping)-1):
            poly1 = temping.pop(0)
            for poly2 in temping:
                other_index += 1
                ## Checks whether the two polygons intersect
                if poly1.intersects(poly2):
                    try:
                        the_overlapped = poly1.intersection(poly2)
                        ## Removes anything that is a point rather than a polygon
                        ## Can be anything from 3 points up to 8 points
                        if type(the_overlapped) == shapely.geometry.Polygon:
                            points = the_overlapped.exterior.coords.xy
                            point = [list(points[0]),list(points[1])]
                            try:
                                temping_over[len(points[0])-4].append([points,name_copies[index],name_copies[other_index],the_overlapped.centroid.bounds[0:2]])
                            except IndexError:
                                print(poly1.exterior.xy)
                                print(poly2.exterior.xy)
                                print(name_copies[index])
                                print(name_copies[other_index])
                                print(len(points[0]))
                    ## Errors can occur occasionally so they need to be accounted for
                    except shapely.errors.TopologicalError:
                        continue
            index += 1
            other_index = index
        point_number = 0
        for pointers in temping_over:
            if pointers != []:
                over_boxes[point_number] = numpy.array([[[i for i in box[0][0]],[j for j in box[0][1]]] for box in pointers])
                over_names[point_number] = numpy.array([[box[1],box[2]] for box in pointers])
                over_centers[point_number] = numpy.array([[box[3][0],box[3][1]] for box in pointers])
                over_boxes[point_number][:,0,:] = (over_boxes[point_number][:,0,:]+move_cent[0])/current_zoom
                over_boxes[point_number][:,1,:] = (over_boxes[point_number][:,1,:]+move_cent[1])/current_zoom
                over_centers[point_number][:,0] = (over_centers[point_number][:,0]+move_cent[0])/current_zoom
                over_centers[point_number][:,1] = (over_centers[point_number][:,1]+move_cent[1])/current_zoom
            point_number += 1
        index = 0
        over_box_copies = [[],[],[],[],[],[]]
        over_name_copies = [[],[],[],[],[],[]]
        over_center_copies = [[],[],[],[],[],[]]
        total_bounds = []
        total_centers = []
        for box_set in over_boxes:
            if type(box_set) != list:
                over_box_copies[index] = numpy.copy(over_boxes[index])
                deleting = changeList(over_box_copies[index],current_zoom,move_cent)
                over_box_copies[index] = numpy.delete(over_box_copies[index],deleting,0)
                over_name_copies[index] = numpy.delete(over_names[index],deleting,0)
                over_center_copies[index] = numpy.delete(over_centers[index],deleting,0)
                changeCenters(over_center_copies[index],current_zoom,move_cent)
                total_bounds += [[item[:,i] for i in range(len(over_box_copies[index][0,0]))] for item in over_box_copies[index]]
                total_centers += [[item[0],item[1]] for item in over_center_copies[index]]
            index += 1

    ## Updates any text on screen that changes
    bar.holding[1].edit(('Zoom: '+str(current_zoom)))
    bar.holding[2].edit(('FPS: '+str(clock.get_fps())))
    bar.holding[3].edit(('Coordinates: '+str(round(90-(start_cent[1]*inv_pix[1]),2))+'N, '+str(round(180-(start_cent[0]*inv_pix[0]),2))+'W'))
    mouse_pos = pygame.mouse.get_pos()
    #if mouse_pos[0]<=largest[0]:
    #    bar.holding[13].edit(('Mouse: '+str(round(90-(mouse_pos[1]*inv_pix[1]),2))+'N, '+str(round(180-(mouse_pos[0]*inv_pix[0]),2))+'W'))

    ## Section for displaying the parents of any pair hovered over
    '''
    if not more_hidden:
        for box in over_buttons:
            bounds = box.getMiniMe()
            position = pygame.mouse.get_pos()
            if bounds.top<position[1]<bounds.bottom and bounds.left<position[0]<bounds.right:
                parentals = box.hover()
    bar.holding[4].edit(('Parent 1: '+parentals[0]))
    bar.holding[5].edit(('Parent 2: '+parentals[1]))
    parentals = ['none','none']
    '''

    ## Clears the screen and updates all images to be redrawn
    screen.fill(colors['white'])
    #sidescreen.fill(colors['white'])
    if back_vis:
        back_image.update()
    if not more_hidden:
        for box in total_bounds:
            makeInvisiPoly(box)
        for box in total_bounds:
            makePoly(box)
        for box in total_centers:
            dist = 4
            adjust = 2
            box = [box[0]-adjust,box[1]-adjust]
            bounds = (box,[box[0]+dist,box[1]],[box[0]+dist,box[1]+dist],[box[0],box[1]+dist])
            makePoly(bounds,'redde',0)
    if not hidden:
        for item in box_copies:
            bounds = (item[:,0],item[:,1],item[:,3],item[:,2])
            makePoly(bounds)
    if drawer != None:
        drawer.update()
    moved = False
    pressed = False
    changeover = False
    if scroll_4:
        scroll_4 = False
        directions[2] -= 1
    if scroll_5:
        scroll_5 = False
        directions[2] += 1
    bar.update()
    screen.blit(sidescreen,(840,0))
    cross.update()
    pygame.display.update()
    clock.tick(72)