import glob
import os.path
import random
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile

BOTTLENECK_TENSOR_SIZE=2048

BOTTLENECK_TENSOR_NAME='pool_3/_reshape:0'

JPEG_DATA_TENSOR_NAME='DecodeJpeg/contents:0'

MODEL_DIR='/home/u784799i/inception'

MODEL_FILE='tensorflow_inception_graph.pb'

CACHE_DIR='/tmp/bottleneck'

INPUT_DATA='/home/u784799i/flower_phtots'

VALIDATION_PERCENTAGE=10

TEST_PERCENTAGE=10

LEARNING_RATE=0.01
STEPS=1000
BATCH=100

def create_image_lists(testing_percentage,validation_percentage):
	result={}
	sub_dirs=[x[0] for x in os.walk(INPUT_DATA)]
	is_root_dir=True
	for sub_dir in sub_dirs:
		if is_root_dir:
			is_root_dir=False
			continue
		extensions=['jpg','jpeg','JPG','JPEG']
		file_list=[]
		dir_name=os.path.basename(sub_dir)
		for extension in extensions:
			file_glob=os.path.jion(INPUT_DATA,dir_name,'*.'+extension)
			file_list.extend(glob.glob(file_glob))
		if not file_list: continue

	label_name=dir_name.lower()
	training_images=[]
	testing_images=[]
	validation_images=[]
	for file_name in file_list:
		base_name=os.path.basename(file_name)
		change=np.random.randint(100)
		if change<validation_percentage:
			validation_images.append(base_name)
		elif chance<(testing_percentage + validation_percentage):
			testing_images.append(base_name)
		else:
			training_images.append(base_name)

		result[label_name]={'dir':dir_name,'training':training_images,'testing':testing_images,
					'validation':validation_images,}
	return result

def get_image_path(image_lists,image_dir,label_name,index,category):
	label_lists=image_lists[label_name]
	category_list=label_lists[category]
	mod_index=index%len(category_list)
	base_name=category_list[mod_index]
	sub_dir=label_lists['dir']

	full_path=os.path.join(image_dir,sub_dir,base_name)
	return full_path

def get_bottleneck_path(image_lists,label_name,index,category):
	return get_image_path(image_lists,CACHE_DIR,label_name,index,category)+'.txt'

def run_bottleneck_on_image(sess,image_data,image_data_tensor,bottleneck_ tensor):
	bottleneck_balues=sess.run(bottleneck_tensor,{image_data_tensor: image_data})
	bottleneck_values=np.squeeze(bottleneck_values)
	return bottleneck_values

def get_or_create_bottleneck(sess,image_lists,label_name,index,category,jpeg_data_tensor,
				bottleneck_tensor):
	label_lists=image_lists[label_name]
	sub_dir=label_liasts['dir']
	sub_dir_path=os.path.join(CACHE_DIR,sub_dir)
	if not os.path.exists(sub_dir_path): os.makedirs(sub_dir_path)
	bottleneck_path=get_bottleneck_path(image_lists,label_name,index,category)
	
	if not os.path.exists(botteneck_path):
		image_path=get_image_path(image_lists,INPUT_DATA,label_name,index,category)
		image_data=gfile.FastGFile(image_path,'rb').read()
		bottleneck_values=run_bottleneck_on_image(sess,image_data,jpeg_data_tensor,
								bottleneck_tensor)
		bottleneck_string=','.jion(str(x) for x in bottleneck_values)
		with open(bottleneck_path,'w') as bottleneck_file:
			bottleneck_file.write(bottleneck_string)
	else:
		with open(bottleneck_path,'r') as bottleneck_file:
			bottleneck_string=bottleneck_file.read()
		bottleneck_values=[float(x) for x in bottleneck_string.split(',')]
	return bottleneck_values

def get_random_cached_bottlenecks(sess,n_classes,image_lists,how_many,category,jpeg_data_tensor,
					bottleneck_tensor):
	bottlenecks=[]
	ground_truths=[]
	for _ in range(how_many):
		label_index=random.randrange(n_classes)
		label_name=list(image_lists.keys())[label_index]
		image_index=random.randrange(65536)
		bottleneck=get_or_create_bottleneck(sess,image_lists,label_name,image_index,category,
							jpeg_data_tensor,bottleneck_tensor)
		ground_truth=np.zeros(n_classes,dtype=np.float32)
		ground_truth[label_index]=1.0
		bottlenecks.append(bottleneck)	
		ground_truths.append(ground_truth)

	return bottlenecks, ground_truths


