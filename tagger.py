import sys
if len(sys.argv) < 3:
    print ("usage: {} filename out-filename".format(sys.argv[0]))
    sys.exit(1)
filename = sys.argv[1]
out_filename = sys.argv[2]

out = ''
with open(filename, 'r') as f:
    for line in f:
        line = line.strip()
        print (line)
        type = ''
        while type not in ['P', 'T', 'I']:
            print ("Type [P: Place, T: Time, I: Ignore]")
            type = raw_input()

        out += line + '\t' + type + '\n'

with open(out_filename, 'w') as f:
    f.write(out)
