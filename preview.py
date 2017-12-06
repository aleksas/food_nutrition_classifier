from PIL import Image, ImageChops, ImageTk, ImageDraw
import tkinter
import os
from copy import deepcopy
from sqlite_data_loader import SQLiteDataLoader

sdl = SQLiteDataLoader('data.sqlite', 'image_data_299.sqlite')

offset = 0
prev_offsets = []

col_red = (255,0,0,255)
col_purple = (255,0,255,255)
col_yellow = (255,255,0,255)
col_green = (0,255,0,255)
line_width = 1

classification_id = 9

rows = 4
images_per_row = 40
show_image_count = rows * images_per_row

columns = ['protein_rate', 'fat_rate', 'carbohydrate_rate']
image_count_by_cat_index = {}

prev_offsets = {}
people_ids = []
current_class_index = None

def on_label_enter(image_id, size):
	print ("%d: %s" % (image_id, str(size)))

def trim_borders(im, color=(255, 255, 255, 255)):
	bg = Image.new(im.mode, im.size, color)
	diff = ImageChops.difference(im, bg)
	diff = ImageChops.add(diff, diff, 2.0, -100)
	bbox = diff.getbbox()
	if bbox:
		return im.crop(bbox)

def display_images(frame, top_offset, offset):
	global info

	sum_width = 0

	#im_w = root.winfo_width() // columns
	im_h = (root.winfo_height() - top_offset) // rows

	for widget in frame.winfo_children():
		widget.grid_forget()
	print ("Class %d, offset %d" % (current_class_index, offset))

	i = 0
	row_count = 0

	current_frame = tkinter.Frame(frame, relief='flat', borderwidth=0)
	current_frame_row = 0
	current_frame.grid(column = 0, row = current_frame_row, padx=0, pady=0)

	eval_link = lambda x, y: (lambda p: on_label_enter(x, y))


	for image_id in sdl.get_image_ids_by_condition_index(current_class_index, classification_id, offset, show_image_count):
		orig_image = Image.open(sdl.get_image_data_by_id(image_id))
		orig_size = orig_image.size
		orig_image_RGB = orig_image.convert('RGB')
		del orig_image

		image, scale = resizeImage(orig_image_RGB, (root.winfo_width(), im_h))
		del orig_image_RGB

		size = image.size

		if sum_width + image.size[0] >= root.winfo_width():
			row_count += 1
			if row_count >= rows:
				break;

			sum_width = 0

			current_frame = tkinter.Frame(frame, relief='flat', borderwidth=0)
			current_frame_row += 1
			current_frame.grid(column = 0, row = current_frame_row, padx=0, pady=0)

		sum_width += image.size[0]

		photo = ImageTk.PhotoImage(image)
		label = tkinter.Label(current_frame, image=photo)
		label.grid(row=0, column=i, padx=0, pady=0)
		label.image = photo
		label.bind("<Enter>", eval_link(image_id, orig_size))

		i += 1

	return offset + i

def resizeImage(image, size):
	new_width = int(size[1] / image.size[1] * image.size[0])

	return (image.resize((new_width, size[1]), Image.ANTIALIAS), size[1] / float(image.size[1]))

def next_class(event=None):
    global prev_offsets
    global current_class_index

    if current_class_index not in prev_offsets:
        prev_offsets[current_class_index] = []

    if len(prev_offsets[current_class_index]) > 0:
        prev_offsets[current_class_index] = prev_offsets[current_class_index][:-1]

    current_class_index += 1
    current_class_index %= len(sdl.get_condition_indeces(classification_id))

    show_next_batch()

def prev_class(event=None):
    global prev_offsets
    global current_class_index

    if current_class_index not in prev_offsets:
        prev_offsets[current_class_index] = []

    if len(prev_offsets[current_class_index]) > 0:
        prev_offsets[current_class_index] = prev_offsets[current_class_index][:-1]

    current_class_index -= 1
    if current_class_index < 0:
        current_class_index += len(sdl.get_condition_indeces(classification_id))

    show_next_batch()

def show_next_batch(event=None):
    global prev_offsets

    if current_class_index not in prev_offsets:
        prev_offsets[current_class_index] = []

    start_offset = 0
    if  len(prev_offsets[current_class_index]) > 0:
        start_offset = prev_offsets[current_class_index][-1][1]

    print("Class %d." % (current_class_index, ))
    image_count = sdl.get_image_count_by_condition_index(current_class_index, classification_id, 1, 9000000000)

    if start_offset < image_count:
        end_offset = display_images(photo_frame, top_offset, start_offset)
        prev_offsets[current_class_index].append((start_offset, end_offset))

def show_prev_batch(event=None):
    global prev_offsets

    if current_class_index not in prev_offsets:
        prev_offsets[current_class_index] = []

    if len(prev_offsets[current_class_index]) > 0:
        prev_offsets[current_class_index] = prev_offsets[current_class_index][:-1]

    if len(prev_offsets[current_class_index]) > 0:
        prev_offsets[current_class_index] = prev_offsets[current_class_index][:-1]
    show_next_batch()


root = tkinter.Tk()

root.geometry('600x400')

label = tkinter.Label(root, compound=tkinter.TOP)
label.grid(column = 0, row = 0)

controls_frame = tkinter.Frame(root, relief='flat', borderwidth=0)
controls_frame.grid(column = 0, row = 0)

photo_frame = tkinter.Frame(root, relief='flat', borderwidth=0)
photo_frame.grid(column = 0, row = 1)

top_offset = 0

button_prev = tkinter.Button(controls_frame, text='\u2191 UP', command=lambda: show_prev_batch())
button_next = tkinter.Button(controls_frame, text='DOWN \u2193', command=lambda: show_next_batch())
button_prev_class = tkinter.Button(controls_frame, text='PREVIOUS CLASS  \u2190', command=lambda: prev_class())
button_next_class = tkinter.Button(controls_frame, text=' \u2192 NEXT CLASS', command=lambda: next_class())

button_quit = tkinter.Button(controls_frame, text='Quit', command=root.quit)

button_prev_class.grid(column = 1, row = 0)
button_prev.grid(column = 2, row = 0)
button_next.grid(column = 3, row = 0)
button_next_class.grid(column = 4, row = 0)
button_quit.grid(column = 5, row = 0)

root.bind("<Up>", show_prev_batch)
root.bind("<Down>", show_next_batch)
root.bind("<Left>", prev_class)
root.bind("<Right>", next_class)

root.update()

top_offset = button_prev.winfo_height()

current_class_index = 0

samples = sdl.get_image_count_by_condition_index(current_class_index, classification_id, 1, 9000000000)

print (samples)

show_next_batch(None)

root.mainloop()
