from __future__ import print_function
import csv
import sys
from xlrd import open_workbook
import os, shutil

"""
Script to extract named sheets from a workbook into csv

*** wbfile is passed from command line passed as -w wbfile  
*** Sheets are converted to csv in data/ folder
"""
# Command line Argument Handling
try:
    import argparse
    parser = argparse.ArgumentParser(description='Script for creating csv files from xls file')
    parser.add_argument('-m','--masterfile', help='e.g -m fido_dict.csv', required=True)
    parser.add_argument('-w','--wbfile', help='e.g -w wbfile.csv', required=True)
    parser.add_argument('-d','--date', help='e.g -d 2017-03-09', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None
    
DICTFILE = open(args['masterfile'], 'rt')
wbfile = args['wbfile']
DATEINVOICE = args['date']
ERRORFILE = '/tmp/errfile' + DATEINVOICE + '.csv'
errfile = open(ERRORFILE, 'w')
DATAFOLDER = 'data'
salesid = {}
custid = {}

# delete all files in folder
def delfiles(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def customerqc(name):
    """
     DO quality control on customer name to reduce rejections
    """
    custname = name.strip()
    custname = custname.replace('Jesus Love','Jesus-Love')
    custname = custname.replace('Roland','Rowland')
    custname = custname.replace('Christain','Christian')
    custname = custname.replace('Pishoh Gole','Pishon Gole')
    custname = custname.replace('Stella Amaran','Stella Amara')
    custname = custname.replace('Omorome','Omoreme')    
    custname = custname.replace('Egerekumo','Ederekumo')
    custname = custname.replace('Mathew','Matthew')
    custname = custname.replace('Mercy Ndubuisi','Mercy Ndubusi')        
    custname = custname.replace('Daniel Egiri','Erigi')
    custname = custname.replace('Chima Customer','Chima-Customer')
    custname = custname.replace('Okafor Priscilla','Priscilla Okafor')
    custname = custname.replace('Nigerian Neavy','Nig Navy')
    custname = custname.replace('Nigerian Navy','Nig Navy')
    custname = custname.replace('Doris Ogede','Ogede Doris')
    custname = custname.replace('Emeka Okolo','Okolo Emeka')
    custname = custname.replace('Sunday David','Sunny David')
    custname = custname.replace('Olayode Ujro','Olayode Ujiro')
    custname = custname.replace('Ganiyu Ayo','Ganiyu Motunrayo')
      
    custname = custname.replace('Ayodele Franca','Franca Ayodele')
    custname = custname.replace('Godspower Customer','Godspower-Customer')
    
    custname = custname.replace('New Integrated Service','New Integrated Services')
    return custname                
    
def reformat (file,prodtype):
    
    outfile = open("OUT/out_%s" %(file), 'w')
    reader1 = csv.reader(DICTFILE)
    file1 = 'data/'+file
    for row in reader1:
        sperson = row[2].upper()
        salesid[sperson] = row[3]
        cperson = row[0].upper()
        custid[cperson] = row[1]
        
    reader2 = csv.reader(open(file1, 'rt'))
    CSVHEADER = 'id,payment_term_id/id,account_id/id,user_id/id,user_id/name,partner_id/id,partner_id/display_name,date_invoice,invoice_line_ids/product_id/id,invoice_line_ids/name,invoice_line_ids/account_id/id,invoice_line_ids/quantity,invoice_line_ids/price_unit'
    print (CSVHEADER,file=outfile)
    rcount = 0
    ercount = 0

    for row in reader2:
        try:
            rcount = rcount + 1
            custname = customerqc(row[3])
            custname = custname.upper()
            salesperson = row[1].upper()
            # print(custname,' master ',salesperson)
            sid = ('__export__.res_users_' + salesid[salesperson]).rstrip()
            cid = ('__export__.res_partner_' + custid[custname]).rstrip()
            if 'OBUN' in file:
                printstr = ',__export__.account_payment_term_7,__export__.account_account_7,'+sid +','+salesperson+','+cid+','+custname+','+DATEINVOICE +','+'__export__.product_product_421'+','+prodtype+','+'__export__.account_account_204'+','+row[7]+','+row[8]
            if 'KPANSIA' in file:                
                printstr = ',__export__.account_payment_term_8,__export__.account_account_7,'+sid +','+salesperson+','+cid+','+custname+','+DATEINVOICE +','+'__export__.product_product_421'+','+prodtype+','+'__export__.account_account_204'+','+row[7]+','+row[8]
            print (printstr,file=outfile)
        except KeyError:
            ercount = ercount + 1
            print('Customer,',row[3],',Salesperson,',row[1],',**** ',file,file=errfile)
        
    print ('FILE,LINES,Errors\n%s,%s,%s\n' %(file, rcount,ercount))
    outfile.close()

def main():
    # extract csv from sheets in workbook
    wb = open_workbook(wbfile)
    delfiles(DATAFOLDER)
    for i in range(0, wb.nsheets-1):
        sheet = wb.sheet_by_index(i)
        print ('sheet name is ',sheet.name)
 
        path =  DATAFOLDER + '/%s.cvs'
        with open( path %(sheet.name.replace(" ","")+DATEINVOICE), "w") as file:
            writer = csv.writer(file, delimiter = ",")
            # print (sheet, sheet.name, sheet.ncols, sheet.nrows)
 
            header = [cell.value for cell in sheet.row(0)]
            writer.writerow(header)
 
            for row_idx in range(1, sheet.nrows):
                row = [int(cell.value) if isinstance(cell.value, float) else cell.value
                   for cell in sheet.row(row_idx)]
                writer.writerow(row)
                
    # Actual reformating
    for file in os.listdir('data'):
        if ('KPANSIA' in file) or ('OBUN' in file):
            reformat(file,'Purewater')
        if ('DISPENSER' in file):
            reformat(file,'Dispenser')
            
    print('See data/ for csv files extracted from xls file and OUT/ directory for import-ready files')        
            
if __name__ == '__main__':
    main()
