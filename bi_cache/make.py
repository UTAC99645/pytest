import asyncio
from .main import main
from .bi.cache import main as cache


def work():
    asyncio.run(main(cache()))


if __name__ == "__main__":
    work()
