import os
import random
from PIL import Image
from sqlite_data_loader import SQLiteDataLoader

sdl = SQLiteDataLoader('data.sqlite', 'image_data_299.sqlite')

classification_id = 11
max_c = 450

dst_directory = 'food_images/cid%d_max%d' % (classification_id, max_c)


train_p = 0.8
test_p = 0.1
valid_p = 0.1

for ci in sdl.get_condition_indeces(classification_id):
    image_ids = random.sample(sdl.get_image_ids_by_condition_index(ci, classification_id, 0, 100000), max_c)

    ci += 1
    dst_train_ci_directory = '%s/train/%d.%d' % (dst_directory, ci, ci)
    dst_test_ci_directory  = '%s/test/%d.%d'  % (dst_directory, ci, ci)
    dst_valid_ci_directory = '%s/valid/%d.%d' % (dst_directory, ci, ci)

    for d in [dst_train_ci_directory, dst_test_ci_directory, dst_valid_ci_directory]:
        if not os.path.exists(d):
            os.makedirs(d)

    image_ids_len = len(image_ids)
    dst_image_dir = ''

    train_image_c = image_ids_len * train_p
    test_image_c = image_ids_len * test_p
    valid_image_c = image_ids_len * valid_p

    for i in range(image_ids_len):
        image_id = image_ids[i]

        if i >= 0 and i < train_image_c:
            dst_image_dir = dst_train_ci_directory
        elif i >= train_image_c and i < train_image_c + test_image_c:
            dst_image_dir = dst_test_ci_directory
        else:
            dst_image_dir = dst_valid_ci_directory

        Image.open(sdl.get_image_data_by_id(image_id)).save('%s/%d.jpg' % (dst_image_dir, image_id))
