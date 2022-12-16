# Steam Storage Optimiser
A tool to help users decide which games to install or uninstall to save space.

![image](https://user-images.githubusercontent.com/15602977/172073497-910b6b42-97b2-4735-9424-dd807d182f9d.png)

## Installation
### Windows
Download the [latest release](https://github.com/JakeMartin-ICL/steam-storage-optimiser/releases/latest) and run - no installation necessary. Windows will likely prevent the program running from an unknown publisher - choose 'Run anyway'.

### Mac and Linux
Download the [latest release](https://github.com/JakeMartin-ICL/steam-storage-optimiser/releases/latest) and make the file executable (`chmod +x steamStorageOptimiser-[platform]`. See guide if unsure: [Mac](https://support.apple.com/en-gb/guide/terminal/apdd100908f-06b3-4e63-8a87-32e71241bab4/mac), [Linux](https://linuxhint.com/make-file-executable-linux/) ). 

## Functionality
When run, the tool will find the size-on-disk of all installed games, then use the Steam Web API to match each game with your 'hours played' to calculate an 'hours played per GB'. As a measure of how efficiently a game has captured your interest in the past for its size, it's likely a reasonably good predictor for the future too. Using the cumulative columns, it's easy to find a selection of games for a given amount of space that might keep you most entertained, plus show how much time that selection has occupied so far.

## Limitations
The Steam Web API provides no method for finding the size-on-disk for a game. The optimiser maintains a shared database to crowdsource this data so uninstalled games that you can be displayed too, as long as they've been seen installed before by anyone using this tool. If there's a game you own which hasn't been matched that you'd like to see your hours/GB for, you can temporarily download it then re-run the optimiser - it'll be added to the database and will help others in future too!

## Privacy
The crowdsourced database contains only average file sizes. When using this software, if your installation size is different to the average file size or the game has not been registered in the database, **only your installation size is uploaded** and nothing more.

## Troubleshooting
Windows Security occasionally mislabels the executable file as a threat. If this occurs, you can either 'allow' the file in Windows Security (sometimes found in 'Protection history') or, if you prefer to inspect and run the Python file directly, download the source code for the latest release. Note that a Python 3 installation is required, in addition to all packages listed in `requirements.txt`.


