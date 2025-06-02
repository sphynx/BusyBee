# Installation

1. Create a virtual env to install Python packages, for example:

```
python -m venv .venv
```

NB: on Ubuntu it may ask you to install venv package separately, like this:

```
sudo apt install python3.12-venv
```

2. Activate this environment:

```
source .venv/bin/activate
```

3. Install dependencies (checked that it works on Python 3.12 and 3.13):

```
pip install -r requirements.txt
```

4. Create .env file with your tokens and other settings:

```
DISCORD_TOKEN=MDM9xblabla
LICHESS_TOKEN=l_here_goes_lichess_token
SLOW_GAMES_THREAD_ID=133844255959
```

5. Run the bot:

```
python main.py
```