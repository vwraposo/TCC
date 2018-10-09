import re 

for line in open("char_matrix.txt"):
    if re.match(r'^neuwiedi', line):
        ret = line.split()

chs = [line.split()[1] for line in open("10.txt") if re.match(r'^character', line)] 

f = open("neuwiedi.txt", "w") 
for i in chs:
    z = 0
    u = 0
    if (int(ret[int(i)]) == 1): 
        u = 1
    else:
        z = 1
    f.write("character {0} 0:{1} 1:{2}\n".format(i, z, u))
f.close()
