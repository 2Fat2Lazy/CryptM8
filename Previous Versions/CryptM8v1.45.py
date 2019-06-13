#CryptM8 v1.4 J.Street 07/04/2019 'Jordanstreet@protonmail.com'

import os, win32api, base64, sys, time, threading
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from colorama import init
from colorama import Fore, Back, Style
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
    user_password = input("Enter your encryption key (or enter K if you wish to generate one): ") #if file exists load from that or generate for user?
    if user_password == "K":
        user_password = base64.b64encode(os.urandom(128))
    else:
        user_password = user_password.encode()

    user_salt = input("Enter your encryption salt (or enter G if you wish to generate one): ") #Same with salt?
    if user_salt == "G":
        try:
            print("Hashing key...")
            progressspin.start()
            user_salt = base64.b64encode(os.urandom(128))
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
    progressspin = Spinner()
    input_file = input("Enter the full file path: ")
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
                data = f.read()
                progressspin.stop()

    except (FileNotFoundError, IOError):
        print("No such file or directory")
        encrypt()
    print("|Starting Encryption|")
    progressspin.start()
    try:
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        progressspin.stop()
        print("|Writing file to drive|")
        progressspin.start()
    except:
        progressspin.stop()
        print("Error ", sys.exc_info()[0], "occured.")
        print("It is highly recommended you generate both a key and salt via the program for maximum security")
        print("However at the very least it is recommended you generate a salt to avoid hashing errors as above")
        input("Press 'Enter' to return to main menu.")
        menu()
    with open(output_file, 'wb') as f:
        f.write(encrypted)
    progressspin.stop()
    print("|File encryption complete|")
    input("Press 'Enter' to return to main menu")
    menu()

def encryptfolder():
    home_drive = os.path.dirname(os.path.realpath(__file__))
    print("Current directory is: " + home_drive)
    input_folder = input("Enter the full directory path: ")
    if input_folder == "Q":
        menu()
    try:
        for files in os.listdir(input_folder):
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

def decrypt():
    progressspin = Spinner()
    input_file = input("Enter the full file path: ")
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
            data = f.read()
            progressspin.stop()
    except (FileNotFoundError, IOError):
        print("|No such file or directory|")
        decrypt()
    try:
        print("|Starting decryption|")
        progressspin.start()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(data)
        progressspin.stop()
        print("|Writing file to disk|")
        progressspin.start()
        with open(output_file, 'wb') as f:
            f.write(decrypted)
        progressspin.stop()
        print("|Decryption Successful|")
        menu()
    except:
        progressspin.stop()
        print("Probable invalid key", sys.exc_info()[0], "occurred.")
        input("Press 'Enter' to return to main menu.")
        menu()

def decryptfolder():
    home_drive = os.path.dirname(os.path.realpath(__file__))
    print("Current directory is: " + home_drive)
    input_folder = input("Enter the full directory path: ")
    if input_folder == "Q":
        menu()
    try:
        for files in os.listdir(input_folder):
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


def viewdirectory():
    nofiles = 0
    home_drive = os.path.dirname(os.path.realpath(__file__))
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print("Current CryptM8 home dir: " + home_drive)
    print("Current mounted drives are: " + str(drives))
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


def menu():
    print(Fore.GREEN)
    print("-----------------------------------------------------------------------------------------------------------")
    print("")
    print("Welcome to CryptM8 v1.4" + Style.RESET_ALL)
    print("Current loaded key is: " + Fore.RED + str(key) + Style.RESET_ALL)
    print("Current loaded salt is: " + Fore.RED + str(user_salt) + Style.RESET_ALL)
    print(Fore.GREEN)
    print("-----------------------------------------------------------------------------------------------------------")
    print(Style.RESET_ALL)
    print("Browse(B)|Encrypt File(E)|Encrypt Folder(EF)|Decrypt File(D)|Decrypt Folder(DF)|Generate Key(G)")
    print("Delete Current K/S (KS)|Quit (Q)")
    usrchoice = input("Enter a menu item: ")
    if usrchoice == "B":
        viewdirectory()

    if usrchoice == "E":
        encrypt()

    if usrchoice == "EF":
        encryptfolder()

    if usrchoice == "D":
        decrypt()

    if usrchoice == "DF":
        decryptfolder()

    if usrchoice == "G":
        keygenerate()

    if usrchoice == "KS":
        clrkey_salt()

    if usrchoice == "Q":
        print(Fore.GREEN + "Thanks for using CryptM8")
        try:
            quit()
        except:
            print("See you again soon...")

    elif usrchoice != "B" or "E" or "D" or "G" or "EF" or "Q" or "KS" or "DF":
        print("You entered an invalid choice...")
        menu()

main()