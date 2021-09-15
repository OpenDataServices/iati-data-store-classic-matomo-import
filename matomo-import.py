
import argparse


def main():

    parser = argparse.ArgumentParser(
            description="Import HTTP access logs to Matomo. ",
            epilog="https://github.com/OpenDataServices/iati-data-store-classic-matomo-import"
        )

    parser.add_argument('file', type=str, nargs='?')
    parser.add_argument('host', type=str, nargs='?')
    parser.add_argument('siteid', type=int, nargs='?')

    args = parser.parse_args()

    config = Config(
        args.file,
        args.host,
        args.siteid
    )

    print(args)




class Config:
    def __init__(self, file, host, siteid):
        self.file = file
        self.host = host
        self.siteid = siteid


if __name__ == '__main__':
    main()