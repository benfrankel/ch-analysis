#!/usr/bin/env python3

from util.guild.pizza_distribution import auto_summary


def main():
    while True:
        guild_name = input('Guild name (exact): ')
        if not guild_name:
            break
        if not auto_summary(guild_name):
            print(f"The guild '{guild_name}' does not exist\n")
            continue
        print()


if __name__ == '__main__':
    main()
