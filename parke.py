#!/usr/bin/env python
# Author: Luis Marques 
# Blog: http://www.lcmarques.com

import sys
import os
from format_columns import *
import getopt
import json
import re
from pprint import pprint


class parseEP:

	def parseEPBlocks(self, filename, outputfile):
		#try:
			pf = parseHints()
			statblock = pf.parseFile(filename)
			f = open(outputfile, "w")
		
			array_json=[]
			ahint=""
			
			for i in statblock:

				jo=re.search('Join order.*', i)
				sq=re.search('.*sql_id.*', i)
				sqt=re.search('.*sql=.*', i)
				pattern = re.compile('  atom_hint=.*', re.DOTALL)
 				atom = pattern.search(i)

 				if atom:
 					ahint=atom.group(0).split('\n')
 					#.split('atom_hint=')[1]	
				if jo: 
					permut=jo.group(0)
				if sq:
					sql_id=sq.group(0).split()[0].split('=')[1]
				if sqt:
					sql_text=sqt.group(0).split('=')[1]
				#if ht:
					
				#	hintsl=ht.group(0)
				#	print hintsl
				#remove empty hints strings
				ahint=[x[2:] for x in ahint if x]

				result=i[i.find('Plan Table\n============')+23:i.find('Predicate Information:')]
				array_json.append({'sql_id': sql_id, 'sql_text': sql_text, 'permutations': permut, 'hints': ahint, 'xplan': result })

			js=json.dumps(array_json, sort_keys=True, indent = 4)
			f.write(js)

		#except:
		#	print "E: Parke can't parse EXPLAIN PLAN! :("	
			f.close()
			return result

	def readEPjson(self, outputfile):
		try:
			json_data=open(outputfile)
			data = json.load(json_data)

			json_data.close()

			return data

		except:
			print "E: Can't parse JSON file " + outputfile

	def showEPresults(self, outputfile):

		try: 
			data = 	self.readEPjson(outputfile)

			while(1):
				try:
					print "SQL Statements available:"
					for i, a  in enumerate(data):

						print str(i+1) + ") " +data[i]['sql_id']

			
					sqlid_op=raw_input("Please enter your option: ")
					sqlid_op=int(sqlid_op)
					hints= data[sqlid_op-1]["hints"]



					print "SQL_ID: "+data[sqlid_op-1]["sql_id"]
					print "SQL_TEXT: "+data[sqlid_op-1]["sql_text"]

					print "PERMUTATIONS:\n"+data[sqlid_op-1]["permutations"] 
					
					# hints
					if len(hints) > 0:
						print "HINTS:"
						for j,a in enumerate(hints):
							print str(j+1)+")"+a

					print "EXPLAIN PLAN:\n"+data[sqlid_op-1]["xplan"] 

				except (IndexError, ValueError):
					print "E: Not a valid option" 
				except KeyboardInterrupt:
					print "\nW: ^C detected! Exiting"
					sys.exit(0)
		except KeyboardInterrupt:
			print "\nW: ^C detected! Exiting"
			sys.exit(0)
		#except:
		#	print "E: Can't parse JSON file " + outputfile



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


def main():
	version="0.2"
	try:
		pf = parseHints()
		pe = parseEP()
		#pp = parseParametersDef()

		opts, args = getopt.getopt(sys.argv[1:], "he", ["help", "explain"])

	except getopt.error, msg:
		print msg
		print "Try --help for more information"
		sys.exit(2)

	#process all available options
	if len(opts) == 0:
		print "Try --help for more information"
	
	else:
		try:
			for o in opts:

				if o[0] in ("-h", "--help"):
					print """Parke [Oracle 10053 trace files parser] 
Usage: parke [OPTION] TRACEFILE OUTPUTFILE
Options are:	
  -e, --explain	explain plan and permutations for all statements"""
			

				if o[0] in ("-e", "--explain"):
					print "Parsing " + args[0] +" => " + args[1]
					pe.parseEPBlocks(args[0], args[1])
					print "All Done! File " + args[1] + " created!"
					pe.showEPresults(args[1])

		except IndexError:
			print "Try --help for more information"


	

			
if __name__ == "__main__":
	main()		

