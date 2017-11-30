
import sqlite3
import io

class SQLiteDataLoader:
	def __init__(self, db_path='data.sqlite', image_db_path='image_data_299.sqlite'):
		self.database_path = db_path
		self.image_database_path = image_db_path
		self.index_cache = None
		self.count_cache = {}

	def get_condition_indeces(self, classification_id):
		if self.index_cache == None:
			q = 'SELECT MAX(class)+1 FROM recipe_classes WHERE classification_id=?'

			connection = sqlite3.connect(self.database_path)

			cursor = connection.cursor()
			params = (classification_id,)

			max_c = cursor.execute(q, params).fetchone()[0]

			connection.close()
			self.index_cache = range(max_c)

		return self.index_cache

	def get_image_count_by_condition_index(self, ci, classification_id, multiplier, max):
		if ci not in self.count_cache and ci is not None:
			q = 'WITH Tmp AS (SELECT recipe_id FROM recipe_classes WHERE classification_id=? AND class=?) SELECT COUNT(*) FROM images, Tmp WHERE images.recipe_id = Tmp.recipe_id'

			connection = sqlite3.connect(self.database_path)

			cursor = connection.cursor()
			params = (classification_id, ci)
			self.count_cache[ci] = cursor.execute(q, params).fetchone()[0]

			print ("Class %d has %d images." % (ci, self.count_cache[ci]))

			connection.close()

		count = self.count_cache[ci]

		return min(int(count * multiplier), max)

	def get_image_ids_by_condition_index(self, ci, classification_id, offset, count):
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
