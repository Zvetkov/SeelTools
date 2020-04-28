# SeelTools

Work in progress GUI toolkit for Ex Machina / Hard Truck Apocalypse, currently at the POC stage.

Maintainer: [Aleksandr Parfenenkov](mailto:work.zvetkov@gmail.com)

## Features
Tries to mimics main game module ("Server") initialisation.
Currently implemented / partially implemented:
Resource Manager - loading handling resource id, names, inheritence
Affix Manager - loading and handling object affixes, use for weapons and vehicle parts
Relationship Manager - loading and handling relationship between factions
Prototype Manager - loading and handling Prototypes from xml files, Prototypes later used to initilaised game objects

Game Object classes - 120 classes, subclasses and dummy classes
Game Object Prototype classes - 111 prototype classes

Displays all loaded prototype from 

## Quick start

### Prerequisites

* Python 3, tested on `3.8.2`

Additional libs:
* lxml
* PySide2


### Installation and execution:

Change path to game directory in `seeltools/utilities/constants.py`:
```py
WORKING_DIRECTORY = "D:/Steam/steamapps/common/Hard Truck Apocalypse"
```

Install required modules using `pip`:
```bash
pip install -r requirements.txt
```

Run entry point script `seeltools_qt.py` or run as module from repository root:
```bash
python -m seeltools
```