#!/usr/bin/python3
from PIL import ImageTk
import PIL.Image
from tkinter import *
import glob, os, math
import subprocess

#TODO:
#-add menu bar at top with configuration and exit options
#-add labels with names of target folders
#-add image selecting feature

#A bug in PIL currently causes the application to crash when loading a large number of images. PIL also doesn't like images that have been programmatically truncated incorrectly (inconsistent sizes?)

folder = os.path.dirname(os.path.realpath(__file__))+"\\"

#accepts folder path as argument
if len(sys.argv) > 1:
    folder = sys.argv[1]
    if os.name != "posix":
        if folder[-1] != "\\":
            folder += "\\"
    else:
        if folder[-1] != "/":
            folder += "/"

print("Folder location: " + folder)

location_y = 0
max_location_x = 0 #keeps track of horizontal scrolling area

root = Tk()
root.title("Image Organizer")
canvas_width = 500
canvas_height = 500
#root.geometry(str(canvas_width+1)+'x'+str(canvas_height+1))

menu_canvas = Canvas(root, width=canvas_width, height=30)
menu_canvas.pack(fill=BOTH, expand=1)

xscrollbar = Scrollbar(root, orient=HORIZONTAL)
xscrollbar.pack(side=BOTTOM, fill=X)
yscrollbar = Scrollbar(root, orient=VERTICAL)
yscrollbar.pack(side=RIGHT, fill=Y)

canvas = Canvas(root, width=canvas_width, height=canvas_height, scrollregion=(0,0,max_location_x,location_y), xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
canvas.pack(fill=BOTH, expand=1)

xscrollbar.config(command=canvas.xview)
yscrollbar.config(command=canvas.yview)

destination_locations = {"blue": "", "red": "", "orange": "", "green": ""} #where the images can be copied/moved to
image_names = {}
images_to_move = {"blue": [], "red": [], "orange": [], "green": []}

image_count = 0
reload_images = False
thumbnail_sizes = [(50, 50), (128, 128), (300, 300), (600, 600)] #size 0 is the current size, 1 is small, 2 is medium, 3 is large
current_size = 0 #0-3, tells us which set of thumbnails to redraw if resizing screen
images = [] #original images
resizing_images = [] #copied from images, used as base to resize so don't mess with originals
# resized_images = []
stored_images = [] #list of lists of images of different sizes
types = ["*.gif", "*.jpg", "*.png", "*.jpeg"]
#types += [type.upper() for type in types] #glob doesn't care about capitalization, at least on Windows, so no need for this

print("Looking for types: " + str(types))

def place_images(event):
    global canvas_width
    global canvas_height
    global current_size
    canvas_width = event.width
    canvas_height = event.height
    display_images(current_size)

canvas.bind("<Configure>", place_images)


def resize_down_click():
    global thumbnail_sizes
    global reload_images
    global stored_images
    global current_size
    current_size = 0
    thumbnail_sizes[0] = thumbnail_sizes[0][0]-10, thumbnail_sizes[0][1]-10
    if thumbnail_sizes[0][0] < 1 or thumbnail_sizes[0][1] < 1:
        thumbnail_sizes[0] = 1, 1
    print("Custom size: "+str(thumbnail_sizes[0]))
    stored_images[0] = resize_images(thumbnail_sizes[0])
    display_images(0)

#expensive because has to reload all images again
def resize_up_click():
    global thumbnail_sizes
    global reload_images
    global stored_images
    global current_size
    current_size = 0
    thumbnail_sizes[0] = thumbnail_sizes[0][0]+10, thumbnail_sizes[0][1]+10
    print("Custom size: "+str(thumbnail_sizes[0]))
    reload_images = True
    stored_images[0] = resize_images(thumbnail_sizes[0])
    display_images(0)

def resize_small_click():
    global thumbnail_sizes
    global current_size
    current_size = 1
    if thumbnail_sizes[0][0] < thumbnail_sizes[1][0] or thumbnail_sizes[0][1] < thumbnail_sizes[1][1]:
        global reload_images
        reload_images = True
    thumbnail_sizes[0] = thumbnail_sizes[1]
    display_images(1)
    
def resize_med_click():
    global thumbnail_sizes
    global current_size
    current_size = 2
    if thumbnail_sizes[0][0] < thumbnail_sizes[2][0] or thumbnail_sizes[0][1] < thumbnail_sizes[2][1]:
        global reload_images
        reload_images = True
    thumbnail_sizes[0] = thumbnail_sizes[2]
    display_images(2)

def resize_large_click():
    global thumbnail_sizes
    global current_size
    current_size = 3
    if thumbnail_sizes[0][0] < thumbnail_sizes[3][0] or thumbnail_sizes[0][1] < thumbnail_sizes[3][1]:
        global reload_images
        reload_images = True    
    thumbnail_sizes[0] = thumbnail_sizes[3]
    display_images(3)
    
blue_var = StringVar()
blue_var.set(destination_locations["blue"])

red_var = StringVar()
red_var.set(destination_locations["red"])

orange_var = StringVar()
orange_var.set(destination_locations["orange"])

green_var = StringVar()
green_var.set(destination_locations["green"])

def select_location(color):
    #take user input for image destination
    print("Do something "+color)
    global destination_locations
    top = Toplevel()
    top.geometry("%dx%d%+d%+d" % (200, 200, 300, 300))
    top.title("Choose "+color+" destination")
    label = Label(top, text="Type in absolute path\n of destination for "+color+" images")
    label.pack(fill=X)
    entry = Entry(top)
    entry.insert(0, destination_locations[color])
    entry.pack()
    entry.focus_set()
    def save_new_location():
        print("New entry "+entry.get())
        destination_locations[color] = entry.get()
        print("Destination for "+color+" is "+"\""+destination_locations[color]+"\"")
        if color == "blue":
            global blue_var
            blue_var.set(destination_locations[color])
        elif color == "red":
            global red_var
            red_var.set(destination_locations[color])
        elif color == "orange":
            global orange_var
            orange_var.set(destination_locations[color])
        elif color == "green":
            global green_var
            green_var.set(destination_locations[color])
    save = Button(top, text="Save", command=save_new_location)
    save.pack()
    close = Button(top, text="Close", command=top.destroy)
    close.pack()

def execute_moves():
    #prepare terminal or command line commands to mass-copy images and execute them, then delete images
    print("Moving images")
    global folder
    command = []
    image_set = set()
    for color in images_to_move:
        print(color)
        if images_to_move[color] != []:
            if os.name != "posix":
                command = ["robocopy", folder, destination_locations[color]]
            else:
                command = ["cp"]
            for image in images_to_move[color]:
                print("\t"+image.split("\\")[-1])
                command.append(image.split("\\")[-1])
                image_set.add(image)
            if os.name == "posix":
                command.append(destination_locations[color])
            print("Copying images with command: \n"+str(command))
            #execute command
            subprocess.run(command, shell=True)
    if os.name != "posix":
        command = ["del"]
    else:
        command = ["rm"]
    for image in image_set:
        command.append(image.split("\\")[-1])
    print("Deleting images with command: "+str(command))
    #delete images
    subprocess.run(command, shell=True)
    command = []
    image_set.clear()

resize_down_button = Button(menu_canvas, text="-", command=resize_down_click, width=10)
resize_down_wind = menu_canvas.create_window(0, 0, anchor=NW, window=resize_down_button, height=30, width=30)

resize_up_button = Button(menu_canvas, text="+", command=resize_up_click, width=10)
resize_up_wind = menu_canvas.create_window(30, 0, anchor=NW, window=resize_up_button, height=30, width=30)

resize_small_button = Button(menu_canvas, text="o", command=resize_small_click, width=10)
resize_small_wind = menu_canvas.create_window(60, 0, anchor=NW, window=resize_small_button, height=30, width=30)

resize_med_button = Button(menu_canvas, text="0", command=resize_med_click, width=10)
resize_med_wind = menu_canvas.create_window(90, 0, anchor=NW, window=resize_med_button, height=30, width=30)

resize_large_button = Button(menu_canvas, text="O", command=resize_large_click, width=10)
resize_large_wind = menu_canvas.create_window(120, 0, anchor=NW, window=resize_large_button, height=30, width=30)

blue_folder_button = Button(menu_canvas, textvariable=blue_var, command=lambda: select_location("blue"), bg="blue", width=10)
blue_folder_wind = menu_canvas.create_window(150, 0, anchor=NW, window=blue_folder_button, height=30, width=50)

red_folder_button = Button(menu_canvas, textvariable=red_var, command=lambda: select_location("red"), bg="red", width=10)
red_folder_wind = menu_canvas.create_window(200, 0, anchor=NW, window=red_folder_button, height=30, width=50)

orange_folder_button = Button(menu_canvas, textvariable=orange_var, command=lambda: select_location("orange"), bg="orange", width=10)
orange_folder_wind = menu_canvas.create_window(250, 0, anchor=NW, window=orange_folder_button, height=30, width=50)

green_folder_button = Button(menu_canvas, textvariable=green_var, command=lambda: select_location("green"), bg="green", width=10)
green_folder_wind = menu_canvas.create_window(300, 0, anchor=NW, window=green_folder_button, height=30, width=50)

execute_button = Button(menu_canvas, text="Execute", command=execute_moves, width=10)
execute_wind = menu_canvas.create_window(350, 0, anchor=NW, window=execute_button, height=30, width=70)

def image_number(click_position_x, click_position_y):
    global thumbnail_sizes
    global canvas_width
    print("thumbnail width: "+str(thumbnail_sizes[0][0])+", height: "+str(thumbnail_sizes[0][1]))
    if click_position_x < 5 or click_position_y < 5:
        image_num = -1
    else:
        image_in_row = math.floor(click_position_x/(thumbnail_sizes[0][0]+10+5))
        row_number = math.floor(click_position_y/(thumbnail_sizes[0][1]+10+5))
        image_num = (row_number) * math.floor(canvas_width/(thumbnail_sizes[0][0]+10)) + (image_in_row)
        print("Image in row: "+str(image_in_row)+", row number: "+str(row_number)+", Image number: "+str(image_num))
    return image_num

def click(event):
    #clicking a 5 pixel box around the picture allows selecting that picture
    print("Creating box")
    print("Click at: "+str(event.x)+","+str(event.y))
    global thumbnail_sizes
    global location_y
    global canvas_width
    global image_count
    global image_names
    images_in_last_row = image_count%(math.floor(canvas_width/(thumbnail_sizes[0][0]+10))) #if images don't fit in screen, then div by 0 or mod by 0 error
    if images_in_last_row == 0:
        images_in_last_row = image_count
    print("Images in last row: "+str(images_in_last_row)+", canvas width: "+str(canvas_width))
    print("location y: "+str(location_y))
    #bug where 3 images present and image size = 100 and pressing at location (32x112) causes blue square to be selected incorrectly
    if event.y >= location_y + thumbnail_sizes[0][1]+5 or (event.y > location_y and event.y < location_y + thumbnail_sizes[0][1]+5 and event.x >= (images_in_last_row * (thumbnail_sizes[0][0]+10) - 5)):
        print("OUT OF BOUNDS")
    else:
        box_location = ""
        image_location = str(event.x - event.x%(thumbnail_sizes[0][0]+10) + 10)+","+str(event.y - event.y%(thumbnail_sizes[0][1]+10) + 10)
        if event.x%(thumbnail_sizes[0][0]+10) < (thumbnail_sizes[0][0]+10)/2:
            top_corner_x = event.x - event.x%(thumbnail_sizes[0][0]+10) + 5
            bottom_corner_x = top_corner_x+(thumbnail_sizes[0][0]+10)/2
            box_location += "left"
        else:
            top_corner_x = event.x - event.x%(thumbnail_sizes[0][0]+10) + (thumbnail_sizes[0][0]+10)/2 + 5
            bottom_corner_x = top_corner_x+(thumbnail_sizes[0][0]+10)/2
            box_location += "right"
        if event.y%(thumbnail_sizes[0][1]+10) < (thumbnail_sizes[0][1]+10)/2:
            top_corner_y = event.y - event.y%(thumbnail_sizes[0][1]+10) + 5
            bottom_corner_y = top_corner_y+(thumbnail_sizes[0][1]+10)/2
            box_location = "top" + box_location
        else:
            top_corner_y = event.y - event.y%(thumbnail_sizes[0][1]+10) + (thumbnail_sizes[0][1])/2 + 10
            bottom_corner_y = top_corner_y+(thumbnail_sizes[0][1]+10)/2
            box_location = "bottom" + box_location
        color = ""
        if box_location == "topleft":
            color = "blue"
        elif box_location == "topright":
            color = "red"
        elif box_location == "bottomleft":
            color = "orange"    
        elif box_location == "bottomright":
            color = "green"
        img_num = image_number(event.x, event.y)
        if img_num != -1:
            tag = str(img_num)+box_location
            if canvas.find_withtag(tag): #remove selection square and untag image
                print("Deleting square with tag: "+tag)
                canvas.delete(tag)
                canvas.dtag(canvas.find_withtag(color+str(img_num)), color+str(img_num))
                print("Removing '"+str(image_names[image_location])+"' from "+color+" list.")
                images_to_move[color].remove(str(image_names[image_location]))
            else: #add selection square and tag image
                print("Tag: "+tag+", top corner: "+str(top_corner_x)+","+str(top_corner_y)+", bottom corner: "+str(bottom_corner_x)+","+str(bottom_corner_y)+" "+box_location)
                canvas.create_rectangle(top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y, fill=color, tags=tag)
                canvas.tag_lower(tag)
                canvas.addtag_withtag(color+str(img_num), image_location)
                print("Image named '"+str(image_names[image_location])+"' selected with "+color+" tag.")
                images_to_move[color].append(str(image_names[image_location]))
            for item in canvas.find_all():
                print(canvas.gettags(item))
    print("Done")

canvas.bind("<ButtonPress-1>", click)

#display images on canvas
def display_images(im_size):
    image_number = 0
    global location_y
    global max_location_x
    location_x = 10
    location_y = 10
    max_location_x = 0
    global stored_images
    global thumbnail_sizes
    global images
    size = thumbnail_sizes[im_size]
    canvas.delete("image")
    for image in stored_images[im_size]:
        canvas.create_image(location_x, location_y, anchor=NW, image=image, tags=("image", str(location_x)+","+str(location_y))) #store image location as tag
        print("Canvas contents: "+str(canvas.find_all()))
        image_names[str(location_x)+","+str(location_y)] = images[image_number].filename
        image_number += 1
        location_x += size[0] + 10
        if location_x >= math.floor((canvas_width/(size[0]+10))) * (size[0]+10):
            if location_x > max_location_x:
                max_location_x = location_x - 10
            location_x = 10
            location_y += size[1] + 10
    print("location_y: "+str(location_y))
    print("max_location_x: "+str(max_location_x))
    canvas.configure(scrollregion=(0,0,canvas_width,location_y))

#resize images already loaded
def resize_images(size):
    global reload_images
    global resizing_images
    global images
    canvasImages = []
    print("Resizing to "+str(size[0])+"x"+str(size[1]))
    if reload_images:
        resizing_images[:] = []
        for im in images:
            print(im.filename)
            resizing_images.append(im.copy())
            resizing_images[-1].thumbnail(size)
            canvasImages.append(ImageTk.PhotoImage(resizing_images[-1]))
            print(canvasImages[-1])
        reload_images = False
    else:
        for im in resizing_images:
            im.thumbnail(size)
            canvasImages.append(ImageTk.PhotoImage(im))
    return canvasImages
    
#run first time
def load_images():
    global reload_images
    global stored_images
    global images
    global image_count
    for files in types:
        for infile in glob.glob(folder+files):
            #print(infile)
            file, ext = os.path.splitext(infile)
            images.append(PIL.Image.open(infile))
            image_count += 1
    print("Done loading "+str(image_count)+" images")
    reload_images = True
    for size in reversed(thumbnail_sizes): #load in reverse so we can just downscale images after loading them once (way faster)
        stored_images.insert(0, resize_images(size)) #insert generated lists backwards since they are generated in reverse order
    print("Done resizing and storing images")
    #display_images(0)
           
def main():
    load_images()
    root.mainloop()
    
if __name__ == "__main__":
    main()
