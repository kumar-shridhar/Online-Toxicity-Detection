# APOLLO-1
This project is one of the many APOLLO projects to be launched in future.

## Detect Toxicity in Online YouTube Comments
Project to check the online toxicity (hate speech, swearing) in YouTube videos comments.

## How to run

1. Clone the repo: ``` git clone https://github.com/kumar-shridhar/APOLLO-1.git``` 
2. Download saved model from [here](https://drive.google.com/open?id=1fXsd0hyf84AB2QRRnBgsMXeH_tEplHxC)
3. Unzip the model and save in ```APOLLO-1/apollo/inference``` folder.
4. ```pip install -r requirements.txt```
5. Change the number of comments to be scraped in the ```config.py``` file. Default value is set to 50.
5. ``` python apollo/app.py```
6. Go to ```localhost:8082``` and provide the YouTube URL. The results will be displayed in the pie chart.


### Contact
Feel free to contact the authors in case of any issues. 
* Naveed Akram
* Ritu Yadav
* Venkatesh Iyer 
* Sadique Adnan Siddiqui
* Ashutosh Mishra
* [Kumar Shridhar](shridhar.stark@gmail.com)
