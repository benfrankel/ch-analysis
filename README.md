# CH Analysis

This repository holds a collection of scripts & utilities for the game Card Hunter.


## Dependencies

You'll need [Python 3.6](https://www.python.org/downloads/release/python-361/) installed to run the scripts.

You should also install [git](https://git-scm.com/downloads) to download the repository from here.


### Discord

Some scripts attempt to operate a Discord bot. Those scripts will fail unless you create your own Discord bot and enter its token in the file `util.guild.chat`.

Furthermore, they require the module `discord.py`, which is available on PyPI (so you can download it using pip).


## Installation

Open a terminal (or command prompt on Windows) and navigate to the place you would like to install CH Analysis.

Enter the command "git clone --depth=1 https://github.com/BenFrankel/CH-Analysis" to download this repository.

Now you can execute any script by running "python \<name of script\>" in your terminal.


# Utilities

Below is an overview of the utilities provided by this repository.


## Verbose Log Parser

The module `util.log_parse` parses verbose CH logs into a dictionary structure.


## Battle Reconstructor

The package `battle` parses verbose battle logs in order to extract battle information. The information can then be used to reconstruct the battle. Currently the package extracts all available battle information but cannot yet reconstruct from this information.

This package is incomplete.

### Enemy Deck Tracker

The enemy's deck is among the information that `battle` is able to extract.


## Battle History

The package `meta` can download a player's battle history from the meta site. It also provides functions to query the resulting data, and to calculate statistics from the data.

The following statistics are available:

- Summary of a list of battles, showing win percentage, wins - defeats, and blitz wins - normal wins - normal defeats - blitz defeats
    - Summary applied to one player
    - Summary applied to all matchups between two players
- Ladder of a player's performance against guild players or guilds
    - Ladder ranking a player's net contribution gain / loss against opponents
    - Ladder ranking a player's net wins / defeats against opponents


## Extreme Deck Optimizer

The package `optimize` receives a character archetype together with a list of card values as input, and finds the deck that maximizes total card value. In addition,

- Cycling is handled properly (traits or Toughness / Shield Block / etc.)
- Card value packs are available (direct magic damage, crowd healing, direct vampire damage, etc.)


## Guild Utilities

The following scripts are used to automate several guild-related tasks.

### Discord Bot Manual Control

`control_discord_bot` allows you to make announcements as your Discord bot manually.

### Daily Deal Wishlist

`daily_deal_wishlist` scrapes the Daily Deal forum thread and checks for matches against a wishlist, and if a match is found, makes an announcement on Discord.

### Guild Pizza Distribution Summary

`guild_summary` scrapes the meta site for the per-season performance of any guild, then generates a summary of its ideal pizza distribution history.

### Guild Pizza Distribution Report

`distribute_pizza` uses `guild_summary` to upload a summary to pastebin and then announce the results on Discord.
