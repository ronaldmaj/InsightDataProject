import numpy as np

all_mat = np.load('comms_mat_all.npy')

array_list = []

for i in range(0,600000,100000):
	array_list.append(all_mat[i:i+100000])
	
array_list.append(all_mat[i+100000:])

for idx,array in enumerate(array_list):
	np.save('Part_'+str(idx)+'.npy',array)