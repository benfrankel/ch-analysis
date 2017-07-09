# Introduction

This is an assorted collection of scripts & utilities for the game Card Hunter.


## Dependencies

You need to have [Python 3.6](https://www.python.org/downloads/release/python-361/) installed.

You should also install [git](https://git-scm.com/downloads) to easily download the repository from here.


## Installation

Open a terminal (or command prompt on Windows) and navigate to the place you would like to install CH Analysis.

Enter the command "git clone --depth=1 https://github.com/BenFrankel/CH-Analysis" to download this repository.

Now you can execute any script by running "python <name of script>" in your terminal.


### Discord

Some scripts attempt to operate a Discord bot. Those scripts will fail unless you create your own Discord bot and enter its token in the file `util.guild.chat`.


# Utilities

Below is a description of the scripts & utilities provided by this repository.


## Verbose Log Parser

The module `util.log_parse` parses verbose CH logs into a dictionary structure.


## Battle Reconstructor

The package `battle` parses verbose battle logs in order to extract battle information. The information can then be used to reconstruct the battle. Currently the package extracts all available battle information but cannot yet reconstruct from this information.

This package is incomplete.

### Enemy Deck Tracker

The enemy's deck is among the information that `battle` is able to extract.


## Extreme Deck Optimizer

The package `optimize` receives a character archetype together with a list of card values as input, and finds the deck that maximizes sum of card values.

- Cycling is handled properly (traits or Toughness / Shield Block / etc.)
- Card value packs are available (direct magic damage, crowd healing, direct vampire damage, etc.)


## Guild Utilities

I have scripts to automate several guild-related tasks.

### Pizzatron3000

`control_pizzatron` allows me to make announcements as the Discord bot Pizzatron3000 manually.

### Daily Deal Wishlist

`dd_wishlist` scrapes the Daily Deal forum thread and checks for matches against a wishlist, and if a match is found, makes an announcement on Discord.

### Guild Pizza Distribution Summary

`guild_summary` scrapes the meta site for the per-season performance of any guild and generates a summary of its ideal pizza distribution history.

### Guild Pizza Distribution Report

`distribute_pizza` uses `guild_summary` to upload a summary to pastebin and make an appropriate announcement on Discord.
