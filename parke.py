#!/usr/bin/env python
# Author: Luis Marques 
# Blog: http://www.lcmarques.com

import sys
import os
from format_columns import *
import getopt


class attr10053:
	def __init__(self, sql_line, hint_line, err_l, used_l, level_l, txt_l):
		self.sql_line=sql_line
		self.hint_line=hint_line
		self.err_l=err_l
		self.used_l=used_l
		self.level_l = level_l
		self.txt_l = txt_l


class parseParametersDef:

	def parseDParam(self, filename):
		try:
			pf = parseHints()
			statblock = pf.parseFile(filename)
			result="";		
			for i in statblock:
				
				result=i[i.find('PARAMETERS WITH DEFAULT VALUES')+1:i.find('Bug Fix Control Environment')]
				print result		
			return result

		except:
			print "E: Parke can't parse DATABASE DEFAULT PARAMETERS! :("


class parseEP:

	def parseEPBlocks(self, filename):
		#try:
			pf = parseHints()
			statblock = pf.parseFile(filename)
			sql_line='N/A'
			result="";
			permut="";

			#implement permutations output

			for i in statblock:
				permut=i[i.find('Join order['):i.find('(newjo-stop')]
				result_sql=i[i.find('sql='):i.find('----- Explain Plan Dump -----')].split('sql=')[1]
				result=i[i.find('Plan Table\n============')+23:i.find('Predicate Information:')]
				print 'SQL: ' + result_sql
				print permut		
				print result

		#except:
		#	print "E: Parke can't parse EXPLAIN PLAN! :("	

			return result


class parseHints:

	#Check if valid is a 10053 trace. First line must start for "Trace File"
	def isValidTraceFile(self, filename):
		try:
			f=open(filename, 'r')
			lines=f.readlines()		
			for l in lines:
				if l.find('Trace file') >=0:
					return lines
					break
				else:
					return None

		except IOError:
			print "E: Parke can't open file: "+filename



	#each entry on list contains an START and END SQLDUMP
	def parseFile(self, filename):

		text="";		
		statblock=[]
		found=0;

		#verify if it's a valid file here
		lines=self.isValidTraceFile(filename)

		if lines == None:
			print "E: Invalid File Format for an 10053 Oracle Trace File"
			sys.exit(2)
		else:		
			for l in lines:						
				if l.find('QUERY BLOCK SIGNATURE') >= 0:
					found=1 #this thing needs improvement!!!
					text=""	
				if l.find('END SQL Statement Dump') >=0:
					found=2
				if found == 1:
					text = text + l
				if found == 2 and text != '':				
					statblock.append(text)
					text=""
				
		return statblock


	def parseHintBlocks(self, filename):
		statblock = self.parseFile(filename)

		sql_line='N/A'
		hint_line=[]
		iblocks=[]
		hl=[]

		err_l='N/A'
		used_l='N/A'
		level_l='N/A'
		txt_l='N/A'
		hints=0

		for i in statblock:
			iblocks=i.split('\n') #transform every /n in list
			for j in iblocks:

				if j.find('sql=') >= 0:
					sql_line=j.split('sql=')[1]												
				if j.find('atom_hint=') >=0:
					hints=1	
					hint_line=j.split('atom_hint=')[1]									
					# parse each category on hint line
					err_l=hint_line.split('err=')[1][0]
					used_l=hint_line.split('used=')[1][0]
					level_l=hint_line.split('lvl=')[1][0]
					txt_l=hint_line.split('txt=')[1].strip()[:-1]						
			
					x=attr10053(sql_line, hint_line, err_l, used_l, level_l, txt_l)
					hl.append(x)
					
		
			if hints==0:
				x=attr10053(sql_line, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A')
				hl.append(x)
					
		return hl

	def parseHintUsage(self, filename):
		hlf = []
		#default value for variables
		labels = ('Hint', 'Used', 'Error', 'Level',  'SQL FULL TEXT')
		hlf = self.parseHintBlocks(filename)				
		data="";
		for i in hlf:
			sql=i.sql_line	
			data =  data + '\n' + i.txt_l +',' + i.used_l + ','+i.err_l+','+i.level_l+','+sql
			rows = [row.strip().split(',')  for row in data.splitlines()]
    		print indent([labels]+rows, hasHeader=True)


def main():
	version="0.1"
	try:
		pf = parseHints()
		pe = parseEP()
		pp = parseParametersDef()

		opts, args = getopt.getopt(sys.argv[1:], "htep", ["help", "hints", "explain", "dparameter"])

	except getopt.error, msg:
		print msg
		print "Try --help for more information"
		sys.exit(2)
	#process all available options
	if len(opts) == 0:
		print "Nothing to do. Please use --help"
	if len(args) < 1:
		print "Nothing to do. Please use --help"

	else:
		for o in opts:
			if o[0] in ("-h", "--help"):
				print """Parke by Luis Marques [Oracle 10053 trace files parser] v0.1
Usage: parke [OPTION] TRACEFILE
Options are:	
  -t, --hints 	hints information regarding all statements
  -e, --explain	explain plan for all statements"""
				sys.exit(0)


			if o[0] in ("-t", "--hints"):
				print "Report Hints for [" + args[0]+"] ..."
				pf.parseHintUsage(args[0])
				sys.exit(0)


			if o[0] in ("-e", "--explain"):
				print "Report Explain for [" + args[0] +"] ..."
				pe.parseEPBlocks(args[0])
				sys.exit(0)


			if o[0] in ("-p", "--dparameter"):
				print "Report Default Parameters for [" + args[0]+"] ..."
				print "Not Yet Implemented. Sorry"				
#				pp.parseDParam(args[0])
				sys.exit(0)

		
	

			
if __name__ == "__main__":
	main()		

