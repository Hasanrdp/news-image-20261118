# Wednesday 18 November 2026: one front page, eight stories, one map

[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Hasanrdp/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Hasanrdp/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

An entry for the [make.fun news-image-20261118 bounty](https://make.fun/bounty/news-image-20261118):
sum up the world's news of Wednesday 18 November 2026 in one image.

## The image

`main.py` draws a one-page newspaper front page and writes it to
`/output/entry.png` (1024 x 1024, PNG, well under 1 MiB):

- **Masthead** naming the day: Wednesday 18 November 2026.
- **Lead story**: Trump lands in Manila for Quad talks, ahead of a meeting
  with Xi Jinping, as the ASEAN summit ends.
- **A world map** with eight numbered pins showing where the news happened.
- **Eight stories** from the day, keyed to the map: Modi's e-visa push at
  the ASEAN summit, Ukraine striking the Crimean bridge for a second day,
  Iran's drone attack on a US radar in Bahrain, Canada and China extending
  trade deals before APEC, Britain sanctioning settlement firms, Cyclone
  Akvan turning severe over the Bay of Bengal, aid chiefs warning the Gaza
  ceasefire may fail, and Nvidia's chief quitting in a spy scandal.
- **An "Also today" strip**: Dhoni retires from the IPL, SpaceX catches a
  Starship, the UN's October civilian death toll in Ukraine, the 2027
  Grammy nominations, Pope Leo hit by a rosary in Peru, and Baidu's chief
  warning of an AI bubble.

Every story is something that happened, or was first reported, on
18 November 2026, written as reported, without hype.

## How it is drawn

`main.py` is pure Python 3 standard library: a pixel canvas, a 5x7 bitmap
font, filled continent polygons for the map, and a small PNG encoder built
on `zlib`. No network, no clock, no randomness, no third-party packages,
so two runs write byte-identical files.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT. See [LICENSE](LICENSE).
