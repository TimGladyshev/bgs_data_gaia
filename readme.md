# Gaia Stats

Set of Jupyter Notebooks for scraping and analysing Gaia Project data from [boardgamers.space](https://www.boardgamers.space/boardgame/gaia-project) 

View or download auto-updating results [here](https://timgladyshev.com/gaia_stats/)

## Installation
```bash
pip install -r requirements.txt
```

## Notebooks

#### fetch_names
Uses Selenium to scrape names for all completed games.

#### fetch_jsons
Fetches jsons from the game data [api](https://www.boardgamers.space/api/game/Modern-riddle-1723) and stores locally as raw json.

#### parse_jsons
Parses json to pandas df and saves as pickle or csv.

#### others:
Creates plotly figures. 

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)