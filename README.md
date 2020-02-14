<a href="http://dataanalyticsandml.xyz/">
<img src="https://i.imgur.com/LMrskDl.png" width=100 align=center>
</a>

# CommenTube
## Helping Brands Find the Right YouTuber

- [Introduction](#Introduction)

- [Overview of Website](#Overview-of-Website)
  * [Website Link](#Website-Link)

- [Repository Structure](#heading-2)
  * [CommenTube_AWS](#CommenTube_AWS)
  * [data](#data)
  * [notebooks](#notebooks)
  * [scripts](#scripts)

<!-- toc -->
## Introduction
YouTube is the 2nd most visited website on the internet and 73% of US adults have stated to using the website on a Pew Reearch survey, larger than all other social media platforms [(source)](https://www.pewresearch.org/fact-tank/2019/04/10/share-of-u-s-adults-using-social-media-including-facebook-is-mostly-unchanged-since-2018/).

Sponsoring YouTube channels is one way for companies to tap into this large audience that can actually be targeted quite precisely - individual tastes vary and there are many channels with very specific audiences.

However, with thousands of channels with 1 million or more subscribers, it can be difficult to choose the right one to sponsor. Age, gender and geographic demographic information is available to the channel owners but not to outside marketers. Further, of the available services, none offer a glimpse into __thoughts, interests and opinions of the *most engaged users*__ of these audiences: the commentors.

## Overview of Website
CommenTube offers channel recommendations based on what these commentors are saying:

<img src="https://i.imgur.com/jZ3uVv0.png" width=900 align=center> 

Simply type in your a key word or even a whole sentence and CommenTube will reveal the channels with the greatest proportion of relevant comments related to your search term. 

<img src="https://imgur.com/HT2DIOx.png" width=900 align=center> 

Switch tabs to see what the most relevant comments are.

<img src="https://imgur.com/h9JNpNU.png" width=900 align=center> 

### Website Link
Visit the website [here](http://dataanalyticsandml.xyz/)

## Repository Structure
This repository contains the files on the AWS EC2 instance used to host the site and data exploration / production steps used to create the final product.

### CommenTube_AWS
The python files used on the AWS EC2 instance. 
- comm_chan_result.py: the workhorse of the website making calls to the PostgreSQL database for relevant comment and channel data based on the users input text.
- server.py: runs the Flask app and interfaces between the HTML file and comm_chan_result.py file when a user makes a submission of text
- 

### data
On my local machine contains the data that was gathered for this project. As the size of all files exceeds 2 GB this has been omitted from upload to GitHub

### notebooks
A range of Jupyter notebooks that tracks my journey including:
- gathering the data and formatting / turning it into .csv files, 
- data exploration of comments 
- processing/cleaning for NLP tasks
- searching for topics within the comments
- testing embeddings and search
- validation

### scripts
A collection of scripts containing various python functions that were used for:
- YouTube comment, video, and channel data collection
- Creating word2vec embeddings
- Data visualization

