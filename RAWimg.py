import subprocess
import hashlib
import argparse
import os
import sys
import logging

def setup_logging(log_file):
    ''' to track event occured during execution and verify intigrity for forensic usage
    '''
    logging.basicConfig(
        filename=log_file,  # give file path of log file 
        filemode='a',       # appending log to file 
        format='%(asctime)s - %(levelname)s - %(message)s',  
        level=logging.INFO  # excluding debug level message 
    )
    console = logging.StreamHandler() 
    console.setLevel(logging.INFO)          # creating and setting handler
    formatter = logging.Formatter('%(levelname)s - %(message)s')        # format for console log message
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
def parse_arguments():
    ''' defining argument formate for proper input with help and reruired fields
    '''
    parser = argparse.ArgumentParser(description='Create a RAW image of a storage device.')
    parser.add_argument('-s', '--source', required=True, help='Source device (e.g., /dev/sda)')
    parser.add_argument('-o', '--output', required=True, help='Output image file path')
    parser.add_argument('-b', '--block-size', default='4M', help='Block size for dd (default: 4M)')
    parser.add_argument('-t', '--hash-type', choices=['md5', 'sha256'], default='sha256', help='Hash type for verification (default: sha256)')
    parser.add_argument('-l', '--log', default='imaging.log', help='Log file path (default: imaging.log)')
    return parser.parse_args()
def convert_path_to_cygwin(path):
    """Convert Windows path to Cygwin path."""
    # Ensure the path is absolute
    if not os.path.isabs(path):
        raise ValueError("The path must be absolute.")

    # Get the drive letter and convert it to lowercase
    drive, path = os.path.splitdrive(path)
    drive = drive[0].lower()  # Get the drive letter and convert to lowercase

    # Replace backslashes with forward slashes
    path = path.replace('\\', '/')
    
    # If path ends with a slash, remove it to avoid issues
    if path.endswith('/'):
        path = path[:-1]

    # Prepend '/cygdrive/<drive-letter>'
    cygwin_path = f"/cygdrive/{drive}{path}"
    
    logging.info(f"Converted Windows path '{path}' to Cygwin path '{cygwin_path}'")
    return cygwin_path


def check_device(source):
    '''Checking for errors in different cases
    '''
    if not os.path.exists(source):
        logging.error(f"Source device {source} does not exist.")
        sys.exit(1)
    if not os.access(source, os.R_OK):
        logging.error(f"Source device {source} is not readable. Check permissions.")
        sys.exit(1)

def create_image(source, output, block_size, cygwin_path):
    logging.info(f"Starting imaging process: {source} -> {output} with block-size: {block_size}")
    
    try:
        if not os.path.exists(cygwin_path):  # Check if Cygwin is installed
            logging.error(f"Cygwin bash not found at {cygwin_path}. Please install Cygwin and update the path.")
            sys.exit(1)
            
        cygwin_source = convert_path_to_cygwin(source)
        cygwin_output = convert_path_to_cygwin(output)

        # If block size is in "M", convert to bytes
        if block_size.endswith('M'):
            block_size_bytes = int(block_size[:-1]) * 1024 * 1024
        else:
            block_size_bytes = block_size
        
        # Construct the command to be executed in Cygwin
        cmd = [cygwin_path, '-c', 
               f'/usr/bin/dd if="{cygwin_source}" of="{cygwin_output}" bs={block_size_bytes} status=progress conv=sync,noerror']

        logging.info(f"Executing Cygwin dd command: {''.join(cmd)}")
        subprocess.run(cmd, check=True)
        logging.info("Imaging completed successfully.")
            
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during imaging of disc: '{e}'")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
        

def calculate_hash(file_path, hash_type):
    logging.info(f"calculating hash: {hash_type} for file: {file_path}")
    
    # Initialize the correct hash function
    hash_func = hashlib.md5() if hash_type == 'md5' else hashlib.sha256()

    try:
        # Open the file and read it in chunks
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):   # reading 4KB chunks
                hash_func.update(chunk)  # Update hash with the current chunk

        # Get the final hexadecimal hash value
        hash_value = hash_func.hexdigest()  
        logging.info(f"{hash_type.upper()} hash: {hash_value}")
        return hash_value

    except Exception as e:
        logging.error(f"Error calculating hash: {e}")
        sys.exit(1)

        
def save_hash(hash_value, output_image, hash_type):
    hash_file = f"{output_image}.{hash_type}"
    try:
        with open (hash_file, 'w') as f:
            f.write(f"{hash_type.upper()}({os.path.basename(output_image)}) = {hash_value}\n") #extracting filenaem from end of path
        logging.info(f"Hash saved to {hash_file}")
    except Exception as e:
        logging.error(f"Error saving hash: {e}")
        sys.exit(1)

def main():
    args = parse_arguments()
    setup_logging(args.log)
    logging.info("RAW Image Creation Script Started.")
    
    check_device(args.source)
    
    # Note: Integrating a write-blocker typically requires hardware intervention.
    # If using a software write-blocker, integrate its activation here.
    # Example placeholder:
    # activate_write_blocker()

    create_image(args.source, args.output, args.block_size, r"C:\cygwin64\bin\bash.exe")
    
    hash_value = calculate_hash(args.output, args.hash_type)
    
    save_hash(hash_value, args.output, args.hash_type)
    
    logging.info("Process completed successfully.")

if __name__ == "__main__":
    main()