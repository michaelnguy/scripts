"""
Python script to parse a global awr report and print sql stats
Author : Rajeev Ramdas
"""

from   html.parser import HTMLParser
import os
import sys
from   pandas    import DataFrame
import pandas    as pd
import xlsxwriter



"""
Class to parse the html in the awr report
Determines if a table, table row, table column has started ended.
Each column is added to a column list
Once the row is complete the entire row is added to a row list
Based on strings it also determines what section of the report is being parsed
"""

class MyHTMLParser(HTMLParser):

        # Class variables to keep track of section in report
        in_h3=False
        in_Ela=False
        in_Cpu=False
        in_Uio=False
        in_Gets=False
        in_Reads=False
        in_UnOptReads=False
        in_Execs=False
        in_Cluster=False

        # Row counter, used to skip first 2 rows in table which are the headers
        # tr_row for each row
        # tr_row for all rows in a section

        tr_ctr=0
        tr_row=[]
        tr_all_rows=[]

        # If we find a h3 begin tag set a flag
        # If we are in a section and see a tr (table row) begin tag, increment the table row counter
        def handle_starttag(self, tag, attrs):
            if tag == 'h3':
               self.in_h3=True

            if (self.in_Ela or self.in_Cpu or self.in_Gets or self.in_Reads or self.in_Execs)  and tag == 'tr':
               self.tr_ctr+=1

        def handle_data(self, data):
            global lst_cpu
            global lst_ela
            global lst_gets
            global lst_reads
            global lst_execs

            # If we are in a h3 section and find the header for each sql ordered by section, set the flag indicating we are in a specific section
            if self.in_h3:
               if data.startswith('SQL ordered by Elapsed Time'):
                    self.in_Ela=True
               elif data.startswith('SQL ordered by CPU Time'):
                    self.in_Cpu=True
               elif data.startswith('SQL ordered by Gets'):
                    self.in_Gets=True
               elif data.startswith('SQL ordered by Reads'):
                    self.in_Reads=True
               elif data.startswith('SQL ordered by Executions'):
                    self.in_Execs=True

            # If we are in one of the Sql sections and we find the line starting with Back to Sql sats it indicates the section is complete
            # transfer the contents of the all_rows list into the section appropriate list
            # Reset all the section indicator flags, and the row and all_rows lists
            if (self.in_Ela or self.in_Cpu or self.in_Gets or self.in_Reads or self.in_Execs) and data.startswith('Back to SQL Statistics'):
               if self.in_Ela:
                   lst_ela=self.tr_all_rows[:]
               elif self.in_Cpu:
                   lst_cpu=self.tr_all_rows[:]
               elif self.in_Gets:
                   lst_gets=self.tr_all_rows[:]
               elif self.in_Reads:
                   lst_reads=self.tr_all_rows[:]
               elif self.in_Execs:
                   lst_execs=self.tr_all_rows[:]

               self.in_Ela=False
               self.in_Cpu=False
               self.in_Gets=False
               self.in_Reads=False
               self.in_Execs=False
               self.tr_ctr=0

               self.tr_row=[]
               self.tr_all_rows=[]

            # If you are in one of the Sql sections, append the column (skip headers)  to the row list
            if (self.in_Ela or self.in_Cpu or self.in_Gets or self.in_Reads or self.in_Execs) and self.tr_ctr > 2:
               self.tr_row.append(data.replace(",",""))

        # If we find a h3 close tag, unset the in_h3 flag
        # If we are in a section and find a table row close tag, append the row to the all_rows list

        def handle_endtag(self, tag):
            if tag == 'h3':
               self.in_h3=False

            if (self.in_Ela or self.in_Cpu or self.in_Gets or self.in_Reads or self.in_Execs) and self.tr_ctr > 2 and tag == 'tr':
                self.tr_all_rows.append(self.tr_row[:24])
                self.tr_row=[]


"""
Beginning of Main Code
Check if a file name has been provided
Read the file and calculate and print
"""

if len(sys.argv) > 1:
   l_fname=sys.argv[1]
   if not os.path.isfile(l_fname):
      print ("File "+l_fname+" Does not Exist")
      sys.exit()
else:
   print ("Syntax : parseawr.py filename")
   sys.exit()

pd.set_option('display.max_rows',5000)
pd.set_option('display.width',1000)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
l_outfile=l_fname.replace(".html",".xlsx")

# Define lists to hold each Sql Ordered by table
lst_cpu=[]
lst_ela=[]
lst_gets=[]
lst_reads=[]
lst_execs=[]

p = MyHTMLParser()

myfile=open(l_fname,"r")
line=myfile.readline()
while line:
          p.feed(line.rstrip('\n').replace("&#160;",'NaN').replace("&nbsp;",'NaN'))
          line=myfile.readline()
myfile.close()

# Convert lists to dataframes
# Set column names according to order in table header for that section
t_ela_df=DataFrame(lst_ela,columns=['sqid','tela','tcpu','tiow','tgets','treads','trows','tclust','texecs' \
                                    ,'eela','ecpu','eiow','egets','ereads','erows','eclust' \
                                    ,'pctdbt','pctdbcpu','pctiow','pctgets','pctreads','pctclust','pctexecs','sqltxt'])
t_cpu_df=DataFrame(lst_cpu,columns=['sqid','tcpu','tela','tiow','tgets','treads','trows','tclust','texecs' \
                                    ,'ecpu','eela','eiow','egets','ereads','erows','eclust' \
                                    ,'pctdbcpu','pctdbt','pctiow','pctgets','pctreads','pctclust','pctexecs','sqltxt'])
t_gets_df=DataFrame(lst_gets,columns=['sqid','tgets','treads','tela','tcpu','tiow','trows','tclust','texecs' \
                                    ,'egets','ereads','eela','ecpu','eiow','erows','eclust' \
                                    ,'pctgets','pctreads','pctdbt','pctdbcpu','pctiow','pctclust','pctexecs','sqltxt'])
t_reads_df=DataFrame(lst_reads,columns=['sqid','treads','tgets','tela','tcpu','tiow','trows','tclust','texecs' \
                                    ,'ereads','egets','eela','ecpu','eiow','erows','eclust' \
                                    ,'pctreads','pctgets','pctdbt','pctdbcpu','pctiow','pctclust','pctexecs','sqltxt'])
t_execs_df=DataFrame(lst_execs,columns=['sqid','texecs','tela','tcpu','tiow','tgets','treads','trows','tclust' \
                                    ,'eela','ecpu','eiow','egets','ereads','erows','eclust' \
                                    ,'pctexecs','pctdbt','pctdbcpu','pctiow','pctgets','pctreads','pctclust','sqltxt'])

# Concatonate dataframes, drop dups
df_all=pd.concat([t_ela_df,t_cpu_df,t_gets_df,t_reads_df,t_execs_df])
df_all_u=df_all.drop_duplicates(['sqid'],keep='first')
df_all_u=df_all_u.apply(pd.to_numeric,errors='ignore')


# Sort data and write to output file
writer = pd.ExcelWriter(l_outfile)
df_all_u[['sqid','texecs','tela','tcpu','tiow','tgets','treads','trows','tclust' \
          ,'eela','ecpu','eiow','egets','ereads','erows','eclust' \
          ,'pctexecs','pctdbt','pctdbcpu','pctiow','pctgets','pctreads','pctclust','sqltxt' \
         ]].sort_values(by='tela',ascending=False).to_excel(writer,'Sheet1')
writer.save()
writer.close()

