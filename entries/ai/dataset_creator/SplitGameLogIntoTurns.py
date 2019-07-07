import sys

def usage():
    print "SplitGameLogIntoTurns.py GAME_FILE.LOG"

if __name__=="__main__":
    if len(sys.argv) != 2:
        usage()
    else:
        file_name = sys.argv[1]
        commands = []
        single_command = []
        with open(file_name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                single_command.append(line)
                if line.startswith("go"):
                    commands.append(single_command)
                    print single_command
                    single_command = []
                #endif
            #endfor
        #endwith
    #endif
