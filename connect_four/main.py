from sys import argv


def main():
    if len(argv) != 2 or argv[1] not in ["--cli", "--gui"]:
        print('Usage: "python3 main.py --cli" or "python3 main.py --gui"')
    elif argv[1] == "--cli":
        import cli
        cli.main()
    else:
        import gui
        gui.main()

if __name__ == "__main__":
    main()