This is my bot from the Google AI Challenge, it ranked 1298 out of 4617. 
To see it in action either run the command below or watch its tournament 
matches at:
http://planetwars.aichallenge.org/profile.php?user_id=10290

java -jar tools/PlayGame.jar maps/map1.txt 10000 200 log.txt "python entries/ai/MyBot.py" "java -jar example_bots/DualBot.jar" | java -jar tools/ShowGame.jar
java -jar tools/PlayGame.jar maps/map1.txt 200 200 log.txt "python entries/2/MyBot.py" "python entries/radu/RaduBot.jar" | java -jar tools/ShowGame.jar


The files in this package are part of a starter package from the Google AI
Challenge. The Google AI Challenge is an Artificial Intelligence programming
contest. You can get more information by visiting www.ai-contest.com.

The entire contents of this starter package are released under the Apache
license as is all code related to the Google AI Challenge. See
code.google.com/p/ai-contest/ for more details.

There are a bunch of tutorials on the ai-contest.com website that tell you
what to do with the contents of this starter package. For the impatient, here
is a brief summary.
  * In the root directory, there are a bunch of code files. These are a simple
    working contest entry that employs a basic strategy. These are meant to be
    used as a starting point for you to start writing your own entry.
    Alternatively, you can just package up the starter package as-is and submit
    it on the website.
  * The tools directory contains a game engine and visualizer. This is meant
    to be used to test your bot. See the relevant tutorials on the website for
    information about how to use the tools.
  * The example_bots directory contains some sample bots for you to test your
    own bot against.


java -jar tools/PlayGame.jar maps/map1.txt 10000 200 log.txt "python entries/ai/MyBot.py" "python jomabot2/MyBot.py" | java -jar tools/ShowGame.jar