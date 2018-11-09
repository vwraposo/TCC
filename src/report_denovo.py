from CADM import CADM
import os 
import sys

def report(folder):
    dirname = '../input/'
    gen = dirname + 'genomic/genomic.nex.con.tre'

    dirname += folder

    directory = os.fsencode(dirname)


    # Compare with others 

    print("Report comparing topology using the CADM test of the resulting denovo trees with the tree obtained with the genomic data.")
    print(30*("-"))
    for d in os.listdir(directory):
        dname = os.fsdecode(d)
        if (not os.path.isdir(dirname + '/' + dname)):
            continue
        print('Target: ' + dname)
        tree = '{0}/{1}/peptides.nex.con.tre'.format(dirname, dname)
        print(tree)
        CADM(gen, tree, '-p')

        print(30*("-"))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        sys.exit(-1)

    report(sys.argv[1])

