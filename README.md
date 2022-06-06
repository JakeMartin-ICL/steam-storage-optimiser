# Steam Storage Optimiser
A tool to help users decide which games to uninstall to save space.

![image](https://user-images.githubusercontent.com/15602977/172073497-910b6b42-97b2-4735-9424-dd807d182f9d.png)

## Functionality
When run, the tool will find the size-on-disk of all ***installed*** games, then use the Steam Web API to match each game with your 'hours played' to calculate an 'hours played per GB'. As a measure of how efficiently a game has captured your interest in the past for its size, it's likely a reasonably good predictor for the future too. Using the cumulative columns, it's easy to find a selection of games for a given amount of space that might keep you most entertained, plus show how much time that selection has occupied so far.

## Limitations
The Steam Web API provides no method for finding the size-on-disk for a game. As such, the only reliable way of collecting this data is looking at the *actual* size of your current installations. This means that ***games that you own but don't currently have installed can't be shown in the list***. 

## Installation
Download the [latest release](https://github.com/JakeMartin-ICL/steam-storage-optimiser/releases/latest) and run - no installation necessary.
