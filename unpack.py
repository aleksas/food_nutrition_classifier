import os
import random
from PIL import Image
from sqlite_data_loader import SQLiteDataLoader

random.seed(1)

sdl = SQLiteDataLoader('data.sqlite', 'image_data_299.sqlite')

classification_id = 11
max_c = 2024

dst_directory = 'food_images/cid%d_max%d' % (classification_id, max_c)

VGG16_SIZE = (224, 224)
INCEPTION_V3_SIZE = (299, 299)

resize_image = None#VGG16_SIZE

train_p = 0.8
test_p = 0.1
valid_p = 0.1

split_db = False#True

for ci in sdl.get_classes(classification_id):
    ci_ids = sdl.get_image_ids_by_class(ci, classification_id, 0, 100000)
    image_ids = random.sample(ci_ids, min(max_c, len(ci_ids)))

    dst_image_dir = ''

    ci += 1
    if split_db:
        dst_train_ci_directory = '%s/train/%d' % (dst_directory, ci)
        dst_test_ci_directory  = '%s/test/%d'  % (dst_directory, ci)
        dst_valid_ci_directory = '%s/valid/%d' % (dst_directory, ci)

        for d in [dst_train_ci_directory, dst_test_ci_directory, dst_valid_ci_directory]:
            if not os.path.exists(d):
                os.makedirs(d)
    else:
        dst_image_dir = '%s/%d' % (dst_directory, ci)

        if not os.path.exists(dst_image_dir):
            os.makedirs(dst_image_dir)


    image_ids_len = len(image_ids)

    if split_db:
        train_image_c = image_ids_len * train_p
        test_image_c = image_ids_len * test_p
        valid_image_c = image_ids_len * valid_p

    for i in range(image_ids_len):
        image_id = image_ids[i]

        if split_db:
            if i >= 0 and i < train_image_c:
                dst_image_dir = dst_train_ci_directory
            elif i >= train_image_c and i < train_image_c + test_image_c:
                dst_image_dir = dst_test_ci_directory
            else:
                dst_image_dir = dst_valid_ci_directory

        im = Image.open(sdl.get_image_data_by_id(image_id))
        if resize_image != None:
            im.thumbnail(resize_image, Image.ANTIALIAS)
        im.save('%s/%d.jpg' % (dst_image_dir, image_id), "JPEG")
