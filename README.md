[//]: # (Image References)

[image1]: ./images/sample_dog_output.png "Sample Output"


## Project Overview

Given an image of a food dish, algorithm will identify an estimate of the dish nutrition class.

![Sample Output][image1]


## Project Instructions

### Instructions

1. Clone the repository and navigate to the downloaded folder.

	```
		git clone https://github.com/aleksas/food_nutrition_classifier.git
		cd food_nutrition_classifier
	```
2. Download the meta-data and image database and place those in the repo, at location `path/to/food_nutrition_classifier/`.
3. Install [Miniconda](https://conda.io/miniconda.html) and obtain the necessary Python packages, and switch Keras backend to Tensorflow as shown below.  

	For __Mac/OSX__:
	```
		conda env create -f requirements/recipes-mac.yml
		source activate recipes
		KERAS_BACKEND=tensorflow python -c "from keras import backend"
	```

	For __Linux__:
	```
		conda env create -f requirements/recipes-linux.yml
		source activate recipes
		KERAS_BACKEND=tensorflow python -c "from keras import backend"
	```

	For __Windows__:
	```
		conda env create -f requirements/recipes-windows.yml
		activate recipes
		set KERAS_BACKEND=tensorflow
		python -c "from keras import backend"
	```
6. Open the notebook and follow the instructions.

	```
		jupyter notebook recipes.ipynb
	```
