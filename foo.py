from pathlib import Path

from pyssembler.gui.ide.explorer import ExplorerNode

def main():

    dir1 = Path('Pyssembler').resolve()

    dir2 = Path('Pyssembler/pyssembler/work').resolve()

    dir3 = Path('Pyssembler/').resolve()

    root = ExplorerNode(None, None)
    root.insert_path(dir3)

    for node in root:
        print(node.value)


def on_change(path: str):
    print(path)

if __name__ == '__main__':
    main()