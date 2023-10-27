# extraction1 can handle all but SQ items
# to take SQ items the buffer will need to be assigned in each of the four
# leaf's of the main VR, length condition tree. This is because checking for the 
# deliminator requires moving the file forward. Would be change to make extraction2


# imports
from pydicom import dcmread
import pydicom
import dicom2nifti
import matplotlib.pyplot as plt
import sys
import os
import struct

# Open the file in binary read mode

t = './1132_dicom/SER00001/UNWRAP/IMAGES/ST1/SE3/00000001.dcm'
# problem bytes
# i = 615
# i > 38360 and i < 38370:
s = '../testing/3dslicer/3DVisualizationDataset/dataset1_Thorax_Abdomen/IM-0001-0002.dcm'
good_tags = False

with open(((not good_tags)*t + good_tags*s), 'rb') as f:
    # Read the preamble and DICOM prefix
    preamble = f.read(128)
    prefix = f.read(4)

    if prefix != b'DICM':
        raise ValueError("Not a valid DICOM file!")
   
    groups = []
    elements = []
    types = []
    bufs = []

    r = ''
    g = ''
    e = ''
    t1 = ''
    t2 = ''
    type = ''
    bs = -1
    buf = []

    insert_idx = -1
    insert_buf = 0

    hex_types = ['UI', 'SH', 'AE', 'CS', 'DA', 'TM', 'LO', 'PN', 'LT', 'SQ', 'US']

    file = ((not good_tags)*('bad_tags.txt') + good_tags*('good_tags.txt'))
    if os.path.isfile(file):
        os.remove(file)
        with open(file, 'w') as ff:
            ff.write('')
    
    i=0
    while i < os.stat(((not good_tags)*t + good_tags*s)).st_size:

        if i > 38360 and i < 38370:
            f.read(20) # no idea what this is
        
        first = f.read(1)
        if ord(first) == 62 and g == '':
            continue # indent

        # group
        g = first.hex()
        g = f.read(1).hex() + g
        # element
        e = f.read(1).hex()
        e = f.read(1).hex() + e
        
        r = f.read(1)
        r1 = f.read(1)
        r2 = f.read(1)
        i+=7
        if (not r1.decode().isdigit()): # explicit VR
            type = r.decode() + r1.decode()

            if type == 'SQ':
                # if explicit SQ

                f.read(1)
                r3 = f.read(4)
                i+=5
                
                if r3 == b'\xff\xff\xff\xff': # undefined length

                    pos_de = [b'\x00',b'\x00',b'\x00',b'\x00']
                    found = False
                    j = 0
                    while not found:

                        d1 = f.read(1)
                        pos_de = pos_de[1:]
                        pos_de.append(d1)
                        j+=1
                        # print(f'i = {i+j+1} |||| j = {j} |||| current byte: {r} |||| pos_de = {b"".join(pos_de)}')

                        if b"".join(pos_de) == b'\xfe\xff\xdd\xe0': # deliminator
                            found = True

                    bs = 3 # end of deliminator buffer 
                    i+=j
                    a = 0
            
                else: # defined length
                    f.read(int.from_bytes(r3, byteorder='little')-1)
                    bs = 0

            else:

                if type == 'OB':
                    bs = 6 # skip OB, dont know about it, no deliminator
                # elif type == 'ST':
                #     bs = 5
                else:
                    bs = ord(r2)

        elif (not r1.decode().isdigit()): # implicit VR

            
            if r2 == b'\xff': # undefined length
                
                pos_de = [b'\x00',b'\x00',b'\x00',b'\x00']
                found = False
                j = 0
                while not found: # skipping
                    j+=4
                    f.read(1)
                    pos_delim = f.read(4) # looking for FFFFE,E0DD

                    d1 = f.read(1)
                    pos_de = pos_de[1:]
                    pos_de.append(d1)
                    j+=1
                    # print(f'i = {i+j+1} |||| j = {j} |||| current byte: {r} |||| pos_de = {b"".join(pos_de)}')

                    if b"".join(pos_de) == b'\xfe\xff\xdd\xe0': # deliminator
                        found = True

                bs = 3 # end of deliminator buffer 
                i+=j
                a = 0
            
            else: # defined length

                bs = ord(r2)

        
        f.read(1) # pad
        buf = f.read(bs)
        i+=bs+1

        groups.append(g)
        elements.append(e)
        types.append(t1+t2)
        bufs.append(buf)

        with open(file, 'a') as ff:
            ss = ''.join([str(ss) if str(ss).isalnum() else '' for ss in buf])
            ff.write(f'({g}, {e}) {type} {ss}, len={len(buf)} \n')
        
        # if g == '0040' and e == '1001':
        #     break


        print(f'-----------')
        print(f'i = {i} |||| r: {r} |||| ({g}, {e}) {type}, bs: {bs}, buf: {buf}')

        g = ''
        e = ''
        type = ''
        bs = -1
        buf = ''




        # elif '\\x' not in str(r):

        #     # implicit VR

        #     if r == b'\xff': # implicit VR, implicit length. Skipping for now
        #         f.read(3) # ffffff
        #         pos_de = [b'\x00',b'\x00',b'\x00',b'\x00']
        #         found = False
        #         j = 0
        #         while not found:
        #             j+=2
        #             i+=2
        #             # pos_delim = f.read(4) # looking for FFFFE,E0DD

        #             r1 = f.read(1)
        #             r2 = f.read(1)
        #             pos_de = pos_de[2:]
        #             pos_de.append(r1)
        #             pos_de.append(r2)
        #             print(f'i = {i+j+1} |||| j = {j} |||| current byte: {r} |||| pos_de = {b"".join(pos_de)}')

        #             if b"".join(pos_de) == b'\xfe\xff\xdd\xe0': 
        #                 print(pos_de)
        #                 found = True

        #         f.read(4) # end of sequence after deliminator b'\x00\x00\x00\x00'
        #         i+=7 # not actually 8 should be 3+4 but this works
        #         # new data elements
        #         g = ''
        #         e = ''
        #         continue
            
        #     # implicit VR, explicit length

        # elif '\\x' in str(r):
        #     if t1 == '':
        #         t1 = r.decode()
        #     elif t2 == '':
        #         t2 = r.decode()
        #         if t1 == 'b':
        #             t1 = 'n'
        #             t2 = 'a'
        #         type = t1+t2
        # elif bs == -1:
        #     if type == 'OB':
        #         f.read(1)
        #         r = f.read(1)
        #         bs = struct.unpack('B', r)[0]*2
        #         f.read(1)
        #         i+=3
        #     elif type == 'SQ':
        #         f.read(1)
        #         byte_bs = f.read(1)
        #         i+=2
                
        #         if byte_bs == b'\xff':
        #             bs = 11
        #         else:
        #             bs = 5
        #     else:
        #         bs = struct.unpack('B', r)[0]
        #         f.read(1)
        #         i+=1
        # else:
        #     if sum([type == tt for tt in hex_types]) == 1:
        #         if i == 615:
        #             buf+='*'
        #         else:
        #             buf+= [r]    
        #     else:
        #         buf+= [struct.unpack('B', r)[0]]


        # a = 5
        # if len(buf) == bs:
        #     groups.append(g)
        #     elements.append(e)
        #     types.append(t1+t2)
        #     bufs.append(buf)

        #     with open(file, 'a') as ff:
        #         ss = ''.join([str(ss) if str(ss).isalnum() else '' for ss in buf])
        #         ff.write(f'({g}, {e}) {type} {ss}, len={len(buf)} \n')
            
        #     # if g == '0040' and e == '1001':
        #     #     break
            

        #     g = ''
        #     e = ''
        #     t1 = ''
        #     t2 = ''
        #     type = ''
        #     bs = -1
        #     buf = []

# with open('tags_test.txt', 'w') as f:
#     for line in list(zip(groups, elements, types, bufs)):
#         s = ''.join([str(s) if str(s).isalnum() else '' for s in line[3]])
#         f.write(f'({line[0]}, {line[1]}) {line[2]} {s}, len={len(line[3])} \n')
            


# # insert new bytes
# with open(s, 'w') as f:

#     i = 0
#     while i < (os.stat(s).st_size):
#         i+=0

#         if i == insert_idx:
#             for b in insert_buf:
#                 f.write(b)
#         else:
#             f.write(f.read(1))