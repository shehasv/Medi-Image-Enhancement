from flask import *  
app = Flask(__name__)
app = Flask(__name__)
app.secret_key = "secret key"  
import os
#import magic
import urllib.request

from PIL import Image
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np
from PIL import Image
from PIL import ImageEnhance
from sklearn.cluster import KMeans
from joblib import dump
import sys
from PIL import Image,ImageFilter

ALLOWED_EXTENSIONS = set([  'jpeg','jpg' ])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			im = Image.open(file)
			pixel_np = np.asarray(im)
			# reshape array (remove rows and columns)
			image_height = im.height
			image_width = im.width
			pixel_np = np.reshape(pixel_np, (image_height * image_width, 3))

			flash('Image found with width: {}, height: {}'.format(image_width,image_height))
			# run k-means clustering on the pixel data
			num_of_centroids = 16 # a 4-bit image is represented by 2^4 colours
			num_of_runs = 10 # number of times to run the k-means algorithm before determining the best 	centroids
			max_iterations = 300 # number of iterations before k-means comes to an end for a single run
			verbosity = 0 # show what's going on when the algorithm is running

			# initiate a kmeans object
			compressor = KMeans(n_clusters=num_of_centroids, n_init=num_of_runs,max_iter=max_iterations, verbose=verbosity)
	
			flash('Runnign K-means')
			# run k-means clustering
			compressor.fit(pixel_np)

			# save the fitted model
			dump(compressor, "compressor.joblib")

			# create an array replacing each pixel label with its corresponding cluster centroid
			pixel_centroid = np.array([list(compressor.cluster_centers_[label]) for label in compressor.labels_])

			# convert the array to an unsigned integer type
			pixel_centroid = pixel_centroid.astype("uint8")
			# reshape this array according to the height and width of our image
			pixel_centroids_reshaped = np.reshape(pixel_centroid, (image_height, image_width, 3), "C")


			# create the compressed image
			compressed_im = Image.fromarray(pixel_centroids_reshaped)

			#image enhancement starts 
			enh_bri = ImageEnhance.Brightness(compressed_im)
			brightness = 1.0
			image_brightened = enh_bri.enhance(brightness)


			enh_col = ImageEnhance.Color(image_brightened)
			color = 1.0
			image_colored = enh_col.enhance(color)


			enh_con = ImageEnhance.Contrast(image_colored)
			contrast = 1.5
			image_contrasted = enh_con.enhance(contrast)


			enh_sha = ImageEnhance.Sharpness(image_contrasted)
			sharpness = 1.5
			image_sharped = enh_sha.enhance(sharpness)

			flash('Image Processing Completed Successfully !')	
			image_sharped.save("/home/shehas/testing/out.jpg")
			flash('File Downloaded Succesfully ')
			return redirect('/')
		else:
			flash('Allowed file type is jpeg')
			return redirect(request.url)

if __name__ == "__main__":
    app.run()
