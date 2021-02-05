# Endless-Sky-Optimizer
## Motivation
Endless Sky (https://endless-sky.github.io/) is an open source space exploration game. Your ship has energy generation and energy storage which is used to power your equipment. Using your equipment generates heat and if you overheat, your ship shuts down. This program uses dynamic programming to find the optimal equipment for the limited space on your ship to maximize your ship's energy generation while keeping your heat low enough that your ship will never overheat.

## Usage
In the folder `inputs` create at `.txt` file with the first line as the name of the ship model and subsequent lines as the names of any non energy generation/cooling related equipment you would like to install, e.g., hyperdrive, weapons, etc. All the files already in this folder are just examples. Run `python3 endlessSkyOptimizer.py [input file name]` to run the program. For example `python3 endlessSkyOptimizer.py exampleInput.txt` 

You can convert cargo space on your ship into equipment space by installing "outfits expansions." Installing these affects the the heat of your ship in a more complicated way such that they can't be treated like other equipment. When running the program you will be given two options. 1) The program runs a search for every number of outfits expansions you could have installed just to show you all your options (starting with however many you have listed in your input file). 2) The program runs a search using only the outfits expansions listed in your input file.

The energy outfits you should install along with the energy generation and net heat of your ship will be printed and saved to the `outputs` folder. The energy generation is what the program is trying to maximize, but it assumes you are firing all your weapons and engines constantly, so it will probably be a negative value in a good ship design. The net heat value is the maximum heat your ship can reach from firing all its weapons and engines constantly with anything above 0 overheating. The program aims to keep this value below 0, but it rounds a little bit to make the runtime faster, so you may get a small positive number on the order of 10. This is still a fine ship design even if this happens because in real gameplay you are never really maxing out all your heat generating equipment for prolonged periods of time, and external sources like enemy weapons cause small fluctuations in your heat levels anyway.

## TODO
- clean up the input output and make that easier
- is there a better way to handle outfits expansions?
- maybe reduce runtime on larger ships by capping capping heat within some range probably [-100000,10000]; check what largest heat generation on single item is (korath double stack core?)
- improve example files to show multi item input functionality
- general neatening or the functions in the main file
