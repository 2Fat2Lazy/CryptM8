#CryptM8 v1.2 J.Street 05/04/2019 'Jordanstreet@protonmail.com'

import os, win32api, base64, sys
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#key = Fernet.generate_key()
#writekey = open('key.key', 'wb')
#writekey.write(key)
#writekey.close()
#print(key)

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
    global key
    global user_salt
    user_password = input("Enter your encryption key (or enter K if you wish to generate one): ") #if file exists load from that or generate for user?
    if user_password == "K":
        user_password = base64.b64encode(os.urandom(128))
    else:
        user_password = user_password.encode()

    user_salt = input("Enter your encryption salt (or enter G if you wish to generate one): ") #Same with salt?
    if user_salt == "G":
        print("Hashing key...")
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
    else:
        print("Unlocking...")
        key = user_password

    menu()

def encrypt():

    input_file = input("Enter the full file path: ")
    output_file = input_file + ".CM8"

    try:
        with open(input_file, 'rb') as f:
            inputsize = os.path.getsize(input_file)
            inputsizekb = inputsize >> 10
            inputsizemb = inputsize >> 20
            outputsizeactualmb = inputsizemb * 1.285 #Improve the accuracy of this
            print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
            print("Estimated output size = " + str(outputsizeactualmb) + "MB")
            print("|Loading file into memory|")
            data = f.read()
    except (FileNotFoundError, IOError):
        print("No such file or directory")
        encrypt()
    print("|Starting Encryption|")
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    print("|Writing file to drive|")
    with open(output_file, 'wb') as f:
        f.write(encrypted)
    print("|File encryption complete|")
    menu()

def decrypt():

    input_file = input("Enter the full file path: ")
    output_file = "Unencrypted" + input_file[:-4]

    try:
        with open(input_file, 'rb') as f:
            inputsize = os.path.getsize(input_file)
            inputsizekb = inputsize >> 10
            inputsizemb = inputsize >> 20
            outputsizeactualmb = inputsizemb * 0.785 #Improve the accuracy of this
            print("Input file size = " + str(inputsizemb) + "MB" " or " + str(inputsizekb) + "KB")
            print("Estimated output size = " + str(outputsizeactualmb) + "MB")
            data = f.read()
    except (FileNotFoundError, IOError):
        print("|No such file or directory|")
        decrypt()
    try:
        print("|Starting decryption|")
        fernet = Fernet(key)
        decrypted = fernet.decrypt(data)
        print("|Writing file to disk|")
        with open(output_file, 'wb') as f:
            f.write(decrypted)
        print("|Decryption Successful|")
        menu()
    except:
        print("Probable invalid key or file too large", sys.exc_info()[0], "Occurred")
        menu()
def viewdirectory():
    nofiles = 0
    home_drive = os.path.dirname(os.path.realpath(__file__))
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print("Current file path: " + home_drive)
    print("Current mounted drives are: " + str(drives))
    drive = input("Enter a drive/directory to view: ")
    for files in os.listdir(drive):
        nofiles = nofiles + 1
        #print(drive + files)
        print(os.path.basename(files))

    print("There is: " + str(nofiles) + " files in this directory")
    menu()

def menu():
    print("-------------------------------------------------------------------------")
    print("Welcome to CryptM8 v1.2")
    print("Current loaded key is: " + str(key))
    print("Current loaded salt is: " + str(user_salt))
    print("-------------------------------------------------------------------------")
    usrchoice = input("Enter a menu item|Browse(B)|Encrypt(E)|Decrypt(D)|Generate Key(G)|: ")
    if usrchoice == "B":
        viewdirectory()

    if usrchoice == "E":
        encrypt()

    if usrchoice == "D":
        decrypt()

    if usrchoice == "G":
        keygenerate()

    elif usrchoice != "B" or "E" or "D" or "G":
        print("You entered an invalid choice...retard")
        menu()

main()