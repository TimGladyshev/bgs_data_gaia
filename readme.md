# Gaia Stats

![screenshot](https://user-images.githubusercontent.com/54454071/191138235-c8122774-90af-40db-a3ca-365aa44c5a8d.png)

Statistical analysis and texting service for a boardgame called Gaia Project. 

Gaia Project is a deterministic perfect-information multiplayer boardgame with a large statespace created by Jens Drögemüller and Helge Ostertag. 
This competitive euro-style game focusing on economy building, competition for actions/locations, 
and victory point accumulation is in the early days of game theory development. 
This project aims to help (especially new) players analyze the validity of various approaches. 

This repo contains a set of Jupyter Notebooks presenting the code used to create [gpstats.dev](https://timgladyshev.com/gaia_stats/). These notebooks:
1. Scrape and parse Gaia Project game data from [boardgamers.space](https://www.boardgamers.space/boardgame/gaia-project)
2. Create interactive plots to show performance of various strategies
3. Send SMS turn reminder messages to users on their turn

[Game Rules](https://images.zmangames.com/filer_public/ce/89/ce890bfd-227e-4249-a52a-976bc5f20d19/en_gaia_rulebook_lo.pdf)

[Active Discord Community](https://discord.gg/KwFHt2DQ)

## Installation
```bash
pip install -r requirements.txt
```

## Notebooks

#### <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/texting_service.ipynb"><img src="https://img.shields.io/badge/nbviewer-texting__service-informational"/></a>
Working example of a simple Flask app that allows registration features, and a threaded texting service.
<br></br>
#### <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/fetch_names.ipynb"><img src="https://img.shields.io/badge/nbviewer-fetch__names-informational"/></a>
Uses Selenium to scrape names for all completed games. Names are used to create links to the game data api.
<br></br>
#### <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/fetch_jsons.ipynb"><img src="https://img.shields.io/badge/nbviewer-fetch__jsons-informational"/></a>
Fetches jsons from the game data [api](https://www.boardgamers.space/api/game/Modern-riddle-1723) and stores locally as raw json.
<br></br>
#### <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/parse_jsons.ipynb"><img src="https://img.shields.io/badge/nbviewer-parse__jsons-informational"/></a>
Parses json game data to pandas df and saves as pickle or csv.
<br></br>
### others:
Create the plotly figures for the site. 
* <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/advanced_techs.ipynb"><img src="https://img.shields.io/badge/nbviewer-advanced__techs-informational"/></a> : advanced technology tile frequency, impact on win probability/score
* <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/basic_tech.ipynb"><img src="https://img.shields.io/badge/nbviewer-basic__tech-informational"/></a> : standard technology tile tile frequency, impact on win probability/score
* <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/final_scorings_deltas.ipynb"><img src="https://img.shields.io/badge/nbviewer-final__scoring__deltas-informational"/></a> : final scoring tile impact on win probability/score
* <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/r1_strucs.ipynb"><img src="https://img.shields.io/badge/nbviewer-r1__structs-informational"/></a> : round one structures frequency and impact on score
* <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/round_scoring.ipynb"><img src="https://img.shields.io/badge/nbviewer-round__scoring-informational"/></a> : round scoring impact on win probability/score
* <a href="https://nbviewer.org/github/TimGladyshev/bgs_data_gaia/blob/master/scoring_methods.ipynb"><img src="https://img.shields.io/badge/nbviewer-scoring__methods-informational"/></a> : score distribution over possible sources and resulting position


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. I will add any new plots to the site.

## License
[MIT](https://choosealicense.com/licenses/mit/)