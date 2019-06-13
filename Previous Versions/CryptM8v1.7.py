#CryptM8 v1.7 J.Street 25/04/2019 'Jordanstreet@protonmail.com'

import os, win32api, base64, sys, time, datetime, threading, socket, shutil
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from colorama import init
from colorama import Fore, Style
from steg import steg_img
init()

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

def clrkey_salt():
    if os.path.exists("key.key"):
        os.remove("key.key")
    else:
        print("Cannot find key file (Must be called key.key in working directory)")
    if os.path.exists("salt.salt"):
        os.remove("salt.salt")
        input("Key & Salt files removed, press 'Enter' to generate a new key/salt pair")
        keygenerate()
    else:
        print("Cannot find salt file (Must be called salt.salt in working directory)")

def user_auth():
    user_key_exists = os.path.isfile('data.dat')
    if user_key_exists == True:
        print("This version")

def main():

    global key
    global user_salt
    existskey = os.path.isfile('key.key')
    existssalt = os.path.isfile('salt.salt')
    if existskey & existssalt == True:
        key = open('key.key', 'rb').read()
        user_salt = open('salt.salt', 'rb').read()
        menu()
    else:
        keygenerate()

def keygenerate():
    progressspin = Spinner()
    global key
    global user_salt
    user_password = input("Enter your encryption key (or enter K if you wish to generate one): ")
    if user_password == "K":
        user_password = base64.b64encode(os.urandom(512))
    else:
        user_password = user_password.encode()

    user_salt = input("Enter your encryption salt (or enter G if you wish to generate one): ")
    if user_salt == "G":
        try:
            start = time.time()
            print("Hashing key...")
            progressspin.start()
            user_salt = base64.b64encode(os.urandom(512))
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA3_224(),
                length=32,
                salt=user_salt,
                iterations=1000000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(user_password))
            writekey = open('key.key', 'wb')
            writekey.write(key)
            writekey.close()
            writesalt = open('salt.salt', 'wb')
            writesalt.write(user_salt)
            writesalt.close()
            progressspin.stop()
            end = time.time()
            elapsed_time = start - end
            print("Key generation took " + str(elapsed_time)[1:-13] + " seconds.")
            input("Press 'Enter' to go to main menu.")
            menu()
        except:
            print("Hashing error occured", sys.exc_info()[0])
            print("It is highly recommended you generate both a key and salt via the program for maximum security")
            print("However at the very least it is recommended you generate a salt to avoid hashing errors as above")
            keygenerate()
    else:
        print("Unlocking...")
        key = user_password

    menu()

def encrypt():
    nofiles = 0
    progressspin = Spinner()
    home_drive = os.path.dirname(os.path.realpath(__file__))
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print("Home directory: " + home_drive)
    print("Current mounted drives are: " + str(drives))
    for files in os.listdir(home_drive):
        nofiles = nofiles + 1
        print(os.path.basename(files))
    print("*Note you can enter a full file path other than the home directory for encryption*")
    input_file = input("Enter the full file path (or Q to return to main menu): ")
    if input_file == "Q":
        menu()
    #if input_file == "key.key" or "salt.salt":
     #   print("Cannot encrypt key or salt file, please select another filename.")
     #   input("Press 'Enter' to return to encryption menu...")
     #   encrypt()
    output_file = input_file + ".CM8"

    try:
        with open(input_file, 'rb') as f:
            inputsize = os.path.getsize(input_file)
            inputsizekb = inputsize >> 10
            inputsizemb = inputsize >> 20
            if inputsizemb > 150:
                print("Current filename" + input_file)
                print("Filesize: " + str(inputsizemb) + "MB")
                print("Input file too large, will cause memory errors")
                encrypt()
            else:
                print("Current filename: " + input_file)
                print("Output filename: " + output_file)
                outputsizeactualmb = inputsizemb * 1.285 #Improve the accuracy of this
                print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
                print("Estimated output size = " + str(outputsizeactualmb) + "MB")
                print("|Loading file into memory|")
                progressspin.start()
                startload = time.time()
                data = f.read()
                endload = time.time()
                progressspin.stop()

    except (FileNotFoundError, IOError):
        print("No such file or directory")
        encrypt()
    print("|Starting Encryption|")
    startenc = time.time()
    progressspin.start()
    try:
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        endenc = time.time()
        progressspin.stop()
        print("|Writing file to drive|")
        progressspin.start()
        startwrt = time.time()
    except:
        progressspin.stop()
        print("Error ", sys.exc_info()[0], "occured.")
        print("It is highly recommended you generate both a key and salt via the program for maximum security")
        print("However at the very least it is recommended you generate a salt to avoid hashing errors as above")
        input("Press 'Enter' to return to main menu.")
        menu()
    with open(output_file, 'wb') as f:
        f.write(encrypted)
    endwrt = time.time()
    progressspin.stop()
    print("|File encryption complete|")
    elapsed_time_load = startload - endload
    print("Loading file to memory took " + str(elapsed_time_load)[1:-12] + " seconds.")
    elapsed_time_enc = startenc - endenc
    print("File encryption took " + str(elapsed_time_enc)[1:-12] + " seconds.")
    elapsed_time_wrt = startwrt - endwrt
    print("Saving file to disk took " + str(elapsed_time_wrt)[1:-13] + " seconds.")
    input("Press 'Enter' to return to main menu")
    menu()

def encryptfolder():
    global input_folder
    global del_after_encrypt
    global files_in_folder
    files_in_folder = 0
    home_drive = os.path.dirname(os.path.realpath(__file__))
    print("Current directory is: " + home_drive)
    input_folder = input("Enter the full directory path: ")
    if input_folder == "Q":
        menu()
    if input_folder == home_drive:
        print("Cannot encrypt root folder as this contains crucial key, salt and CryptM8 files.")
        input("Press 'Enter' to return to encryption menu")

    del_after_encrypt = input("Do you want to delete the original files after decryption? (Y/N)")
    try:
        start_op = time.time()
        for files in os.listdir(input_folder):
            files_in_folder = files_in_folder + 1
            currentfile = input_folder + "\\" + os.path.basename(files)
            print(currentfile)
            output_file = currentfile + ".CM8"
            with open(currentfile, 'rb') as f:
                inputsize = os.path.getsize(currentfile)
                inputsizekb = inputsize >> 10
                inputsizemb = inputsize >> 20
                if inputsizemb > 150:
                    print("Current filename" + currentfile)
                    print("Filesize: " + str(inputsizemb) + "MB")
                    print("Input file too large, will cause memory errors")
                    encrypt()
                else:
                    print("Current filename: " + currentfile)
                    print("Output filename: " + output_file)
                    outputsizeactualmb = inputsizemb * 1.285  # Improve the accuracy of this
                    print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
                    print("Estimated output size = " + str(outputsizeactualmb) + "MB")
                    print("Currently encrypting file # " + str(files_in_folder)) #Add out of comparitor
                    print("|Loading file into memory|")
                    data = f.read()
                    print("|Starting Encryption|")
                    try:
                        fernet = Fernet(key)
                        encrypted = fernet.encrypt(data)
                        print("|Writing file to drive|")
                    except:
                        print("Error ", sys.exc_info()[0], "occured.")
                        print("It is highly recommended you generate both a key and salt via the program for maximum security")
                        print("However at the very least it is recommended you generate a salt to avoid hashing errors as above")
                        input("Press 'Enter' to return to main menu.")
                        menu()
                    with open(output_file, 'wb') as f:
                        f.write(encrypted)
                        print("|File encryption complete|")
    except:
        print("Something fucked occured: ", sys.exc_info()[0])
    end_op = time.time()
    elapsed_op_time = start_op - end_op
    if del_after_encrypt == "Y":
        print("Encryption operation took " + str(elapsed_op_time)[1:-12] + " seconds.")
        print("Preparing to delete files...")
        time.sleep(5)
        del_files_original()
    if del_after_encrypt == "N":
        print("Decryption operation took " + str(elapsed_op_time)[1:-12] + " seconds.")
        print("Please be sure to move/remove the original unencrypted files to avoid file errors in future.")
        input("Press 'Enter' to return to main menu.")
        menu()

def del_files_original():
    print("Deleting files " + str(files_in_folder) + "files in folder...")
    try:
        start_op = time.time()
        for files in os.listdir(input_folder):
            currentfile = input_folder + "\\" + os.path.basename(files)
            if currentfile.endswith(".CM8") !=True:
                os.remove(currentfile)
                print("File deleted -" + os.path.basename(files))
        end_op = time.time()

    except (OSError, FileNotFoundError):
        print("Exception " + sys.exc_info()[0] + "occured.")

    elapsed_op_time = start_op - end_op
    print("File deletion took " + str(elapsed_op_time)[1:-12] + " seconds.")
    print("File deletion complete, deleted " + str(files_in_folder) + " files.")
    input("Press 'Enter' to return to main menu.")

def decrypt():
    progressspin = Spinner()
    nofiles = 0
    home_drive = os.path.dirname(os.path.realpath(__file__))
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print("Home directory: " + home_drive)
    print("Current mounted drives are: " + str(drives))
    for files in os.listdir(home_drive):
        nofiles = nofiles + 1
        print(os.path.basename(files))
    print("*Note you can enter a full file path other than the home directory for encryption*")
    input_file = input("Enter the full file path (or Q to return to main menu.): ")
    if input_file == "Q":
        menu()
    if input_file.endswith('.CM8') != True:
        input_file = input_file + ".CM8"

    try:
        with open(input_file, 'rb') as f:
            output_file = "Unencrypted" + input_file[:-4]
            print("Current filename: " + input_file)
            print("Output filename: " + output_file)
            inputsize = os.path.getsize(input_file)
            inputsizekb = inputsize >> 10
            inputsizemb = inputsize >> 20
            outputsizeactualmb = inputsizemb * 0.785 #Improve the accuracy of this
            print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
            print("Estimated output size = " + str(outputsizeactualmb) + "MB")
            print("|Loading file to memory|")
            progressspin.start()
            startload = time.time()
            data = f.read()
            endload = time.time()
            progressspin.stop()
    except (FileNotFoundError, IOError):
        print("|No such file or directory|")
        decrypt()
    try:
        print("|Starting decryption|")
        progressspin.start()
        startdec = time.time()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(data)
        enddec = time.time()
        progressspin.stop()
        print("|Writing file to disk|")
        progressspin.start()
        startwrt = time.time()
        with open(output_file, 'wb') as f:
            f.write(decrypted)
        endwrt = time.time()
        progressspin.stop()
        print("|Decryption Successful|")
        elapsed_time_load = startload - endload
        print("Loading file to memory took " + str(elapsed_time_load)[1:-12] + " seconds.")
        elapsed_time_dec = startdec - enddec
        print("File decryption took " + str(elapsed_time_dec)[1:-12] + " seconds.")
        elapsed_time_wrt = startwrt - endwrt
        print("Saving file to disk took " + str(elapsed_time_wrt)[1:-13] + " seconds.")
        input("Press 'Enter' to return to main menu.")
        menu()
    except:
        progressspin.stop()
        print("Probable invalid key", sys.exc_info()[0], "occurred.")
        input("Press 'Enter' to return to main menu.")
        menu()

def decryptfolder():
    global input_folder
    global del_after_decrypt
    global files_in_folder
    files_in_folder = 0
    home_drive = os.path.dirname(os.path.realpath(__file__))
    print("Current directory is: " + home_drive)
    input_folder = input("Enter the full directory path: ")
    if input_folder == "Q":
        menu()
    del_after_decrypt = input("Do you want to delete the original files after decryption? (Y/N)")
    try:
        start_op = time.time()
        for files in os.listdir(input_folder):
            files_in_folder = files_in_folder + 1
            currentfile = input_folder + "\\" + os.path.basename(files)
            print(currentfile)
            with open(currentfile, 'rb') as f:
                print("Current filename: " + currentfile)
                output_file = currentfile[:-4]
                print("Output filename: " + output_file)
                inputsize = os.path.getsize(currentfile)
                inputsizekb = inputsize >> 10
                inputsizemb = inputsize >> 20
                outputsizeactualmb = inputsizemb * 0.785  # Improve the accuracy of this
                print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
                print("Estimated output size = " + str(outputsizeactualmb) + "MB")
                print("Currently encrypting file # " + str(files_in_folder))  # Add out of comparitor
                print("|Loading file to memory|")
                data = f.read()
                try:
                    print("|Starting decryption|")
                    fernet = Fernet(key)
                    decrypted = fernet.decrypt(data)
                    print("|Writing file to disk|")
                    with open(output_file, 'wb') as f:
                        f.write(decrypted)
                    print("|Decryption Successful|")
                except:
                    print("Probable invalid key", sys.exc_info()[0], "occurred.")
                    input("Press 'Enter' to return to main menu.")
                    menu()

    except (FileNotFoundError, IOError):
            print("|No such file or directory|")
            decrypt()
    end_op = time.time()
    elapsed_op_time = start_op - end_op
    if del_after_decrypt == "Y":
        print("Decryption operation took " + str(elapsed_op_time)[1:-12] + " seconds.")
        print("Preparing to delete files...")
        time.sleep(5)
        del_files_decrypt()
    if del_after_decrypt == "N":
        print("Decryption operation took " + str(elapsed_op_time)[1:-12] + " seconds.")
        print("Please be sure to move/remove the original encrypted files to avoid file errors in future.")
        input("Press 'Enter' to return to main menu.")
        menu()

def del_files_decrypt():
    print("Deleting " + str(files_in_folder) + " files in folder")
    try:
        start_op = time.time()
        for files in os.listdir(input_folder):
            currentfile = input_folder + "\\" + os.path.basename(files)
            if currentfile.endswith(".CM8"):
                os.remove(currentfile)
                print("File deleted -" + os.path.basename(files))
        end_op = time.time()
    except (OSError, FileNotFoundError):
        print("Exception " + sys.exc_info()[0] + "occured.")

    elapsed_op_time = start_op - end_op
    print("File deletion took " + str(elapsed_op_time)[1:-12] + " seconds.")
    print("File deletion complete, deleted " + str(files_in_folder) + " files.")
    input("Press 'Enter' to return to main menu.")

def viewdirectory():
    nofiles = 0
    home_drive = os.path.dirname(os.path.realpath(__file__))
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print("Current CryptM8 home dir: " + home_drive)
    print("Current mounted drives are: " + str(drives))
    current_action = input("What would you like to do? (Browse(B)|Copy(C)|Delete(D)|View(V)|Quit(Q): ")
    if current_action == "D":
        print("Current mounted drives are: " + str(drives))
        print("Current CryptM8 home directory: " + home_drive)
        for files in os.listdir(home_drive):
            nofiles = nofiles + 1
            print(os.path.basename(files))
        print("There is " + str(nofiles) + " files in the home directory. *Note you can enter a file path outside of the home directory to delete*")
        del_file = input("Enter the full file (or Q to return to main menu): ")
        if del_file == "Q":
            menu()
        print("The filepath to delete is: " + del_file)
        confirm = input("Are you sure you want to delete(Y/N): " + del_file)
        if confirm == "Y":
            print("Preparing to delete: " + del_file)
            try:
                os.remove(del_file)
                print("File deleted...")
                input("Press 'Enter' to return to main menu.")
            except(OSError, FileNotFoundError):
                print("File currently in use or does not exist")
                print(sys.exc_info()[0] + "Occured.")
        menu()
    if current_action == "Q":
        menu()
    if current_action == "B":
        drive = input("Enter a drive/directory to view (Or type Q to return to menu): ")
        if drive == "Q":
            menu()
        try:
            for files in os.listdir(drive):
                nofiles = nofiles + 1
                print(os.path.basename(files))
            print("There is: " + str(nofiles) + " files in this directory")
            viewdirectory()
        except FileNotFoundError:
            print("No such file or directory")
    if current_action == "V":
        nofiles = 0
        print("Current mounted drives are: " + str(drives))
        print("Current CryptM8 home directory: " + home_drive)
        for files in os.listdir(home_drive):
            nofiles = nofiles + 1
            print(os.path.basename(files))
        print("There is " + str(nofiles) + " files in the home directory. *Note you can enter a file path outside of the home directory to view*")
        view_file = input("Enter the filepath you wish to view: ")
        try:
            f = open(view_file, "r")
            file_extension = os.path.splitext(view_file)
            try:
                file_content = f.read()
                print(file_content)
                input("Press 'Enter' to return to file manager.")
                viewdirectory()
            except UnicodeDecodeError:
                print("It would appear you loaded an unsupported file type '" + file_extension[1] + "' or a file containing non unicode characters.")
                input("Press 'Enter' to return to file manager.")
                viewdirectory()

        except(FileNotFoundError, IOError):
            print("File currently in use or does not exist")
            print(sys.exc_info()[0] + "Occured.")

    if current_action == "C":
        nofiles = 0
        print("Current mounted drives are: " + str(drives))
        print("Current CryptM8 home directory: " + home_drive)
        for files in os.listdir(home_drive):
            nofiles = nofiles + 1
            print(os.path.basename(files))
        print("There is " + str(nofiles) + " files in the home directory.")
        copy_file = input("Enter the file to copy: ")
        if os.path.exists(copy_file):
            dest_path = input("Enter the directory you wish to copy the file to: ")
            dest_rename = input("If you wish to rename this file enter filename now. If not leave blank.")
            try:
                shutil.copy(copy_file, dest_path)
                print("File " + copy_file + " copied successfully.")
                input("Press 'Enter' to return to file manager.")
                viewdirectory()
            except:
                print("The file has been modified, or is unable to be copied.")
                input("Press 'Enter' to return to file manager.")
                viewdirectory()
        else:
            print("This file does not exist, or cannot be copied.")
            input("Press 'Enter' to return to file manager.")
            viewdirectory()
        input("Press 'Enter' to return to main menu.")
        viewdirectory()
#def del_file():
 #   print("Note file names inside of the root folder do not require a full filename for deletion.")


def send_file():
    print("WARNING EXTREMELY EXPERIMENTAL|DO NOT TRUST")
    print("CAUTION SENDING FILES OVER 150MB")
    print("Please note 'sending party' needs to be 'listening' before receiver can initiate file transfer")
    host = input("Enter the ip/hostname to send to: ")  # Get local machine name
    #port = input("Enter port number: ")  # Reserve a port for your service every new transfer wants a new port or you must wait.
    port = 50000
    s = socket.socket()  # Create a socket object
    s.bind((host, port))  # Bind to the port
    s.listen(5)  # Now wait for client connection.

    print('Server listening....')

    while True:
        conn, addr = s.accept()  # Establish connection with client.
        print('Got connection from: ', addr)
        data = conn.recv(1024)
        print('Server received data: ', repr(data))
        filename = input("Enter the file you wish to send: ")
        f = open(filename, 'rb')
        l = f.read(1024)
        while (l):
            conn.send(l)
            print('Sent ', repr(l))
            l = f.read(1024)
        f.close()

        print('Done sending file' + filename)
        conn.close()
        input("Press 'Enter' to return to main menu...")
        menu()

def receive_file():
    print("WARNING EXTREMELY EXPERIMENTAL|DO NOT TRUST")
    print("CAUTION SENDING FILES OVER 150MB IN SIZE")
    print("Please note received_file will have to be appended with the appropriate file extension prior to receiving.")
    s = socket.socket()  # Create a socket object
    host = input("Enter the ip/hostname to receive from: ")  # Ip address that the TCPServer  is there
    #port = input("Enter port number: ")  # Reserve a port for your service every new transfer wants a new port or you must wait.
    port = 50000
    input("Please confirm that the sending party is 'listening' then press 'Enter' to proceed.")

    try:
        s.connect((host, port))
        s.send(b"Connection to " + host.encode() + b" successful.")
    except:
        print("Other client not ready to send...Please confirm sender is 'listening' before initiating transfer.")
        input("Press 'Enter' to return to main menu.")
        menu()

    with open('received_file', 'wb') as f:
        print('file opened')
        while True:
            print('receiving data...') #Seems to lose data at beginning or end of file?...
            data = s.recv(1024)
            print('data=%s', (data))
            if not data:
                break
            # write data to a file
            f.write(data)

    f.close()
    print('Successfully received file')
    s.close()
    print('connection closed')
    print("Please note 'received_file' will need to be appended with the correct file extension to allow viewing.")
    input("Press 'Enter' to return to main menu.")
    menu()

def secret_menu():
    print("Well done you have discovered the secret menu...I havent really decided what to put here yet...but well done anyway")
    print("Menu|Main Menu (Q)|Credits (C)|")
    sm_choice = input("Enter a choice: ")
    if sm_choice == "Q":
        menu()
    if sm_choice == "C":
        made_by()
    elif sm_choice != "Q" or "C":
        print("You entered an invalid choice retard...try again but this time try not royally fuck it up...")
        input("Press 'Enter' to return to the secret menu....")
        secret_menu()

def encrypt_drive():
    print("WARNING MODULE HEAVILY UNDER-TESTED")
    print("If you supply a folder path it will encrypt the items inside plus all sub directories.")
    print("alternatively if you supply a drive letter CryptM8 will attempt to encrypt everything contained on this drive.")
    print("As such this module is to be used with EXTREME caution, as I cannot be responsible for the damage it may do.")
    print("Furthermore it will delete the originsl files automatically without prompt.")
    ed_disclaimer = input("Enter Y if you acknowledge the consequences of this action or N to return to menu.")
    if ed_disclaimer == "N":
        input("Press 'Enter' to return to main menu.")
        menu()
    if ed_disclaimer == "Y":
        no_files = 0
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        print("Current mounted drives are: " + str(drives))
        dm_drive = input("Enter the drive you wish to encrypt: ")
        if dm_drive == "Q" or "q":
            menu()
        for root, dirs, files in os.walk(dm_drive):
            for name in files:
                no_files = no_files + 1
                print(os.path.join(root, name))
                currentfile = os.path.join(root, name)
                output_file = os.path.join(root, name + ".CM8")
                with open(currentfile, 'rb') as f:
                    inputsize = os.path.getsize(currentfile)
                    inputsizekb = inputsize >> 10
                    inputsizemb = inputsize >> 20
                    if inputsizemb > 150:
                        print("Current filename" + currentfile)
                        print("Filesize: " + str(inputsizemb) + "MB")
                        print("Input file too large, will cause memory errors")
                        encrypt_drive()
                    else:
                        print("Current filename: " + currentfile)
                        print("Output filename: " + output_file)
                        outputsizeactualmb = inputsizemb * 1.285  # Improve the accuracy of this
                        print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
                        print("Estimated output size = " + str(outputsizeactualmb) + "MB")
                        print("Currently encrypting file # " + str(no_files))  # Add out of comparitor
                        print("|Loading file into memory|")
                        data = f.read()
                        print("|Starting Encryption|")
                        try:
                            fernet = Fernet(key)
                            encrypted = fernet.encrypt(data)
                            print("|Writing file to drive|")
                        except:
                            print("Error ", sys.exc_info()[0], "occured.")
                            print("It is highly recommended you generate both a key and salt via the program for maximum security")
                            print("However at the very least it is recommended you generate a salt to avoid hashing errors as above")
                            input("Press 'Enter' to return to main menu.")
                            menu()
                        with open(output_file, 'wb') as f:
                            f.write(encrypted)
                print("Deleting file: " + currentfile)
                os.remove(currentfile)


        print("There is: " + str(no_files) + " files in this drive.")
        input("Press 'Enter' to return to menu.")
        secret_menu()

def decrypt_drive():
    no_files = 0
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print("Current mounted drives are: " + str(drives))
    dm_drive = input("Enter the drive you wish to decrypt (or Q to return to main menu): ")
    if dm_drive == "Q" or "q":
        menu()
    for root, dirs, files in os.walk(dm_drive):
        for name in files:
            no_files = no_files + 1
            print(os.path.join(root, name))
            currentfile = os.path.join(root, name)
            with open(currentfile, 'rb') as f:
                print("Current filename: " + currentfile)
                output_file = currentfile[:-4]
                print("Output filename: " + output_file)
                inputsize = os.path.getsize(currentfile)
                inputsizekb = inputsize >> 10
                inputsizemb = inputsize >> 20
                outputsizeactualmb = inputsizemb * 0.785  # Improve the accuracy of this
                print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
                print("Estimated output size = " + str(outputsizeactualmb) + "MB")
                print("Currently encrypting file # " + str(no_files))  # Add out of comparitor
                print("|Loading file to memory|")
                data = f.read()
                try:
                    print("|Starting decryption|")
                    fernet = Fernet(key)
                    decrypted = fernet.decrypt(data)
                    print("|Writing file to disk|")
                    with open(output_file, 'wb') as f:
                        f.write(decrypted)
                    print("|Decryption Successful|")
                except:
                    print("Probable invalid key", sys.exc_info()[0], "occurred.")
                    input("Press 'Enter' to return to main menu.")
                    menu()
            print("Deleting file: " + currentfile)
            os.remove(currentfile)
    print("There is " + str(no_files) + " in this directory.")
    input("Press 'Enter' to return to menu.")
    secret_menu()

def archiver():
    print("This module will move the entire contents of a directory and compress them into a '.zip' archive.")
    home_drive = os.path.dirname(os.path.realpath(__file__))
    print("Note the output folder will be the CryptM8 folder shown below...")
    print("Current CryptM8 directory is: " + home_drive)
    zip_dir = input("Please enter the full file path you wish to archive (or Q to return to menu): ")
    if zip_dir == "Q" or "q":
        menu()
    if os.path.exists(zip_dir):
        zip_name = input("What do you want to name the archive: ")
        print("Creating archive, file output will be the CryptM8 home directory.")
        shutil.make_archive(zip_name, 'zip', zip_dir)
        print("File successfully archived, output folder is: " + home_drive)
        input("Press 'Enter' to return to main menu.")
        menu()
    else:
        print("Folder/Directory " + str(zip_dir) + " not found.")
        input("Press 'Enter' to return to archiver.")
        archiver()

def backup():
    home_drive = os.path.dirname(os.path.realpath(__file__))
    print("Current key directory is: " + home_drive)
    bk_dest = input("Enter the full path you wish to save the key to: ")
    if os.path.exists(bk_dest):
        try:
            shutil.copy("key.key", bk_dest)
            print("Key sucessfully copied to " + bk_dest)
            input("Press 'Enter' to return to main menu.")
            menu()
        except:
            print("Cannot copy key to " + bk_dest)
            print("Possible permission error or folder is read only.")
            print(sys.exc_info()[0], " error occured.")
    else:
        print("File or folder does not seem to exist. Please double check file path.")
        input("Press 'Enter' to return to key backup menu.")
        backup()

def file_hide():
    accepted_ext = (".png", ".PNG", ".BMP", ".bmp")
    print("This module will attempt to encrypt a given file and then hide it within an image file.")
    print("Please use a '.png' or '.bmp' file for the target file, the file also needs to be the same size or larger,"
          "than the file you are hiding inside.")
    print("**Note if you keep getting exceptions try using a '.png' file as this generally has the best success rate.**")
    input_file = input("Enter the file name or full path of the file to be encrypted and hidden: ")
    if os.path.exists(input_file):
        target_file = input("Enter the file name or full path of the target file: ")
        if target_file.endswith(accepted_ext) !=True:
            print("Please use a '.png' or '.bmp' file, else this can produce errors.")
            input("Press 'Enter' to return to the file hider menu.")
            file_hide()
        if os.path.exists(target_file):
            inputsize = os.path.getsize(target_file)
            inputsizekb = inputsize >> 10
            inputsizemb = inputsize >> 20
            output_file = steg_img.IMG(payload_path=input_file, image_path=target_file)
            print("Preparing to hide " + input_file + " into file " + target_file)
            print("This may take a long time depending on your system and the file size.")
            try:
                output_file.hide()
                outputsize = os.path.getsize(output_file)
                outputsizekb = outputsize >> 10
                outputsizemb = outputsize >> 20
                print("File successfully hidden.")
                print("Size before: " + inputsizemb + "MB or " + inputsizekb + "KB")
                print("Size after: " + outputsizemb + "MB or " + outputsizekb + "KB")
                input("Press 'Enter' to return to main menu.")
                menu()
            except:
                print("Unexpected error ",sys.exc_info()[0], " occurred.")
                print("Please note this module is still under development and is prone to errors.")
                print("Please try and use a '.png' or '.bmp' file and ensure it is suitably sized to hide the file.")
                print("**Also note if you keep seeing these errors try using a '.png' file**")
                input("Press 'Enter' to return to file hider.")
                file_hide()
        else:
            print("The target file does not exist. Please try again.")
            input("Press 'Enter' to return to file hide menu.")
    else:
        print("The file or directory you have chosen does not exist. Please try again.")
        input("Press 'Enter' to return to file hide menu.")
        file_hide()

def un_hide():
    print("This module will attempt to retrieve a file hidden within an image.")
    input_file = input("Enter the file name or full path of the file to retrieve from: ")
    if os.path.exists(input_file):
        output_file = steg_img.IMG(image_path=input_file)
        print("Preparing to retrieve file from: " + input_file)
        print("This may take a long time depending on your system and the file size.")
        try:
            output_file.extract()
        except:
            print("Unexpected error ", sys.exc_info()[0], " occured.")
            print("Please note this module is still under development and is likely to throw errors.")
            print("If you keep encountering these errors try using a '.bmp' or '.png' image file.")
            input("Press 'Enter' to return to main menu.")
            menu()
        print("Successfully retrieved file from: " + input_file)
        input("Press 'Enter' to return to main menu.")
        menu()
    else:
        print("The file or directory you have chosen does not exist. Please try again.")
        input("Press 'Enter' to return to file retrieval menu.")
        file_hide()

def menu():
    now = datetime.datetime.now()
    menu_salt = user_salt
    if len(menu_salt) > 128:
        menu_salt = str(user_salt[0:128]) + "..."
    print(Fore.GREEN)
    print("-----------------------------------------------------------------------------------------------------------")
    print("")
    print("Welcome to CryptM8 v1.7 25/04/19" + Style.RESET_ALL)
    print("Current loaded key: " + Fore.RED + key.decode('utf-8') + Style.RESET_ALL)
    print("Loaded key is: " + Fore.RED + str(len(key)) + Style.RESET_ALL + " characters in length.")
    print("Current loaded salt: " + Fore.RED + str(menu_salt) + Style.RESET_ALL)
    print("Loaded salt is: " + Fore.RED + str(len(user_salt)) + Style.RESET_ALL + " characters in length.")
    print("Current date/time is: " + now.strftime("%H:%M %d-%m-%Y"))
    print(Fore.GREEN)
    print("-----------------------------------------------------------------------------------------------------------")
    print(Style.RESET_ALL)
    print("Archiver(A)|Browse(B)|Hide Files(HD)|Un-Hide Files(UH)|Encrypt File(E)|Decrypt File(D)|Encrypt Drive(ED)|Decrypt Drive (DD)")
    print("Encrypt Folder(EF)|Decrypt Folder(DF)|Generate Key(G)|Delete Current K/S (KS)|Backup Key(BK)|"
          "File Send (FS)|File Receive(FR)|Quit (Q)")
    usrchoice = input("Enter a menu item: ")
    if usrchoice == "A":
        archiver()

    if usrchoice == "B":
        viewdirectory()

    if usrchoice == "HD":
        file_hide()

    if usrchoice == "UH":
        un_hide()

    if usrchoice == "E":
        encrypt()

    if usrchoice == "ED":
        encrypt_drive()

    if usrchoice == "EF":
        encryptfolder()

    if usrchoice == "D":
        decrypt()

    if usrchoice == "DD":
        decrypt_drive()

    if usrchoice == "DF":
        decryptfolder()

    if usrchoice == "G":
        keygenerate()

    if usrchoice == "KS":
        clrkey_salt()

    if usrchoice == "BK":
        backup()

    if usrchoice == "FS":
        send_file()

    if usrchoice == "FR":
        receive_file()

    if usrchoice == "u,u,d,d,l,r,l,r,b,a,s":
        secret_menu()

    if usrchoice == "Q":
        print(Fore.GREEN + "Thanks for using CryptM8")
        try:
            quit()
        except:
            print("See you again soon...")

    elif usrchoice != "A" or "B" or "DF" or "HD" or "UH" or "E" or "D" or "G" or "EF" or "Q" or "KS" or "DF" or "FS" or "FR" or "u,u,d,d,l,r,l,r,b,a,s":
        print("You entered an invalid choice...")
        input("Press 'Enter' to return to main menu.")
        menu()

def made_by():
    import time
    first_line = "CryptM8 v1.7 (25/04/19) developed by Jordan Street"
    second_line = "If you modify/re-use my code please credit/say thanks as it has been a slow process " \
                  "over a month or so to get to this stage\n and would mean the world to me. Thanks"
    third_line = "P.S This is my first proper Python/programming project, and as such I know there is a huge number of newbie errors \n" \
                 "and some program breaking bugs however please be kind. As I will continue working on CryptM8 in my sparetime.\n" \
                 "And again many many thanks for checking out CryptM8. Jordan S."
    for i in range(len(first_line)):
        print(Fore.GREEN + first_line[i], end='', flush=True)
        time.sleep(0.1)
    print('\n')
    for i in range(len(second_line)):
        print(second_line[i], end='', flush=True)
        time.sleep(0.1)
    print('\n')
    for i in range(len(third_line)):
        print(third_line[i], end='', flush=True)
        time.sleep(0.1)
    print(Style.RESET_ALL)
    input("Press 'Enter' to return to the secret menu.")
    secret_menu()

main()