import sqlite3
import io
import numpy as np
from sqlite_data_loader import SQLiteDataLoader

database_path = '../recipes/data.sqlite'
image_data_database_path = '../recipes/image_data_299.sqlite'
sdl = SQLiteDataLoader(database_path, image_data_database_path)

classification_id = 11
step = 2

ranges = []
for protein in range(0, 11, step):
    p_range = (min(protein, 10), min(protein + step, 10))

    if (p_range[1] == p_range[0]):
        p_range = 0, 0

    for fat in range(0, 11, step):
        f_range = np.array((fat, min(10, fat + step)))

        if (f_range[1] == f_range[0]):
            f_range = 0, 0

        for carb in range(0, 11, step):
            c_range = np.array((carb, min(10, carb + step)))

            if (c_range[1] == c_range[0]):
                c_range = 0, 0

            if p_range[0] + f_range[0] + c_range[0] > 10:
                continue
            if p_range[1] + f_range[1] + c_range[1] < 10 + step:
                continue

            ranges.append((p_range, f_range, c_range))

centroids = []
partial_queries = []
for i in range(len(ranges)):
    rp, rf, rc = np.array(ranges[i]) / 10
    sp, sf, sc = '<', '<', '<'
    if rp[1] == 1:
        sp = '<='
    if rf[1] == 1:
        sf = '<='
    if rc[1] == 1:
        sc = '<='

    centroid = (np.sum(rp) / 2, np.sum(rf) / 2, np.sum(rc) / 2)
    centroid /= np.sum(centroid)
    entry = (i, classification_id, centroid[0], centroid[1], centroid[2])
    centroids.append(entry)

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

    #f = 'SELECT recipe_id from recipe_rates WHERE %s >= %f AND %s %s %f AND %s >= %f AND %s %s %f AND %s >= %f AND %s %s %f'
    #query = f % (cnp, rp[0], cnp, sp, rp[1], cnf, rf[0], cnf, sf, rf[1], cnc, rc[0], cnc, sc, rc[1])
    partial_queries.append('INSERT INTO recipe_classes (recipe_id, classification_id,  class) SELECT recipe_id, 11 as classification_id, %d as class from nutrition_rates WHERE %s AND %s AND %s;' % (i, cndp, cndf, cndc))

query = 'WITH tmp AS (\n%s\n)\nSELECT * FROM tmp' % ('\nUNION ALL\n'.join(partial_queries))
#print (query)
print ('\n'.join(partial_queries))

print ('\n\n\n')

for centroid in centroids:
    query = 'INSERT INTO centroids (id, classification_id,  protein, fat, carbohydrate) VALUES (%d, %d, %f, %f, %f);' %  centroid

    print (query)

sdl.fix_class_sequence(classification_id)

def get_condition_indeces(classification_id):
	q = 'SELECT MAX(class)+1 FROM recipe_classes WHERE classification_id=?'

	connection = sqlite3.connect(self.database_path)

	cursor = connection.cursor()
	params = (classification_id,)

	max_c = cursor.execute(q, params).fetchone()[0]

	connection.close()
	self.index_cache[classification_id] = range(max_c)
