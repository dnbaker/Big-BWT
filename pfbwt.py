#!/usr/bin/env python3

import sys, time, argparse, subprocess, os.path

Description = """
Tool to build the BWT for higly repetive files using the approach
described in 
   "Prefix-Free Parsing for Building Big BWTs"
   
The input file cannot contain the characters 0, 1 or 2 which are
used internally by the algorithm. The character 0 is used as the EOF
in the output BWT. The dictionary and the parse should not be larger than 2GB. 

Input files larger than 2GB are ok, but computing the BWT in the traditional way
takes 9n bytes; if this is a problem just don't use the option -c
"""

parse_exe = "./newscan.x"
parsebwt_exe = "./bwtparse"
parsebwt_exe64 = "./bwtparse64"
pfbwt_exe = "./pfbwt.x"
bwt_exe = "./simplebwt"
bwt_exe64 = "./simplebwt64"


def main():
  parser = argparse.ArgumentParser(description=Description, formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument('input', help='input file name', type=str)
  parser.add_argument('-w', '--wsize', help='sliding window size (def. 10)', default=10, type=int)
  parser.add_argument('-p', '--mod', help='hash modulus (def. 100)', default=100, type=int)
  parser.add_argument('-k',  help='keep temporary files',action='store_true')
  parser.add_argument('-c',  help='check BWT',action='store_true')
  #parser.add_argument('-v',  help='verbose',action='store_true')
  args = parser.parse_args()
  logfile_name = args.input + ".log"
  print("Sending logging messages to file:", logfile_name)
  with open(logfile_name,"w") as logfile:  
    
    
    start0 = start = time.time()
    command = "{exe} {wsize} {modulus} {file}".format(exe=parse_exe, 
              wsize=args.wsize, modulus = args.mod, file=args.input)
    print("==== Parsing. Command:", command)
    if(execute_command(command,logfile,logfile_name)!=True):
      return
    print("Elapsed time: {0:.4f}".format(time.time()-start))      

    start = time.time()  
    if(os.path.getsize(args.input+".parse") >=  4*(2**31-4) ):
      command = "{exe} {file}".format(exe=parsebwt_exe64, file=args.input)
    else:
      command = "{exe} {file}".format(exe=parsebwt_exe, file=args.input)
    print("==== Computing BWT of parsing. Command:", command)
    if(execute_command(command,logfile,logfile_name)!=True):
      return
    print("Elapsed time: {0:.4f}".format(time.time()-start));      
        
    start = time.time()        
    command = "{exe} {wsize} {file}".format(exe=pfbwt_exe, wsize=args.wsize, file=args.input)
    print("==== Computing final BWT. Command:", command)
    if(execute_command(command,logfile,logfile_name)!=True):
      return
    print("Elapsed time: {0:.4f}".format(time.time()-start))      
    print("Total construction time: {0:.4f}".format(time.time()-start0))      

    # ---- delete intermediate files
    if(args.k==False):
      command = "rm {file}.parse {file}.parse_old {file}.last {file}.bwlast {file}.dict {file}.ilist {file}.occ".format(file=args.input);
      print("==== Deleting temporary files.") # no need to show the command
      if(execute_command(command,logfile,logfile_name)!=True):
        return   

    # --- start checking ---
    if(args.c):
      start = time.time()
      if(os.path.getsize(args.input)>= 2**31):
        command = "{exe} {file}".format(exe=bwt_exe64, file=args.input)
      else:
        command = "{exe} {file}".format(exe=bwt_exe, file=args.input)
      print("==== Computing BWT using sacak. Command:", command)       
      if(execute_command(command,logfile,logfile_name)!=True):
        return   
      print("Elapsed time: {0:.4f}".format(time.time()-start));      
      command = "cmp {file}.bwt {file}.Bwt".format(file=args.input); 
      print("==== Comparing BWTs. Command:", command);
      if(execute_command(command,logfile,logfile_name)):
        print("BWTs match");
      else:
        print("BWTs differ");
    # --- end checking ---

  print("==== Done")


# execute command: return True is everything OK, False otherwise
def execute_command(command,logfile,logfile_name):
  try:
    subprocess.check_call(command.split(),stdout=logfile,stderr=logfile)
  except subprocess.CalledProcessError:
    print("Error executing command line:")
    print("\t"+ command)
    print("Check log file: " + logfile_name)
    return False
  return True



if __name__ == '__main__':
    main()
