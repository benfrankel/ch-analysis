# CH Analysis

This repository holds a collection of scripts & utilities for the game Card Hunter, including the code for the Discord bot "Pizzatron".


## Dependencies

You'll need [Python 3.6](https://www.python.org/downloads/release/python-361/) installed to run the scripts.

You should also install [git](https://git-scm.com/downloads) to download the repository from here.


### Discord

Some scripts attempt to operate a Discord bot. Those scripts will fail unless you create your own Discord bot and enter its token in the file `secrets.py` as `PIZZATRON_TOKEN = '<your token here>'`

Furthermore, they require the module `discord.py`, which is available on PyPI (so you can download it using pip).


## Installation

Open a terminal (or command prompt on Windows) and navigate to the place you would like to install CH Analysis.

Enter the command "git clone --depth=1 https://github.com/benfrankel/ch-analysis" to download this repository.

Now you can execute any script by running "python \<name of script\>" in your terminal.


# Utilities

Below is an overview of the utilities provided by this repository.

## Discord Bot

`run_pizzatron` runs the Discord bot.

`control_pizzatron` allows you to send messages as the Discord bot manually.


## Verbose Log Parser

The module `util.log_parse` parses verbose CH logs into a dictionary structure.


## Battle Reconstructor

The package `battle` parses verbose battle logs in order to extract battle information. The information can then be used to reconstruct the battle. Currently the package extracts all available battle information but cannot yet reconstruct from this information.

This package is incomplete.

### Enemy Deck Tracker

The enemy's deck is among the information that `battle` is able to extract.


## Battle History

The package `metadata` can download battle history from the API.


## Extreme Deck Optimizer

The package `optimize` receives a character archetype along with a list of card values as input, and finds the deck that maximizes total card value. In addition,

- Cycling is handled properly (traits or Toughness / Shield Block / etc.)
- Card value packs are available (direct magic damage, crowd healing, direct vampire damage, etc.)

