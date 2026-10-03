#jai siya ram
#we are just keeping address of the location of -> database(ScholarNotes) , schema path (BrainDump), 
#and also like if SCHOLAR_DB ALREDY EXIST VS IF NOT EXIST THEN WE ARE IMPORTING THE REAL OR TRUE PATH IF THAT ENVIORNMENT VARIABLE IS NOT PRESENT 
import os
#like this gives the path to where teh notes are stored 
DATA_DIR = os.path.expanduser("~/ScholarNotes")
#This is the path to the database where all the information is stored regarding all the notes 
DB_PATH = os.environ.get("SCHOLAR_DB",os.path.join(DATA_DIR,"scholar.db"))
#Path to THE schema from the path of this files folder and connecting to schema.sql
SCHEMA_PATH = os.path.join(os.path.dirname(__file__),"schema.sql")
