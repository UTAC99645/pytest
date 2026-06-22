from pathlib import Path


def main():
    bdir = Path("./input")
    if not bdir.exists() or not bdir.is_dir():
        print("input not exists, creating...")
        bdir.unlink(missing_ok=True)
        bdir.mkdir(exist_ok=True, parents=True)
        print("input created, please put your files in bdir and run again.")
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
