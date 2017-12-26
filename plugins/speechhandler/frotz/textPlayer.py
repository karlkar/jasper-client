import os, sys, signal, time, re
from signal import signal, SIGPIPE, SIG_DFL
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty

'''
 Currently, for games that require several clicks to get start info, it doesn't scrape everything. Lost.z5 is one. The first couple commands will not produce the expected output.

 Class Summary: TextPlayer([name of the game file])
 Methods:    run()
             parse_and_execute_command_file([text file containing a list of commands])
             execute_command([command string])
            get_score(), returns None if no score found, returns ('2', '100') if 2/100 found
            quit()
'''
class Response:
    location = ""
    description = ""

class textPlayer:

    # Initializes the class, sets variables
    def __init__(self, game_filename):
        signal(SIGPIPE, SIG_DFL)
        self.game_loaded_properly = True

        # Verify that specified game file exists, else limit functionality
        game_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),"games",game_filename)
        if game_filename == None or not os.path.exists(game_path):
            self.game_loaded_properly = False
            print "Unrecognized game file or bad path"
            return

        self.game_filename = game_filename
        self.game_log = game_filename + '_log.txt'
        self.debug = False

    # Runs the game
    def run(self):
        response=Response()
        if self.game_loaded_properly == True:
            print( "CWD: %s"%os.getcwd() )
            # Start the game process with both 'standard in' and 'standard out' pipes
            dfrotz=os.path.join(os.path.dirname(os.path.realpath(__file__)),"dfrotz")
            game=os.path.join(os.path.dirname(os.path.realpath(__file__)),"games",self.game_filename)
            self.game_process = Popen([dfrotz, game], stdin=PIPE, stdout=PIPE, bufsize=1)

            # Create Queue object
            self.output_queue = Queue()
            t = Thread(target=self.enqueue_pipe_output, args=(self.game_process.stdout, self.output_queue))

            # Thread dies with the program
            t.daemon = True
            t.start()

            # Grab start info from game.
            start_output = self.get_command_output()
            print start_output
            # The following line matches 'hit' in 'white house' in Zork 1
            #if 'Press' in start_output or 'press' in start_output or 'Hit' in start_output or 'hit' in start_output:
            #    start_output += '**'+self.execute_command('\n')
            if 'introduction' in start_output:
                start_output += self.execute_command('no\n') # Parc
            if( self.game_filename=='zork1.z5' ):
                Response.location="West of House"
                Response.description="You are standing in an open field west of a white house, with a boarded front door. There is a small mailbox here."
            return Response
        else:
            print('Game not loaded properly')


    # Sends buffer from output pipe of game to a queue where it can be retrieved later
    def enqueue_pipe_output(self, output, queue):
        for line in iter(output.readline, b''):
            queue.put(line)
        output.close()

    # Run a bash command and wait until it finishes
    def run_bash(self, command):
        process = Popen(command, shell=True)
        process.wait()

    # Parses through a text list of commands (or a single command) and executes them
    def parse_and_execute_command_file(self, input_filename):
        if self.game_loaded_properly == True:
            if (os.path.exists(filename)):
                f = open(filename, 'r')
                commands = f.read()
                f.close()
                if '\n' in commands:
                    for command in commands.split('\n'):
                        print self.execute_command(command)
                else:
                    print self.execute_command(command)

    # Send a command to the game and return the output
    def execute_command(self, command):
        if self.game_loaded_properly == True:
            self.game_process.stdin.write(command + '\n')
            return self.clean_command_output(self.get_command_output())
            #return self.get_command_output()

    # Returns the current score in a game
    def get_score(self):
        if self.game_loaded_properly == True:
            self.game_process.stdin.write('score\n')
            command_output = self.get_command_output()
            score_pattern = '[0-9]+ [\(total ]*[points ]*[out ]*of [a maximum of ]*[a possible ]*[0-9]+'
            matchObj = re.search(score_pattern, command_output, re.M|re.I)
            if matchObj != None:
                score_words = matchObj.group().split(' ')
                return int(score_words[0]), int(score_words[len(score_words)-1])
        return None
            

    # Remove score and move information from output
    def clean_command_output(self, text):
        response=Response()
        print( "Clean_command_output - input : %s",text )
        #regex_list = ['[0-9]+/[0-9+]', '^(.*)Score:[ ]*[-]*[0-9]+(.*)$', 'Moves:[ ]*[0-9]+', 'Turns:[ ]*[0-9]+', '[0-9]+:[0-9]+ [AaPp][Mm]', ' [0-9]+ \.'] # that last one is just for murderer.z5
        #for regex in regex_list:
        #    matchObj = re.findall(regex, text, re.I)
        #    if matchObj != None:
        #        for mo in matchObj:
        #            print( "Found: %s",mo )
        #        text = text[matchObj.end() + 1:]
        #return text
        if(self.game_filename=='zork1.z5'):
            matchObj=re.findall('^\s*(.*?)\s*Score:\s*[-]*[0-9]+\s*Moves:\s*[-]*[0-9]+\s*(.*)$',text,re.I)
            if( len(matchObj) ):
                response.location=matchObj[0][0]
                response.description=matchObj[0][1]
            else:
                # otherwise, this was a simple error message from the parser which does not include a score
                response.description=text
        return response

    # Grab the output from the queue
    def get_command_output(self):
        command_output = ''
        output_continues = True

        # While there is still output in the queue
        while (output_continues):
            try: 
                line = self.output_queue.get(timeout=.001)
            except Empty:
                output_continues = False
            else:
                command_output += line

        # Clean up the output
        command_output = command_output.replace('\n', ' ').replace('>', ' ').replace('<', ' ')
        while '  ' in command_output:
            command_output = command_output.replace('  ', ' ')

        return command_output

    def quit(self):
        if self.game_loaded_properly == True:
            self.game_process.stdin.write('quit\n')
            self.game_process.stdin.write('y\n')
        if self.game_process.stdin != None:
            self.game_process.stdin.write('n\n')

