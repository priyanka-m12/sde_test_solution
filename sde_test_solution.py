"""
Simple script which reads input json file and performs spread calculations and the output get stored in output json file
"""

#import packages
import sys, getopt
import json
import pandas as pd
import datetime

#Main function implementation
def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print("Usage:  sde-test-solution.py -i inputfile -o outputfile")
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('sde-test-solution.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print('Input file is :', inputfile)
   print('Output file is :', outputfile)
   #Calling spread logic function
   spread_cal(inputfile,outputfile)

#spread logic implementation
def spread_cal(srcfile,destfile):
#Read JSON file
   print('Spread logic has started', datetime.datetime.now())
   with open(srcfile) as json_file:
      input_json = json.load(json_file)
      parsed_data=input_json['data']
      json_to_df=pd.DataFrame(parsed_data)
   #Create Seperate dataframes for Corp and Govt data  
      df_corp=json_to_df.query('id.str.contains("c")')
      df_govt=json_to_df.query('id.str.contains("g")')
   #Filter Not null values for Yield column
      df_corp_non_null=df_corp[df_corp["yield"].notnull()]
      df_govt_non_null=df_govt[df_govt["yield"].notnull()]
   #Generate new Ids for Joining Corp and Govt dataframes
      df_corp_non_null['new_id'] = df_corp_non_null.id.str.slice(1,)
      df_govt_non_null['new_id'] = df_govt_non_null.id.str.slice(1,)
   #Convert string to integer in Yield column
      df_corp_non_null['new_corp_yield'] = df_corp_non_null['yield'].replace("%","",regex=True).astype(float)
      df_govt_non_null['new_govt_yield'] = df_govt_non_null['yield'].replace("%","",regex=True).astype(float)
   #Join both dataframes on new_id column
      df_join = pd.merge(df_corp_non_null,  df_govt_non_null, on='new_id', how='inner')
   #Substracting Yields from Corp and Govt dataframes
      df_join['spread_to_benchmark_temp']= ((df_join['new_corp_yield'] - df_join['new_govt_yield'])*100).astype(int)
      df_join['spread_to_benchmark']= df_join['spread_to_benchmark_temp'].astype(str) +  ' bps'
      df_final=df_join.rename(columns={'id_x':'corporate_bond_id','id_y':'government_bond_id'})
      df_final[['corporate_bond_id','government_bond_id','spread_to_benchmark']].to_json(destfile,orient='records',lines=True)
   print('Spread logic has finished', datetime.datetime.now())
   
   
if __name__ == "__main__":
   main(sys.argv[1:])