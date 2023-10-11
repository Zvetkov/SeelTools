# SeelTools

Work in progress GUI toolkit for Ex Machina / Hard Truck Apocalypse, POC stage, mostly abandoned at this point.

Only reading, inspecting and writing structured data back is implemented!

**Editing data is not possible from GUI!**


This was a reverse engineering project to study the game's stucture, as such it can be used to research what properties are supported by any of the many Prototype classes (these describe all the entities in the game - cars, guns, towns, quests etc.)

Developers: 

[Aleksandr Parfenenkov](mailto:work.zvetkov@gmail.com)

[Andrey Shpilevoy](https://github.com/AndreyShpilevoy)

## Features
Tries to mimics main game module ("Server") initialisation.
Currently implemented / partially implemented:
* Resource Manager - loading handling resource id, names, inheritence
* Affix Manager - loading and handling object affixes, use for weapons and vehicle parts
* Relationship Manager - loading and handling relationship between factions
* Prototype Manager - loading and handling Prototypes from xml files, Prototypes later used to initilaised game objects

* Game Object classes - 120 classes, subclasses and dummy classes
* Game Object Prototype classes - 111 prototype classes

Displays all loaded prototype from game files as a tree in GUI.

## Quick start

### Prerequisites

* Python 3, tested on `3.8.2`
* requirements.txt

### Installation and execution:

Tool tries to find game working directory in Steam libraries. If suitable install not found, it will fallback to hardcoded path.

Fallback path to game directory in `seeltools/utilities/constants.py`:
```py
FALLBACK_WORKING_DIRECTORY = "D:/Steam/steamapps/common/Hard Truck Apocalypse"
```

Install required modules using `pip`:
```bash
pip install -r requirements.txt
```

Run entry point script `seeltools_qt.py`:
```bash
py .\seeltools_qt.py
```

### Code style:
Maximum line length: 120 characters

Naming:
* We use Targem style(camelCase, TitleCase) for functions, classes and variables taken from original game.
* We use pythonic style(snake_case, TitleCase, CAPS_CASE) for all other new native entities created for use in tool.

When possible for Targem vars/funcs/classes we try to save original names, for new entities use 1) descriptive, 2) short names  - in that order of priorities.
 
 Taken from game:
 * variablesInCamelCase (remove "m_", "b_" etc and replace TitleCase if found in original variables)
 * ClassesInTitleCase, FunctionsInTileCase
 
 Native:
* snake_case - variable names, function names, method names, and module or package (i.e. file) names
* TitleCase - class names
* CAPITALIZED_NAMES - constants 
Also see: https://www.python.org/dev/peps/pep-0008/ and https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html
