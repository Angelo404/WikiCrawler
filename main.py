
import sqlite3
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

class wikiCrawller:

	WIKI_PREFIX = "https://en.wikipedia.org"

	def __init__(self, starting_point = "/wiki/Wiki"):
		"""
		"""
		self.conn = self.establishConnection();
		create_table_query = '''
		CREATE TABLE IF NOT EXISTS wikipages (
		 id INTEGER PRIMARY KEY,
		 title text NOT NULL,
		 url text NOT NULL,
		 numOfConnections integer NOT NULL,
		 numOfUniqueWords integer NOT NULL,
		 numOfWords integer NOT NULL,
		 words text NOT NULL,
		 parent text NOT NULL
		);'''
		try:
			self.c = self.conn.cursor()
			self.c.execute(create_table_query)
		except Error as e:
			print(e)

		self.run(starting_point)

	def run(self, starting_point):
		"""
		"""
		current_url = self.WIKI_PREFIX + starting_point
		visited = [starting_point]
		not_visited = []
		parent_url = ""
		counter = 0

		clear_links = lambda x: [_.attrs['href'] for _ in x if (len(_.contents) == 1) and ("class" not in _.attrs) and (
					None is re.search('\[[0-9]+|\]|\^', _.text) and (
						None is re.search('upload\.|[A-Z][_\sa-z]+:|#[a-zA-Z]|action=edit', _.attrs['href'])))]
		difference = lambda x, y: [_ for _ in x if _ not in y]
		compiled_regex = re.compile(r'\.\[[a-zA-Z0-9\]\[,-]+\]|\.|\,|\"|\'|\s|\\n|-|\(|\)|;|\[|\]|:|\^|\*|\&|\!|[^\x00-\x7F]', re.IGNORECASE)

		while 1:
			counter += 1
			num_of_words = 0
			num_of_unique_words = 0
			words = []
			#--
			print(current_url)
			html = urlopen(current_url)
			soup = BeautifulSoup(html.read(), features="html5lib")
			main = soup.find("div", {"id": "mw-content-text", "lang": "en"})
			all_links = main.find_all("a")
			title = soup.find("h1").get_text()
			# --
			cleared_links = clear_links(all_links)
			not_visited.extend(difference(cleared_links, visited))

			paragraphs = main.find_all("p")
			for p in paragraphs:
				for word in p.get_text().split(' '):
					tmp_word = compiled_regex.sub('', word).lower()
					if len(tmp_word) < 2:
						continue
					if tmp_word not in words:
						words.append(tmp_word)
						num_of_unique_words += 1
					num_of_words += 1

			# put parent into the database
			self.c.execute(("INSERT INTO wikipages (title, url, numOfConnections, numOfUniqueWords, numOfWords, words, parent) VALUES ('%s', '%s', %s, %s, %s, '%s', '%s')" % (title, current_url, len(cleared_links), num_of_unique_words, num_of_words, ','.join(words), parent_url)))
			if title.lower() == 'Bo Leuf'.lower():
				break

			parent_url = current_url
			to_visit = not_visited.pop(0)
			visited.append(to_visit)
			current_url = self.WIKI_PREFIX + to_visit
			if counter == 100:
				counter = 0
				print("committing...")
				self.conn.commit()
		self.conn.commit()
		o = 0;
			

	def establishConnection(self):
		"""
		"""
		try:
			conn = sqlite3.connect('wiki_database.db')
			return conn
		except Error as e:
			print(e)


	def isInDatabase(self):
		"""
		"""
		find_query = ""


	def importToDatabase(self):
		"""
		"""
		improt_query = ""
	

if __name__ == '__main__':
	wikiCrawller()