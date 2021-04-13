#!/usr/bin/env python3

import pizzatron


def main():
    pizzatron.load()
    client = pizzatron.Client()
    client.run(pizzatron.TOKEN)


if __name__ == '__main__':
    main()
