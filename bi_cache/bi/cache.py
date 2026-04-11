from pathlib import Path


def main():
    bdir = Path("./bdir")
    if not bdir.exists():
        print("bdir not exists, creating...")
        bdir.mkdir(exist_ok=True, parents=True)
        print("bdir created, please put your files in bdir and run again.")
        return [1]
    if not bdir.exists():
        bdir.mkdir(exist_ok=True, parents=True)
        return [1]
    rtn = []
    for file_dir in (p for p in bdir.rglob("entry.json")):
        rtn.append(file_dir.parent)
    if rtn == []:
        return [1]
    return rtn


if __name__ == "__main__":
    print(*main())
