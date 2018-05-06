kono data
===========
a simple label-it-yourself app - for more structure in your data.

## Why do I need it?
Kono data provides an easy way to label an unstructured image dataset.

## How can I use it?
You can use the hosted version (available soon) or 
install it on your own server, see <b>Installation</b>.

You provide Kono Data with a path to your dataset (currently only AWS S3 is supported)
and possible labels for each datapoint.

## How does the processing flow look like?
On the left side you see an image and on the right its possible labels.
Click the checkbox or type the number and a label is selected.
One or all labels can be selected. If you click _Save_ or hit enter the labeling for this 
image is saved and the next image in the dataset is loaded.

<img src="docs/img/label_hotdog.png" alt="" style="height: 200px;" />

## How can I see the labeling progress of a dataset?
## How can I export a dataset?
<img src="docs/img/export_hotdog.png" alt="" style="height: 200px;" />

## Installation
This app is written in Python 3 and based on [Django](https://www.djangoproject.com/).
Python requirements are listed in the ```requirements.txt``` and can be 
installed with ```pip install --upgrade -r requirements.txt```. 

## Future features
These are some ideas I've been thinking about:
1. Add adapters for other content types: video, sound, gif
2. Add structure to labels: binary, multi-label (can include pairs of binary labels)
3. Add dockerfile to be on the hypetrain
4. Train and export deep-learning model

## Awesome, but why the weird name?
For no particular reason (knowledge-annotate-data) this project is named after 
[Hyōichi Kōno](https://en.wikipedia.org/wiki/Hy%C5%8Dichi_K%C5%8Dno), a Japanese adventurer,
best known for circling Japan on bicycle.

