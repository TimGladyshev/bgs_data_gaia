#!/bin/bash

factions=("terrans" "lantids" "hadsch-hallas" "ivits" "baltaks" "geodens" "xenos" "gleens" "ambas" "taklons" "bescods" "firaks" "itars" "nevlas")
players=(2 3 4)
path=$1
num_players=$2

for faction in ${factions[@]}; do
	scp -i ~/.ssh/google_compute_engine /home/tim/Documents/gaia/plots/${path}${faction}.html  timothygladyshev@34.123.233.225:/home/timothygladyshev/gaia_stats/${num_players}p/${path}${faction}.html
done
