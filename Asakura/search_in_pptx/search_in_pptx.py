#!/usr/bin/python

import sys
import os
import subprocess
import glob
import numpy as np
import pandas as pd
import time

### extract data from one pptx and save that data. 
	### page is divided by __5960__ , pagenumber is before __3__, ex page 108 is afaf__5960__108__3__adfafd

def mk_word_file(path_pptx,path2access):
	string_summary = path2access
	for path in glob.iglob( path_pptx + "/ppt/slides/*.xml"):
		st = path.rfind("/") +6
		fn = path.rfind(".xml")
		page = path[st:fn]
	#print(page)

		with open(path,"r") as f:
			string = f.read()
		#print(len(string)  ) 

		str_res = ""
		st = string.find("<a:t>") 
		fn = string.find("</a:t>")
		index = 0 
		while st > -1 :
			str_res = str_res + string[(st+5) :fn]  
			string = string[(fn+6):]
			#print(st)
			st = string.find("<a:t>") 
			fn = string.find("</a:t>")
			index = index + 1 
			if(index > 10000):
				break
			#print(str_res)
		if len(str_res) > 0:
			string_summary = string_summary + "__5960__" + page + "__3__"  + str_res
			#print(string_summary)

	#os.system("cd /Users/Toshiaki/Desktop/medicine/USMLE/")
	#os.system("rm -rf search/Chapter2_biochemistry/words.txt")
	with open( path_pptx + "/words.txt","w") as f:
		f.write(string_summary)


def preparation():
	#if len(sys.argv) < 2:
	#    usage()
	path = "./"
	cd_com = ["cd",path]
	subprocess.check_call(cd_com)
	#os.system("cd /Users/Toshiaki/Desktop/medicine/USMLE/")
	os.system("rm -rf search")
	os.system("mkdir search") 



	for path2access in glob.iglob("**/*.pptx",recursive = True):
		file_name = path2access[path2access.rfind("/")+1:path2access.rfind(".pptx")]
		print(path2access)
		print(file_name)
		if not os.path.exists("search/"+ file_name):
			try:
				mkdir_com = ["mkdir","search/"+ file_name]
				subprocess.check_call(mkdir_com)
				unzip_com = ["unzip",path2access]
				subprocess.check_call(unzip_com)
				mv_com = ["mv","_rels", "ppt", "docProps", "[Content_Types].xml", \
				"search/" + file_name]
				subprocess.check_call(mv_com)
				mk_word_file("search/" + file_name,path2access)
			except:
				dummy = 1
		else:
			print("exist")
	exit()




### search word in one pptx.
def search_word():
	if len(sys.argv) < 2:
		usage()

	search_word = sys.argv[1]
	index = 0
	paths = []
	flag = False
	for file in glob.iglob("search/*/words.txt"):
		with open(file,"r") as f:
			string_summary = f.read()
		if string_summary.find(search_word) > -1:
			flag = True
			path2access = string_summary.split("__5960__")[0]
			paths.append( path2access )

			page= []
			for text in string_summary.split("__5960__")[1:]:
				if text.find(search_word) > -1:
					fn = text.find("__3__")
					page.append( int(text[:fn]) ) 
			page.sort()
			print(str(index) + " : " + path2access + " ; "+"page : " + str( page) )
			index = index + 1
	if flag == True:
		print("Enter number which you want to check, ex 0,1,2 ")
		index = input()
		index_list = index.split(",")
		for ind in index_list:
			try:
				open_com = ["open",paths[ int( ind) ]]
				subprocess.check_call(open_com)
				time.sleep(2)
			except:
				print("Error : please type correctly")
				break

	else:
		print("not found")

def usage():
	print("Usage: %s [search_word] --- if search_word is prep, data preparation start." % sys.argv[0])
	exit()


def main():
	if len(sys.argv) < 2:
		usage()
	if sys.argv[1] == "prep":
		preparation()

	if not os.path.exists("search"):
		print("type left at first : python3.6 %s prep  " % sys.argv[0])
		exit()
	search_word()

main() 	    