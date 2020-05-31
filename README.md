# APOLLO-1
This project is one of the many APOLLO projects to be launched in future.

## Detect Toxicity in Online YouTube Comments
Project to check the online toxicity (hate speech, swearing) in YouTube video comments.

## How to run

1. Clone the repo: ``` git clone https://github.com/kumar-shridhar/APOLLO-1.git``` 
2. Set python export path: ```export PYTHONPATH="${PYTHONPATH}:/path/to/your/cloned_repo/```
2. Download saved model from [here](https://drive.google.com/file/d/1RNd4L_zGVrFF_Cl-6KfoHIInMO-5A0e3/view?usp=sharing)
3. Unzip the model and save in ```APOLLO-1/apollo/inference``` folder.
4. Install all the requirements by command: ```pip install -r requirements.txt```
5. Change the number of comments to be scraped in the ```config.py``` file at ```APOLLO-1/apollo/Scraper/```. Default value is set to 50.
5. Run command: ``` python apollo/Frontend/app.py```
6. Go to ```localhost:8082``` and provide the YouTube URL. The results will be displayed in the pie chart.


### Contact
Feel free to contact the authors in case of any issues. 
* [Naveed Akram](https://github.com/n-akram)
* [Ritu Yadav](https://github.com/RituYadav92)
* [Venkatesh Iyer](https://github.com/venkyiyer)
* [Sadique Adnan Siddiqui](https://github.com/sadique-adnan)
* [Ashutosh Mishra](https://github.com/ashutoshmishra1014)
* [Kumar Shridhar](https://kumar-shridhar.github.io/)
