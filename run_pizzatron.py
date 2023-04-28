#!/usr/bin/env python3

import pizzatron


def main():
    client = pizzatron.Client()
    client.load()
    client.run(pizzatron.TOKEN)


if __name__ == '__main__':
    main()
