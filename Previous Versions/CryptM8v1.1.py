#CryptM8 v1.1 J.Street 04/04/2019 'Jordanstreet@protonmail.com'

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
    keygenerate()
    menu()

def keygenerate():
    global key
    global user_salt
    user_password = input("Enter your encryption key: ") #if file exists load from that or generate for user?
    user_password = user_password.encode()
    user_salt = input("Enter your encryption salt (or enter G if you wish to generate one): ") #Same with salt?
    if user_salt == "G":
        print("Generating key...")
        user_salt = base64.b64encode(os.urandom(16))
    else:
        print("Unlocking...")
        user_salt = user_salt.encode()
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

    menu()

def encrypt():

    input_file = input("Enter the full file path: ")
    output_file = input_file + ".kek"

    try:
        with open(input_file, 'rb') as f:
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
            print("|Loading file into memory|")
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
        print("|Decryption Sucessful|")
        menu()
    except:
        print("Probable invalid key or file too large", sys.exc_info()[0], "Occured")
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
    print("Current loaded key is: " + str(key))
    print("Current loaded salt is: " + str(user_salt))
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