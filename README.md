[![news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/meongs123/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/meongs123/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

# The World in One Page — Wednesday 18 November 2026

One image that sums up the world's news of Wednesday 18 November 2026, as an
editorial front page: masthead with the date and story count, a numbered
world map of the six leads, six lead cards with flat programmatic icons, an
"ALSO ON THIS PAGE" list of 24 more stories, a "BY THE NUMBERS" strip, and
a source line. 30 stories, 6 continents.

## How it is made

`compose.py` draws the whole page with PIL (DejaVu fonts, system install):
no photos, no AI images, no network — every icon, map shape and letter is
drawn here from code, so the output is fully deterministic (identical bytes
on every run). `main.py` (standard library only) copies the committed
`entry.png` to `/output/entry.png` for the grader.

```sh
python3 compose.py        # writes entry.png (1024x1024 PNG, <1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Stories (all verified against real reporting)

Leads: the U.S. and Iran trade fire in the Gulf — U.S. jets hit an IRGC
missile site on Qeshm after Iran's third attack on Bahrain in five days;
APEC opens in Shenzhen with a first-ever Trump–Xi–Putin three-way summit
on Thursday; Nvidia beats with $115.8B revenue, up 103%, and the board
says it will not reinstate Huang; the Knesset elects Kahana speaker 66-52,
a blow to Netanyahu; the U.S. loses its measles-free status after 26
years, with 5,412 cases in 2026; COP31 concedes the 1.5°C Paris target
will be overshot. Plus 24 more in the ALSO list, from the Deutsche Bank
15m-document leak and Mongolia's president resigning to the Anthropic IPO
pricing and Brent at $92.76. Disputed claims are hedged ("Iran says",
"Russia says"). Two claims seen in rival entries were left out because
they could not be verified from a real source.

## License

MIT. All drawings and text are original work.
