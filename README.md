My first real programm as a python beginner and its may be outdated or doesnt work because... well im lazy and really bad at codeing
also i indeed do not have any understanding of git or/and .gitignore and i just used something my ide recommended im sorry if this is bad

## Setup

Use Python 3 and install the input-control dependency:

```sh
python -m pip install -r requirements.txt
python bot.py
```

The launcher lists the scripts in `scripts/`. Select a coordinate step, click
**Capture location**, move the cursor to the desired screen position, and press
**Ctrl+K**. The captured position is saved in the ignored local `settings.json`
file and used by `infernalbot.py`; locations not yet captured keep their
original defaults. Capture coordinates with the game at the same resolution
and display scaling you intend to use for automation.
