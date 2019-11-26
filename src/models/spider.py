from bs4 import BeautifulSoup
import requests
from pprint import pprint

class BookSpider():
	def __init__(self, url):
		self.url = url
		self.headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
		self.parse_dict = {}
		self.tag_list=[
				'a',
				'abbr', 
				'acronym',
				'address',
				'applet',
				'area',
				'article',
				'aside',
				'audio',
				'b',
				'base',
				'basefont',
				'bdi',
				'bdo',
				'big',
				'blockquote',
				'br',
				'button',
				'canvas',
				'caption',
				'center',
				'cite',
				'code',
				'col',
				'colgroup',
				'data',
				'datalist',
				'dd',
				'del',
				'details',
				'dfn',
				'dialog',
				'dir',
				'div',
				'dl',
				'dt',
				'em',
				'embed',
				'fieldset',
				'figcaption',
				'figure',
				'font',
				'footer',
				'form',
				'frame',
				'frameset',
				'h1',
				'h2',
				'h3',
				'h4',
				'h5',
				'h6',
				'head',
				'header',
				'hr',
				'i',
				'iframe',
				'img',
				'input',
				'ins',
				'kbd',
				'label',
				'legend',
				'li',
				'link',
				'main',
				'map',
				'mark',
				'meta',
				'meter',
				'nav',
				'noframes',
				'noscript',
				'object',
				'ol',
				'optgroup',
				'option',
				'output',
				'p',
				'param',
				'picture',
				'pre',
				'progress',
				'q',
				'rp',
				'rt',
				'ruby',
				's',
				'samp',
				'script',
				'section',
				'select',
				'small',
				'source',
				'span',
				'strike',
				'strong',
				'style',
				'sub',
				'summary',
				'sup',
				'svg',
				'table',
				'tbody',
				'td',
				'template',
				'textarea',
				'tfoot',
				'th',
				'thead',
				'time',
				'title',
				'tr',
				'track',
				'tt',
				'u',
				'ul',
				'var',
				'video',
				'wbr']

	def scrape(self):
		request = requests.get(self.url, self.headers)
		f = open("file.html", "wb+")
		f.write(bytes(request.text, request.encoding))
		f.close()
		self.parse(request.text)

	def parse(self, response):
		main_soup = BeautifulSoup(response, "html.parser")
		#extract a tags and their attributes
		for tag in self.tag_list:
			tag_selectors =  main_soup.find_all(tag)
			if tag_selectors != []:
				self.parse_dict[tag] = []
				for selector in tag_selectors:
					info_dict = {}
					info_dict = selector.attrs
					info_dict['text'] = selector.text.strip()
					self.parse_dict[tag].append(info_dict)


	def sort_structure(self, data, sort=True):
		alpha = {}
		for datum in data:
			for key in datum:
				if key[0] not in alpha:
					alpha[key[0]] = {}
				if key not in alpha[key[0]]:
					alpha[key[0]][key] = []
				if datum[key] not in alpha[key[0]][key]:
					alpha[key[0]][key].append(datum[key])
					if sort:
						alpha[key[0]][key] = sorted(alpha[key[0]][key])
		return alpha