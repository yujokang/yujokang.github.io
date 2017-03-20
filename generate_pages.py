from os import sep, listdir
from sys import argv

ENCODING = "UTF-8"
HTML_EXTENSION = ".html"
SOURCE_EXTENSION = ".src"

class HTMLElement:
	def __init__(self, tag, attribute_pairs = [], children = []):
		self.tag = tag
		self.children = []
		self.simple = True
		self.parent = None

		self.attributes_str = ""
		for (name, value) in attribute_pairs:
			self.attributes_str += " %s=\"%s\""%(name, value)

		for child in children:
			self.add(child)
		self.update_simple()
	def unsimplify(self):
		if (self.simple):
			self.simple = False
			if (not self.parent is None):
				self.parent.unsimplify()
	def update_simple(self):
		if (len(self.children) > 1):
			self.unsimplify()
	def child_is_tagged(self, child):
		return isinstance(child, HTMLElement)
	def add(self, child):
		self.children.append(child)
		self.update_simple()
		if (self.child_is_tagged(child)):
			child.parent = self
			if (not child.simple):
				self.unsimplify()
	def indented_str(self, indentation = ""):
		if (self.simple):
			children_text = ""
			for child in self.children:
				children_text += str(child)
			return "%s<%s%s>%s</%s>"%(indentation, self.tag, \
						  self.attributes_str, \
						  children_text, self.tag)

		next_indentation = "\t" + indentation
		text = "%s<%s>\n"%(indentation, self.tag)
		for child in self.children:
			if (self.child_is_tagged(child)):
				text += child.indented_str(next_indentation)
			else:
				text += next_indentation + str(child)
			text += "\n"
		text += "%s</%s>"%(indentation, self.tag)

		return text
	def __str__(self):
		return self.indented_str()

class HTMLCommend:
	def __init__(self, comment):
		self.comment = comment
	def __str__(self):
		return "<!-- %s -->"%(self.comment)

class Page:
	def __init__(self, \
		     file_base, page_title, text_header, link_label, body_text):
		self.file_base = file_base
		self.page_title = page_title
		self.text_header = text_header
		self.link_label = link_label
		self.body_text = body_text
	def get_path(self):
		return self.file_base + HTML_EXTENSION
	def generate_navbar_tab(self, container):
		body = None
		if (self == container):
			body = self.link_label
		else:
			link_attribute = ("href", self.get_path())
			body = HTMLElement("a", \
					   attribute_pairs = [link_attribute], \
					   children = [self.link_label])
		return HTMLElement("td", children = [body])
	def generate_navbar(self, all_pages):
		navbar_row = HTMLElement("tr")
		navbar_table = HTMLElement("table", children = [navbar_row])
		for page in all_pages:
			navbar_row.add(page.generate_navbar_tab(self))
		return navbar_table
	def generate(self, all_pages):
		charset_attribute = ("charset", ENCODING)
		charset = HTMLElement("meta",
				      attribute_pairs = [charset_attribute])
		title = HTMLElement("title", children = [self.page_title])
		head = HTMLElement("head", children = [charset, title])
		header = HTMLElement("h1", children = [self.text_header])
		navbar = self.generate_navbar(all_pages)
		body = HTMLElement("body", children = [header, navbar, "<hr>", \
						       self.body_text])
		root = HTMLElement("html", children = [head, body])

		page_file = open(self.get_path(), "w")
		page_file.write(str(root))
		page_file.close()

def parse_page_source(source_path):
	name = source_path.split(sep)[-1]
	file_base = name[: -len(SOURCE_EXTENSION)]
	source_file = open(source_path, "r")
	page_title = source_file.readline().rstrip()
	text_header = source_file.readline().rstrip()
	link_label = source_file.readline().rstrip()
	body_text = source_file.read()
	source_file.close()

	return Page(file_base, page_title, text_header, link_label, body_text)

def generate_pages(members):
	pages = []
	for member in members:
		if (member.endswith(SOURCE_EXTENSION)):
			pages.append(parse_page_source(member))
	for page in pages:
		page.generate(pages)

if (__name__ == "__main__"):
	if (len(argv) <= 1):
		print "Usage: %s [.src files]"%(argv[0])
	generate_pages(argv[1 : ])
