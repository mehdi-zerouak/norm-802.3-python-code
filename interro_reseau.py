import sys
#           +--------------------+
#           |  PROJET TD RESEAU  |
#           |    ZEROUAK MEHDI   |
#           |       G3 - I       |
#           +--------------------+


# ------------ debut du programme ----------------------

print('\n---------- PROJET TD RESEAU ---------- \n')
print('Welcome \n')

# -------- les constants ---------

PREAMBLE = '01010101010101010101010101010101010101010101010101010101'
SFD = '10101011'

PREAMBLE_HX = '55555555555555'
SFD_HX = 'AB'

# ------- les entrées d'utilisateur 1 ( source + destination ) ---------

print("---- Destination/source adresses ----- \n")

print("Note: La format de l'adresse MAC est XX-XX-XX-XX-XX-XX ou XXXXXXXXXXXX ! (en hexadecimal (12 caractere) )")

# fonction pour validé les adresses
def validate_mac_address(mac):

    mac = mac.replace('-', '') # XX-XX-XX-XX-XX-XX to XXXXXXXXXXXX

    if len(mac) != 12:
        print("Erreur! L'adresse MAC doit contenir 12 caractères\n")
        sys.exit() 

    for i in range(12):
        if mac[i] not in '0123456789ABCDEF':
            print("Erreur! Adresse MAC non valide (les caractere valid sont: 0-9 ou A-F)\n")
            sys.exit()

    return True


destination_address = input("L'adresse de la destination: ")
validate_mac_address(destination_address)

source_address = input("L'adresse de la source: ")
validate_mac_address(source_address)

# ------- les entrées d'utilisateur 2 ( Data ) ---------

print("\n ---- Data (en hexadecimal) ----- \n")

# fonction pour validé les données
def validate_data(data):

    if len(data) < 1:
        print("Erreur! aucune donnée à envoyer! \n")
        sys.exit()

    for i in range(len(data)):
        if data[i] not in '0123456789ABCDEF':
            print("Erreur! Data non valide (les caractere valid sont: 0-9 ou A-F) \n")
            sys.exit()

data = input("Les données: ")
validate_data(data)

# calculation des trames

if len(data) % 32 == 0:
    nombre_des_trames = ( len(data) // 32 )
    # 32 car une data de trame contient 16 bytes et chaque byte = 2 lettres en hexadecimal
else:
    nombre_des_trames = ( len(data) // 32 ) + 1

# division de notre data en plusieur trames
data_de_chaque_trame_en_hexadecimal = []

for i in range(0 , len(data) , 32):
    data_de_chaque_trame_en_hexadecimal.append(data[i:i+32])

# --------- calculation du length (LEN) de chaque trame -------------

len_data_de_chaque_trame = [] # nombre des octets de data de chaque trames

for i in range(nombre_des_trames):
    len_data = len(data_de_chaque_trame_en_hexadecimal[i])
    if len_data % 2 == 0:
        len_data_de_chaque_trame.append( len_data // 2 )
    else:
        len_data_de_chaque_trame.append( (len_data // 2) + 1 )
    # car 1 character d'hexadecimal = 4 bits en binaire et 1 byte = 8 bits
    # len_data est le nombre des octets de trame data

# padding pour data si le LEN est inferieur a 16

for i in range(nombre_des_trames):
    if len_data_de_chaque_trame[i] < 16:
        # add padding
        while ( len(data_de_chaque_trame_en_hexadecimal[i]) < 32 ):
            data_de_chaque_trame_en_hexadecimal[i] += '00' 


# ---------- calculation du CRC de chaque trame ---------------------
    # CRC = VRC1 + VRC2 + LRC1 + LRC2

# data de chaque trame en binaire pour calculer VRC + LRC
data_de_chaque_trame_en_binaire = []

# HELPER FUNCTION 1 
def hexadecimal_to_binaire(hexadecimal1 , length ):
    binaire = ''
    hex_dict = {'0': '0000', '1': '0001', '2': '0010', '3': '0011',
                '4': '0100', '5': '0101', '6': '0110', '7': '0111',
                '8': '1000', '9': '1001', 'A': '1010', 'B': '1011',
                'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'  }
    

    for j in range(length):
        binaire += hex_dict[hexadecimal1[j]]

    return binaire

for i in range(nombre_des_trames):

    hex_data = data_de_chaque_trame_en_hexadecimal[i]

    binary_data = hexadecimal_to_binaire(hex_data , 32)

    data_de_chaque_trame_en_binaire.append(binary_data)

# division de chaque data de trame a 2 partie (8 byte + 8 byte)
data_de_chaque_trame_en_binaire_sur_2 = []

for i in range(nombre_des_trames):
    byte_1 = data_de_chaque_trame_en_binaire[i][0:64] # car 8 bytes = 128 bits en binaire, 128 / 2 = 64
    byte_2 = data_de_chaque_trame_en_binaire[i][64:128]
    data_de_chaque_trame_en_binaire_sur_2.append([byte_1 , byte_2])


# ---------------------- calculation de VRC et LRC ------------------------------

# LRC
def calculate_LRC(half_frame_data):
    # half frame data est une chaine de 64 caractere (8 bytes)
    lrc = ''
    for i in range(0 , 64 , 8):

        nombre_des_1 = 0
        for j in range(8):
            if half_frame_data[j+i] == '1':
                nombre_des_1 += 1

        if nombre_des_1 % 2 == 0:
            lrc += '0'
        else:
            lrc += '1'

    return lrc


def calculate_VRC(half_frame_data):
    vrc = ''
    for i in range(8):

        nombre_des_1 = 0
        for j in range(0, 64 , 8):
            if half_frame_data[i+j] == '1':
                nombre_des_1 += 1

        if nombre_des_1 % 2 == 0:
            vrc += '0'
        else:
            vrc += '1'

    return vrc

# calculation de CRC de chaque trame , Tq CRC = VRC1 + VRC2 + LRC1 + LRC2

crc_de_chaque_trame_en_binaire = []

for i in range(nombre_des_trames):

    first_half_data = data_de_chaque_trame_en_binaire_sur_2[i][0]
    second_half_data = data_de_chaque_trame_en_binaire_sur_2[i][1]

    vrc1 = calculate_VRC(first_half_data)
    vrc2 = calculate_VRC(second_half_data)

    lrc1 = calculate_LRC(first_half_data)
    lrc2 = calculate_LRC(second_half_data)

    crc = vrc1 + vrc2 + lrc1 + lrc2

    crc_de_chaque_trame_en_binaire.append(crc)


# hexadecimal crc

crc_de_chaque_trame_en_hexadecimal = []

for i in range(nombre_des_trames):
    binaire = crc_de_chaque_trame_en_binaire[i]
    decimal = int(binaire , 2)
    hexadecimal = format(decimal , 'X') # mais 00001111 = F avec cette fonction mais nous voulons 0F
    # donc ......
    len_hex = len(hexadecimal)

    if len_hex < 8:
        tmp = 8 - len_hex
        for j in range(tmp):
            hexadecimal = '0' + hexadecimal # c comme un padding a gauche
    
            
    crc_de_chaque_trame_en_hexadecimal.append(hexadecimal)


# ------------ affichage --------------------------
print('\n ---- Resultat ----- \n')
print(f' * Nombre des trames: {nombre_des_trames} trames \n')
print(' ---- Affichage des trames avec la form 802.3 (en hexadecimal) ---- \n')

for i in range(nombre_des_trames):
    print('___________________________________________________________________________________')
    print(f'*** Trame N°{i+1} ***')
    # affichage de trame avec la format 802.3 en hexadecimal
    data_padding = data_de_chaque_trame_en_hexadecimal[i]
    crc = crc_de_chaque_trame_en_hexadecimal[i]
    len = format(len_data_de_chaque_trame[i] , 'X')
    print('+---------------------------------------------------------------------------------------+')
    print(f'|{PREAMBLE_HX}|{SFD_HX}|{destination_address}|{source_address}|{len}|{data_padding}|{crc}|')
    print('+---------------------------------------------------------------------------------------+')
    print('___________________________________________________________________________________\n\n')


affichage_binaire = input(' * Voulez-vous afficher les trames en binaire ? ( 1 -> oui , autre caractere -> quitter ): ')
if affichage_binaire == '1':
    print(' ---- Affichage des trames avec la form 802.3 (en binaire) ---- \n')

    for i in range(nombre_des_trames):
        print('___________________________________________________________________________________')
        print(f'*** Trame N°{i+1} ***')
         # affichage de trame avec la format 802.3 en binaire
        data_padding_b = data_de_chaque_trame_en_binaire[i]
        crc_b = crc_de_chaque_trame_en_binaire[i]
        destination_address_b = hexadecimal_to_binaire(destination_address , 12)
        source_address_b = hexadecimal_to_binaire(source_address , 12)
        len_b = bin(len_data_de_chaque_trame[i]).lstrip('-0b') # psq cette fonction retourn -0b apres le chiffre binaire
        print('-------------------------------------------------------------------------------------')
        print(f'Preamble: {PREAMBLE}')
        print(f'SFD: {SFD}')
        print(f'Destination: {destination_address_b}')
        print(f'Source: {source_address_b}')
        print(f'Len: {len_b} (sans le padding a gauche)')
        print(f'Data&Padding: {data_padding_b}')
        print(f'CRC: {crc_b}')
        print('-------------------------------------------------------------------------------------')
        print('___________________________________________________________________________________\n\n')

print('\nFin de programme. \n\n')