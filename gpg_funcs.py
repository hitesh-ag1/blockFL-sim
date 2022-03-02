import os
import gnupg

def initialize_gpg_agents(CLIENTS):
    client_deets = {}
    for cl in range(CLIENTS):
        folder = "/home/hitesh/.gnupg"+str(cl)
        
        #Make directory
        cmd1 = "mkdir "+folder
        os.system(cmd1)
        
        #Generate key
        gpg = gnupg.GPG(gnupghome=folder)
        input_data = gpg.gen_key_input(
            name_email='client'+str(cl)+'@xyz.com',
            passphrase='1234')
        key = gpg.gen_key(input_data)
        
        client_deets[cl] = {
                            'folder': folder, 
                            'email': 'client'+str(cl)+'@xyz.com', 
                            'passphrase':'1234',
                            'key': key
                           }
    return client_deets

def share_keys(client_graph, client_deets):
    for client, client_nbs in client_graph.items():
        
        #EXPORT
        gpg = gnupg.GPG(gnupghome=client_deets[client]['folder'])
        ascii_armored_public_keys = gpg.export_keys(client_deets[client]['key'].fingerprint)
        with open('mykeyfile.asc', 'w') as f:
            f.write(ascii_armored_public_keys)
        
        #IMPORT
        for nb in client_nbs:
            gpg = gnupg.GPG(gnupghome=client_deets[nb]['folder'])
            key_data = open('mykeyfile.asc').read()
            import_result = gpg.import_keys(key_data)

def encrypt_file(client_graph, client_deets, model, node):
    gpg = gnupg.GPG(gnupghome=client_deets[node]['folder'])
    with open(model, 'rb') as f:
        nb_emails = [client_deets[nb]['email'] for nb in client_graph[node]]
        status = gpg.encrypt_file(f, recipients=nb_emails, output = model+'.gpg', always_trust=True)
    return status.status


def decrypt_file(client_graph, client_deets, model, node):
    gpg = gnupg.GPG(gnupghome=client_deets[node]['folder'])
    with open(model, 'rb') as f:
        status = gpg.decrypt_file(f, passphrase='1234', output=model+'.json')
    return status.status

def decrypt_str(client_graph, client_deets, string, node):
    gpg = gnupg.GPG(gnupghome=client_deets[node]['folder'])
    decrypted_data = gpg.decrypt(string, passphrase='1234')
    return decrypted_data