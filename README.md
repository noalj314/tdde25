Starting the game:
To start the game one needs to have python3 installed and our folder downloaded. Simply go in to the ctf folder and type following commands in the terminal:
-	source setup.sh
-	python3 ctf.py 
    or 
    python3 ctf.py --big (for bigger menu) 

Implemented features:
-	Counting score. The game is made to be played indefinitely and the score of respective tanks is counted and displayed in the console. 

-	Sounds. We have different sound effects for handling different events such as shooting, capturing the flag etc. 

-	Hot seat multiplayer. In the main menu of the game one can choose to play singleplayer or multiplayer. Multiplayer meaning that two people can play together on the same computer.

-	Hit points. Tanks and wooden boxes have different hitpoints, meaning that they need different amount of shots to get destroyed.

-	Respawn protection. When a tank has been destroyed, there is a brief interval where the tank cannot be damaged. 

-	Unfair ai. The ai controlled tanks have a greater bullet speed and tank speed to create a more challenging game. 

-	Welcome screen. When the game is launched the player is received by a welcome screen with different choices for maps and game mode. 

-	Score screen. Counting score feature is implemented on the game screen instead of the console. 

-	Power-ups. Different power-ups spawn around the map. When a tank goes over the power-up they receive a temporary increase in one of the stats depending on the power-up. 



Brief explanation of each file and how the main program calls them:
The game consists of 9 different files. The main file of the game is ctf.py and all other files have unique tasks and handle different aspects of the game. 

Ai.py
The file for the ai controlled tanks contains different functions so that some of the tanks can be ai controlled. They are programmed to find the flag and return it to their homebase, destroying any tanks or wooden boxes in their way. The ai files is imported at the top of the main file and the main file calls the ai class to create the ai controlled tanks. 

Gameobjects.py
This file contains all the physical objects within the game such as the different boxes and the tanks. It is responsible for all the attributes of the different objects. How they move, how they shoot etc. The file is imported at the top of the main file and respective object calls its corresponding function. 

Images.py
All images used in the game are loaded and stored here. The file is imported at the top of the game and each picture is imported when needed. 

Maps.py
All maps are created and stored here. The relevant map is imported when the user chooses one at the main menu. 

Menu.py
The menu file contains the welcome screen. It is imported at the top of the main file. 

Game_over.py
This file is for the menu that is called and appears every time a player (tank) has won. 

Sounds.py
All sounds used in the game are loaded and stored here. The file is imported at the top of the game and each sound is imported when respective event has occurred.

Ctf.py
This is the main file that consists of a main game function which contains all the functions that create the game. There is also a main loop that contains all the functions that are called continuously such as handling events when different keys are pressed. The loop is called every frame (which is 50 frames per second in our case). 

Starting the game:
To start the game one needs to have python3 installed and our folder downloaded. Simply go in to the ctf folder and type following commands in the terminal:
-	source setup.sh
-	python3 ctf.py 
    or 
    python3 ctf.py --big (for bigger menu) 

Implemented features:
-	Counting score. The game is made to be played indefinitely and the score of respective tanks is counted and displayed in the console. 

-	Sounds. We have different sound effects for handling different events such as shooting, capturing the flag etc. 

-	Hot seat multiplayer. In the main menu of the game one can choose to play singleplayer or multiplayer. Multiplayer meaning that two people can play together on the same computer.

-	Hit points. Tanks and wooden boxes have different hitpoints, meaning that they need different amount of shots to get destroyed.

-	Respawn protection. When a tank has been destroyed, there is a brief interval where the tank cannot be damaged. 

-	Unfair ai. The ai controlled tanks have a greater bullet speed and tank speed to create a more challenging game. 

-	Welcome screen. When the game is launched the player is received by a welcome screen with different choices for maps and game mode. 

-	Score screen. Counting score feature is implemented on the game screen instead of the console. 

-	Power-ups. Different power-ups spawn around the map. When a tank goes over the power-up they receive a temporary increase in one of the stats depending on the power-up. 



Brief explanation of each file and how the main program calls them:
The game consists of 9 different files. The main file of the game is ctf.py and all other files have unique tasks and handle different aspects of the game. 

Ai.py
The file for the ai controlled tanks contains different functions so that some of the tanks can be ai controlled. They are programmed to find the flag and return it to their homebase, destroying any tanks or wooden boxes in their way. The ai files is imported at the top of the main file and the main file calls the ai class to create the ai controlled tanks. 

Gameobjects.py
This file contains all the physical objects within the game such as the different boxes and the tanks. It is responsible for all the attributes of the different objects. How they move, how they shoot etc. The file is imported at the top of the main file and respective object calls its corresponding function. 

Images.py
All images used in the game are loaded and stored here. The file is imported at the top of the game and each picture is imported when needed. 

Maps.py
All maps are created and stored here. The relevant map is imported when the user chooses one at the main menu. 

Menu.py
The menu file contains the welcome screen. It is imported at the top of the main file. 

Game_over.py
This file is for the menu that is called and appears every time a player (tank) has won. 

Sounds.py
All sounds used in the game are loaded and stored here. The file is imported at the top of the game and each sound is imported when respective event has occurred.

Ctf.py
This is the main file that consists of a main game function which contains all the functions that create the game. There is also a main loop that contains all the functions that are called continuously such as handling events when different keys are pressed. The loop is called every frame (which is 50 frames per second in our case). 


load_image('menubackground.png')
load_image('score.png')  