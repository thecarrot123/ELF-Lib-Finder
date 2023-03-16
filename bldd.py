import argparse
import os
import time
import threading

SCRIPT_NAME = "elfs_parser.sh"
OUTFILE_NAME = "report.txt"
RUNNING = False

class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_path(path):
    print(f"{bcolors.OKGREEN}Path: {bcolors.ENDC}{path}")

def print_error(error):
    print(bcolors.FAIL + "Error:" + bcolors.ENDC + " " + error)
    exit(1)

def parse_data(lines):
    data = {}
    file_name = None
    machine = None
    libraries = None
    for line in lines:
        words = line.split()
        if len(words) <= 1:
            continue
        if words[0] == "File:":
            file_name = words[1]
        elif words[0] == "Machine:":
            machine = " ".join(words[1:])
        elif words[0] == "Libraries:":
            libraries = []
            for word in words[1:]:
                libraries.append(word[1:-1])
            if machine == None or file_name == None or libraries == None:
                print("Some data are missing! exiting.")
                exit(2)
            if machine not in data.keys():
                data[machine] = {}
            for lib in libraries:
                if lib not in data[machine].keys():
                    data[machine][lib] = []
                data[machine][lib].append(file_name)
    return data

def waiting():
    actions = ['-','\\','|','/']
    colors = [bcolors.OKGREEN,bcolors.FAIL,bcolors.OKGREEN,bcolors.FAIL]
    while RUNNING:
        for i in range(0,len(actions)):
            if not RUNNING:
                break;
            print('[' + colors[i] + actions[i] + bcolors.ENDC + '] Working...',end="")
            time.sleep(0.25)
            print("\r",end="")
            time.sleep(0.25)

def write_data():
    file = open(OUTFILE_NAME, "w")
    for machine,libraries in data.items():
        file.write(f'------------------------------ {machine} ------------------------------\n')
        libs = list(libraries.items())
        sorted_libs = sorted(libs, key = lambda item: -len(item[1]))
        for library,files in sorted_libs:
            file.write(f"{library} ({len(files)} execs)\n")
            for file_name in files:
                file.write(f"\t\t-> {file_name}\n")
        file.write("\n")
    file.close()
    
def prase_args():

    def valid_path(path):
        if os.path.exists(path):
            return path
        else:
            raise FileNotFoundError(path)
        
    parser = argparse.ArgumentParser(
                    prog='bldd.py',
                    description="""Backward ldd: shows all elf executable 
                    files that use specified shared library files.""",
                    )
    #epilog='Text at the bottom of help'
    parser.add_argument("-o <file>","--output_file",type=str,default=OUTFILE_NAME,
                        help="Place the output into <file>. Default value is <report.txt>")
    parser.add_argument("-p <path>","--path",type=valid_path,default=os.getcwd(),
                        help="Find all shared library used by executables in <path> directory and subdirectories")
    return parser.parse_args()

if __name__ == "__main__":

    args = prase_args()
    path = args.path
    OUTFILE_NAME = args.output_file

    print_path(path)

    try:
        RUNNING = True
        thread = threading.Thread(target=waiting)
        thread.start()
        lines = os.popen(f"./{SCRIPT_NAME} {path}").read().split('\n')
        RUNNING = False
        thread.join()
        data = parse_data(lines)

    except KeyboardInterrupt:
        print(bcolors.ENDC + "Terminating.")
        RUNNING = False
        thread.join()
        exit(0)
    
    write_data()
    print(f"{bcolors.BOLD}Done! {bcolors.ENDC}Printed output to {OUTFILE_NAME}.")