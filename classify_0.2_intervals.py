import sqlite3
import io
import numpy as np
from sqlite_data_loader import SQLiteDataLoader

database_path = 'data.sqlite'
image_data_database_path = 'image_data_299.sqlite'
sdl = SQLiteDataLoader(database_path, image_data_database_path)

classification_id = 11
step = .2

print ('DELETE FROM recipe_classes WHERE classification_id=%d;' % classification_id)
print ('DELETE FROM centroids WHERE classification_id=%d;' % classification_id)
print ('\n\n\n')

ranges = []
for protein in np.arange(0.0, 1.0, step):
    p_range = protein, protein + step

    for fat in np.arange(0.0, 1.0, step):
        f_range = fat, fat + step

        for carbs in np.arange(0.0, 1.0, step):
            c_range = carbs, carbs + step

            if p_range[0] + f_range[0] + c_range[0] > 1 + step * 1:
                continue
            if p_range[1] + f_range[1] + c_range[1] < 1:
                continue

            ranges.append((p_range, f_range, c_range))

centroids = []
partial_queries = []
offset = 0
for i in range(len(ranges)):
    rp, rf, rc = ranges[i]
    sp, sf, sc = '<', '<', '<'
    if rp[1] == 1.0:
        sp = '<='
    if rf[1] == 1.0:
        sf = '<='
    if rc[1] == 1.0:
        sc = '<='

    centroid = (np.sum(rp) / 2, np.sum(rf) / 2, np.sum(rc) / 2)
    centroid /= np.sum(centroid)

    cnp, cnf, cnc = 'protein_rate', 'fat_rate', 'carbohydrate_rate'

    cndp = '%s >= %.1f AND %s %s %.1f' % (cnp, rp[0], cnp, sp, rp[1])
    if rp[0] == rp[1] and rp[0] == 0:
        cndp = '%s = 0' % cnp

    cndf = '%s >= %.1f AND %s %s %.1f' % (cnf, rf[0], cnf, sf, rf[1])
    if rf[0] == rf[1] and rf[0] == 0:
        cndf = '%s = 0' % cnf

    cndc = '%s >= %.1f AND %s %s %.1f' % (cnc, rc[0], cnc, sc, rc[1])
    if rc[0] == rc[1] and rc[0] == 0:
        cndc = '%s = 0' % cnc

    cond  = 'WHERE ' + ' AND '.join([cndp, cndf, cndc])
    count = sdl.get_image_count_by_condition('nutrition_rates', cond)

    if int(count) <= 10:
        print (cond)
        print (count)
        offset += 1
        continue

    entry = (i - offset, classification_id, centroid[0], centroid[1], centroid[2])
    centroids.append(entry)

    #f = 'SELECT recipe_id from recipe_rates WHERE %s >= %f AND %s %s %f AND %s >= %f AND %s %s %f AND %s >= %f AND %s %s %f'
    #query = f % (cnp, rp[0], cnp, sp, rp[1], cnf, rf[0], cnf, sf, rf[1], cnc, rc[0], cnc, sc, rc[1])
    partial_queries.append('INSERT INTO recipe_classes (recipe_id, classification_id,  class) SELECT recipe_id, %d as classification_id, %d as class from nutrition_rates %s;' % (classification_id, i - offset, cond))

query = 'WITH tmp AS (\n%s\n)\nSELECT * FROM tmp' % ('\nUNION ALL\n'.join(partial_queries))
#print (query)
print ('\n'.join(partial_queries))

print ('\n\n\n')

for centroid in centroids:
    query = 'INSERT INTO centroids (id, classification_id,  protein, fat, carbohydrate) VALUES (%d, %d, %f, %f, %f);' %  centroid

    print (query)

sdl.fix_class_sequence(classification_id)
