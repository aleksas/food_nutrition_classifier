
import sqlite3
import io

class SQLiteDataLoader:
	def __init__(self, db_path='data.sqlite', image_db_path='image_data_299.sqlite'):
		self.database_path = db_path
		self.image_database_path = image_db_path
		self.index_cache = {}
		self.count_cache = {}
		self.nutrition_cache = {}
		self.range_count_cache = {}

	def get_classes(self, classification_id):
		if not classification_id in self.index_cache:
			q = 'SELECT MAX(class)+1 FROM recipe_classes WHERE classification_id=?'

			connection = sqlite3.connect(self.database_path)

			cursor = connection.cursor()
			params = (classification_id,)

			max_c = cursor.execute(q, params).fetchone()[0]

			connection.close()
			self.index_cache[classification_id] = range(max_c)

		return self.index_cache[classification_id]

	def fix_class_sequence(self, classification_id):
		q = 'SELECT class FROM recipe_classes WHERE classification_id=? GROUP BY class ORDER BY class ASC'

		connection = sqlite3.connect(self.database_path)

		cursor = connection.cursor()
		params = (classification_id,)

		initial_classes = cursor.execute(q, params).fetchall()

		for  i in range(len(initial_classes)):
			s1 = 'update recipe_classes set class=%d WHERE classification_id=%d and class=%d;' % (i, classification_id, initial_classes[i][0])
			s2 = 'update centroids set id=%d WHERE classification_id=%d and id=%d;' % (i, classification_id, initial_classes[i][0])
			print (s1)
			print (s2)

		connection.close()

	def get_nutrition_values(self, classification_id):
		if not classification_id in self.nutrition_cache:
			q = 'SELECT protein_rate, fat_rate, carbohydrate_rate, class FROM nutrition_rates, recipe_classes WHERE nutrition_rates.recipe_id = recipe_classes.recipe_id AND recipe_classes.classification_id = ?'

			params = (classification_id,)
			connection = sqlite3.connect(self.database_path)

			cursor = connection.cursor()
			self.nutrition_cache[classification_id] = cursor.execute(q, params).fetchall()

			connection.close()

		return self.nutrition_cache[classification_id]

	def get_image_count_by_class(self, ci, classification_id, factor, max):
		if not classification_id in self.count_cache:
			self.count_cache[classification_id] = {}

		if ci not in self.count_cache[classification_id] and ci is not None:
			q = 'WITH Tmp AS (SELECT recipe_id FROM recipe_classes WHERE classification_id=? AND class=?) SELECT COUNT(*) FROM images, Tmp WHERE images.recipe_id = Tmp.recipe_id'

			connection = sqlite3.connect(self.database_path)

			cursor = connection.cursor()
			params = (classification_id, ci)
			self.count_cache[classification_id][ci] = cursor.execute(q, params).fetchone()[0]

			print ("Class %d has %d images." % (ci, self.count_cache[classification_id][ci]))

			connection.close()

		count = self.count_cache[classification_id][ci]

		return min(int(count * factor), int(max * factor))

	def get_image_count_by_ranges(self, ci, classification_id, ranges):
		if not classification_id in self.range_count_cache:
			self.range_count_cache[classification_id] = {}

		if not classification_id in self.range_count_cache[ci]:
			q = 'SELECT count(*) FROM nutrition_rates WHERE protein_rate >= ? AND protein_rate <= ? AND fat_rate >= ? AND fat_rate <= ? AND carbohydrate_rate >= ? AND carbohydrate_rate <= ?'

			params = (ranges[0][0],ranges[0][1],ranges[1][0],ranges[1][1],ranges[2][0],ranges[2][1])
			connection = sqlite3.connect(self.database_path)

			cursor = connection.cursor()
			self.range_count_cache[classification_id][ci] = cursor.execute(q, params).fetchall()

			connection.close()

		return self.range_count_cache[classification_id][ci]

	def get_image_count_by_condition(self, table, condition):
		q = 'SELECT count(*) FROM %s %s;' % (table, condition)

		connection = sqlite3.connect(self.database_path)

		cursor = connection.cursor()
		count = cursor.execute(q).fetchone()[0]

		connection.close()

		return count

	def get_centroids(self, classification_id):
		q = 'SELECT protein, fat, carbohydrate, id FROM centroids WHERE classification_id=?'

		params = (classification_id,)
		connection = sqlite3.connect(self.database_path)

		cursor = connection.cursor()
		res = list(cursor.execute(q, params).fetchall())

		connection.close()

		return res

	def get_image_ids_by_class(self, ci, classification_id, offset, count):
		q = 'WITH Tmp AS (SELECT recipe_id FROM recipe_classes WHERE classification_id=? AND class=?) SELECT images.id FROM images, Tmp WHERE images.recipe_id=Tmp.recipe_id LIMIT ?, ?'

		image_ids = []

		connection = sqlite3.connect(self.database_path)

		cursor = connection.cursor()
		for row in cursor.execute(q, (classification_id, ci, offset, count)):
			image_ids.append(row[0])

		connection.close()

		return image_ids

	def get_image_count(self):
		q = 'SELECT COUNT(*) FROM images'

		connection = sqlite3.connect(self.database_path)

		cursor = connection.cursor()
		count = cursor.execute(q).fetchone()[0]

		connection.close()

		return count

	def get_image_data_by_id(self, image_id):
		q = 'SELECT raw FROM image_data WHERE id=?'

		connection = sqlite3.connect(self.image_database_path)

		cursor = connection.cursor()
		raw = cursor.execute(q, (image_id,)).fetchone()[0]

		connection.close()

		return io.BytesIO(raw)
