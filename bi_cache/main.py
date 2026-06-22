import asyncio
import json
import sys
from functools import wraps as warps
from pathlib import Path

from ffmpeg import Progress
from ffmpeg.asyncio import FFmpeg
from pymediainfo import MediaInfo
from tqdm.auto import tqdm

from .bi import cache

if not Path("./output").exists() or not Path("./output").is_dir():
    Path("./output").unlink(missing_ok=True)
    Path("./output").mkdir(exist_ok=True, parents=True)

output_dir = Path("./output")

sem = asyncio.Semaphore(2)  # 限制同时运行的协程数量


class VideoMaker:
    """通过 ffmpeg 将视频和音频合并为 mp4 文件"""

    count = 0

    def __init__(self, name, dir_way):
        """在初始化时，创建一个 FFmpeg 对象，并设置输入和输出文件路径"""
        VideoMaker.count += 1
        dirp = Path(dir_way)
        self.p_bar = tqdm(
            total=int(get_video_frame_count(dirp / "video.m4s")),
            desc=f"正在处理 {name[:9]}...",
            unit="帧",
            leave=False,
            file=sys.stderr,
            position=VideoMaker.count - 1,
            colour="blue",
        )
        self.name = name
        self.ffmpeg = (
            FFmpeg()
            .option("y")
            .input(str(dirp / "video.m4s"))
            .input(str(dirp / "audio.m4s"))
            .output(
                str(output_dir / f"{name}.mp4"),
                vcodec="copy",
                acodec="copy",
            )
        )

    async def make(self):
        """ "通过调用 FFmpeg 对象的 execute 方法来执行视频和音频的合并操作"""

        @self.ffmpeg.on("progress")
        def handle_progress(progress: Progress):
            self.p_bar.update(progress.frame - self.p_bar.n)
            self.p_bar.refresh()

        async with sem:
            await self.ffmpeg.execute()
            self.p_bar.close()
        return str(Path(output_dir / f"{self.name}.mp4").absolute())


def get_video_frame_count(video_path):
    media_info = MediaInfo.parse(video_path)
    for track in media_info.tracks:
        if track.track_type == "Video":
            print(track.frame_count)
            return track.frame_count
    return None


async def main(array):
    if array[0] == 1:
        print("main:\n  err:\n    没有找到缓存文件")
        return 1
    all_maker = []
    for file_dir in array:
        parent = Path(file_dir)
        entry = Path(file_dir / "entry.json")
        if not entry.exists():
            continue
        with entry.open("r", encoding="utf-8") as f:
            data = json.load(f)
        name = await safe_name(data["title"])
        print(
            f"main:\n  正在处理 {name}\n  dir:\n  >{entry.parent.absolute()}\n  output:\n  >{output_dir.absolute() / f'{name}.mp4'}"
        )
        parent_path = [p for p in parent.rglob("*") if p.is_dir()]
        maker = VideoMaker(name, parent_path[0].absolute())

        all_maker += (maker,)
    await asyncio.gather(*(maker.make() for maker in all_maker), return_exceptions=True)
    print(f"总共处理了 {VideoMaker.count} 个视频")


async def safe_name(name):
    if (output_dir / f"{name}.mp4").exists():
        print(f"safe_name say:\n  name:\n  >{name}\n  already exists, auto renaming...")
        i = 1
        while (output_dir / f"{name}_{i}.mp4").exists():
            print(
                f"safe_name say:\n  name:\n  >{name}_{i}\n  already exists, auto renaming..."
            )
            i += 1
        return f"{name}_{i}"
    else:
        return name


async def video_maker(name, dir_way):
    video_maker = VideoMaker(name, dir_way)
    await video_maker.make()
