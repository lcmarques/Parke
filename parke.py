#!/usr/bin/env python
# Author: Luis Marques 
# Blog: http://www.lcmarques.com

import sys
import os
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
			
			#each i represents a trace statement
			for i in statblock:
				

				#REGEX POWER!

				jo=re.findall('Join order\[.*', i)
				best=re.search('Best join order:.*', i)
				sq=re.search('.*sql_id.*', i)
				sqt=re.search('.*sql=.*', i)
				pattern = re.compile('  atom_hint=.*', re.DOTALL)
				sofar = re.compile('Best so far'
                 '.*?' + re.escape("***********************") ,
                 re.DOTALL)
 			
 				atom = pattern.search(i)
 	
 				if sofar:
 					sofar_search=sofar.search(i)
 					bestsofar= sofar_search.group(0).split("Best so far: ")[1].split('\n')
 					bestsofar.pop(-1) # remove last element of the list corresponding *************

 				if atom:
 					
 					ahint=atom.group(0).split('\n')
 					#.split('atom_hint=')[1]	
				if sq:
					sql_id=sq.group(0).split()[0].split('=')[1]
				if sqt:
					sql_text=sqt.group(0).split('sql=')[1]
				
				if best:
					best_permut=best.group(0).split('Best join order:')[1].strip()


				#remove empty hints strings
				ahint=[x[2:] for x in ahint if x]

				permut=[x for x in jo if x]


				result=i[i.find('Plan Table\n============')+23:i.find('Predicate Information:')]
				array_json.append({'sql_id': sql_id, 'sql_text': sql_text, 
					'permutations': permut, 'best_permutation': best_permut, 'best_so_far': bestsofar, 'hints': ahint, 'xplan': result })

			js=json.dumps(array_json, indent = 2)
			f.write(js)
			f.close()
			return result

		#except:
		#	print "E: Parke can't parse EXPLAIN PLAN! :("	
		


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
					print "SQL Statements available (Ctrl+C exit):"
					for i, a  in enumerate(data):

						print str(i+1) + ") " +data[i]['sql_id']

			
					sqlid_op=raw_input("Please enter your option: ")
					sqlid_op=int(sqlid_op)

					#get both arrays for hints and permutation
					hints= data[sqlid_op-1]["hints"]
					permut=data[sqlid_op-1]["permutations"]
					best_p=data[sqlid_op-1]["best_permutation"]



					print "Sql_id: "+data[sqlid_op-1]["sql_id"]
					print "Sql_text: "+data[sqlid_op-1]["sql_text"]


					
					print "Permutations:"
					for j, a in enumerate(permut):
						print str(j+1)+")"+a
					
					print "Best Join Order is: "+ data[sqlid_op-1]["best_permutation"]
					
					# hints
					if len(hints) > 0:
						print "Hints:"
						for j,a in enumerate(hints):
							print str(j+1)+")"+a

					print "Explain Plan:\n"+data[sqlid_op-1]["xplan"] 

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
	if sys.version_info<(2,6,0):
    		print "E: Parke needs at least Python 2.6! Exiting.."
   	else:
			main()		

