from flask import Flask, render_template, request

import numpy as np
import pandas as pd
import comm_chan_result as ccr

# Create the application object
app = Flask(__name__)

@app.route('/',methods=["GET","POST"]) #we are now using these methods to get user input
def home_page():
	return render_template('index.html')  # render a template

@app.route('/output')
def recommendation_output():
	# Pull input
    keyword_input = request.args.get('keyword')
    sim_thresh_input = request.args.get('sim_thresh')
    
    if sim_thresh_input == "":
        sim_thresh_input = "50"
	
   	# Case if empty
    if keyword_input == "":
        return render_template("index.html",my_form_result="Empty")
    else:
        
        chan_dict_list, comm_dict_list = ccr.get_comment_channel_results(
            keyword_input, 
            int(sim_thresh_input))
		
        return render_template("index.html",chan_dicts=chan_dict_list,comm_dicts=comm_dict_list,my_form_result="NotEmpty")



# start the server with the 'run()' method
if __name__ == "__main__":
	app.run(debug=True) #will run locally http://127.0.0.1:5000/






