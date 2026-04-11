from bi_cache import bili_cache_make
import asyncio


def main():
    select = input(
        "请选择要执行的功能：\n1. 生成Bili缓存视频\n2. 其他功能（未实现）\n请输入数字选择："
    )
    choice = int(select)
    match choice:
        case 1:
            print("正在生成Bili缓存视频...")
            bili_cache_make()

        case _:
            print("无效的选择，请输入数字1")


if __name__ == "__main__":
    main()
