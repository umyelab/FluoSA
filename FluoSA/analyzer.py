'''
Copyright (C)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext. 

For license issues, please contact:

Dr. Bing Ye
Life Sciences Institute
University of Michigan
210 Washtenaw Avenue, Room 5403
Ann Arbor, MI 48109-2216
USA

Email: bingye@umich.edu
'''




import os
import cv2
import json
import torch
import datetime
import numpy as np
from scipy.spatial import distance
import pandas as pd
from readlif.reader import LifFile
from detectron2.config import get_cfg
from detectron2.modeling import build_model
from detectron2.checkpoint import DetectionCheckpointer



class AnalyzeCalciumSignal():

	def __init__(self,path_to_lif,results_path,stim_t,duration):

		self.detector=None
		self.neuro_mapping=None
		self.path_to_lif=path_to_lif
		self.results_path=os.path.join(results_path,os.path.splitext(os.path.basename(self.path_to_lif))[0])
		os.makedirs(self.results_path,exist_ok=True)
		self.neuro_number=None
		self.neuro_kinds=None  # the catgories of neural structures to be analyzed
		self.stim_t=stim_t  # the frame number when stimulation is on 
		lifdata=LifFile(self.path_to_lif)
		file=[i for i in lifdata.get_iter_image()][0]
		self.full_duration=len([i for i in file.get_iter_t(c=0,z=0)])-1
		self.duration=duration # the duration (in frames) for example generation / analysis, 0: use entire duration
		if self.duration<=0:
			self.duration=self.full_duration
		self.main_channel=0 # main_channel: the channel for frames to analyze
		self.to_deregister={}
		self.register_counts={}
		self.neuro_contours={}
		self.neuro_centers={}
		self.neuro_existingcenters={}
		self.neuro_Fmeans={}
		self.all_parameters={}


	def prepare_analysis(self,path_to_detector,neuro_number,neuro_kinds):
		
		print('Preparation started...')
		print(datetime.datetime.now())

		config=os.path.join(path_to_detector,'config.yaml')
		detector=os.path.join(path_to_detector,'model_final.pth')
		neuromapping=os.path.join(path_to_detector,'model_parameters.txt')
		with open(neuromapping) as f:
			model_parameters=f.read()
		self.neuro_mapping=json.loads(model_parameters)['neuro_mapping']
		neuro_names=json.loads(model_parameters)['neuro_names']
		dt_infersize=int(json.loads(model_parameters)['inferencing_framesize'])
		print('The total categories of neural structures in this Detector: '+str(neuro_names))
		print('The neural structures of interest in this Detector: '+str(neuro_kinds))
		print('The inferencing framesize of this Detector: '+str(dt_infersize))
		cfg=get_cfg()
		cfg.merge_from_file(config)
		cfg.MODEL.DEVICE='cuda' if torch.cuda.is_available() else 'cpu'
		self.detector=build_model(cfg)
		DetectionCheckpointer(self.detector).load(detector)
		self.detector.eval()

		self.neuro_number=neuro_number
		self.neuro_kinds=neuro_kinds

		total_number=0

		for neuro_name in self.neuro_kinds:

			total_number+=self.neuro_number[neuro_name]
			self.all_parameters[neuro_name]={}
			for parameter_name in ['F0','dF/F0','Fmax','Stim_t']:
				self.all_parameters[neuro_name][parameter_name]={}
			self.to_deregister[neuro_name]={}
			self.register_counts[neuro_name]={}
			self.neuro_contours[neuro_name]={}
			self.neuro_centers[neuro_name]={}
			self.neuro_existingcenters[neuro_name]={}
			self.neuro_Fmeans[neuro_name]={}

			for i in range(self.neuro_number[neuro_name]):
				self.to_deregister[neuro_name][i]=0
				self.register_counts[neuro_name][i]=None
				self.neuro_contours[neuro_name][i]=[None]*self.duration
				self.neuro_centers[neuro_name][i]=[None]*self.duration
				self.neuro_existingcenters[neuro_name][i]=(-10000,-10000)
				self.neuro_Fmeans[neuro_name][i]=[0.0]*self.duration

		print('Preparation completed!')


	def track_neuro(self,frame_count,neuro_name,contours,centers,Fmeans):

		unused_existing_indices=list(self.neuro_existingcenters[neuro_name])
		existing_centers=list(self.neuro_existingcenters[neuro_name].values())
		unused_new_indices=list(range(len(centers)))
		dt_flattened=distance.cdist(existing_centers,centers).flatten()
		dt_sort_index=dt_flattened.argsort()
		length=len(centers)

		for idx in dt_sort_index:
			index_in_existing=int(idx/length)
			index_in_new=int(idx%length)
			if index_in_existing in unused_existing_indices:
				if index_in_new in unused_new_indices:
					unused_existing_indices.remove(index_in_existing)
					unused_new_indices.remove(index_in_new)
					if self.register_counts[neuro_name][index_in_existing] is None:
						self.register_counts[neuro_name][index_in_existing]=frame_count
					self.to_deregister[neuro_name][index_in_existing]=0
					self.neuro_contours[neuro_name][index_in_existing][frame_count]=contours[index_in_new]
					center=centers[index_in_new]
					self.neuro_centers[neuro_name][index_in_existing][frame_count]=center
					self.neuro_existingcenters[neuro_name][index_in_existing]=center
					self.neuro_Fmeans[neuro_name][index_in_existing][frame_count]=Fmeans[index_in_new]

		if len(unused_existing_indices)>0:
			for i in unused_existing_indices:
				if self.to_deregister[neuro_name][i]<5:
					self.to_deregister[neuro_name][i]+=1
				else:
					self.neuro_existingcenters[neuro_name][i]=(-10000,-10000)


	def detect_neuro(self,frames,images,batch_size,frame_count):

		# frames: frames averageprojected along z, with pixel values in float
		# images: unit8 format of frames averageprojected along z, for Detectors to detect neural structures

		tensor_images=[torch.as_tensor(image.astype("float32").transpose(2,0,1)) for image in images]
		inputs=[{"image":tensor_image} for tensor_image in tensor_images]

		with torch.no_grad():
			outputs=self.detector(inputs)

		for batch_count,output in enumerate(outputs):

			image=images[batch_count]
			frame=frames[batch_count]
			instances=outputs[batch_count]['instances'].to('cpu')
			masks=instances.pred_masks.numpy().astype(np.uint8)
			classes=instances.pred_classes.numpy()
			scores=instances.scores.numpy()

			if len(masks)>0:

				mask_area=np.sum(np.array(masks),axis=(1,2))
				exclusion_mask=np.zeros(len(masks),dtype=bool)
				exclusion_mask[np.where((np.sum(np.logical_and(masks[:,None],masks),axis=(2,3))/mask_area[:,None]>0.8) & (mask_area[:,None]<mask_area[None,:]))[0]]=True
				masks=[m for m,exclude in zip(masks,exclusion_mask) if not exclude]
				classes=[c for c,exclude in zip(classes,exclusion_mask) if not exclude]
				classes=[self.neuro_mapping[str(x)] for x in classes]
				scores=[s for s,exclude in zip(scores,exclusion_mask) if not exclude]

				for neuro_name in self.neuro_kinds:

					contours=[]
					centers=[]
					goodcontours=[]
					goodmasks=[]
					Fmeans=[]

					neuro_number=int(self.neuro_number[neuro_name])
					neuro_masks=[masks[a] for a,name in enumerate(classes) if name==neuro_name]
					neuro_scores=[scores[a] for a,name in enumerate(classes) if name==neuro_name]

					if len(neuro_masks)>0:

						if len(neuro_scores)>neuro_number*2:
							sorted_scores_indices=np.argsort(neuro_scores)[-int(neuro_number*2):]
							neuro_masks=[neuro_masks[x] for x in sorted_scores_indices]

						for mask in neuro_masks:
							mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
							goodmasks.append(mask)
							cnts,_=cv2.findContours((mask*255).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
							goodcontours.append(sorted(cnts,key=cv2.contourArea,reverse=True)[0])

						areas=[np.sum(np.array(m),axis=(0,1)) for m in goodmasks]
						sorted_area_indices=np.argsort(np.array(areas))[-neuro_number:]
						areas_sorted=sorted(areas)

						for x in sorted_area_indices:
							mask=goodmasks[x]
							area=areas_sorted[x]
							cnt=goodcontours[x]
							contours.append(cnt)
							centers.append((int(cv2.moments(cnt)['m10']/cv2.moments(cnt)['m00']),int(cv2.moments(cnt)['m01']/cv2.moments(cnt)['m00'])))  

							if area>0:
								Fmeans.append(np.sum(frame*mask)/area)
							else:
								Fmeans.append(0)

						self.track_neuro(frame_count+1-batch_size+batch_count,neuro_name,contours,centers,Fmeans)


	def acquire_information(self,batch_size=1,autofind_t=False,stimulation_channel=0,main_channel=0):

		# autofind_t: automatically find the frame number of stimulation, False: use stim_t
		# stimulation_channel: the channel for record stimulation onset

		print('Acquiring information in each frame...')
		print(datetime.datetime.now())

		self.main_channel=main_channel

		initial_frame=None
		stimulation_checked=False
		main_frames=[]
		images=[]
		batch_count=frame_count=0

		lifdata=LifFile(self.path_to_lif)
		file=[i for i in lifdata.get_iter_image()][0]
		channels=[i for i in file.get_iter_c(t=0,z=0)]

		while True:

			if frame_count<self.duration:

				frame_project=[np.array(i) for i in file.get_iter_z(t=frame_count,c=self.main_channel)]
				#frame_project=np.array(frame_project).sum(0)/len(frame_project)
				frame_project=np.array(frame_project).max(0)

				if autofind_t is True:

					frame_project_stim=[np.array(i) for i in file.get_iter_z(t=frame_count,c=stimulation_channel)]
					frame_project_stim=np.array(frame_project_stim).sum(0)/len(frame_project_stim)

					if initial_frame is None:
						initial_frame=frame_project_stim

					if stimulation_checked is False:
						if np.mean(frame_project_stim)>1.2*np.mean(initial_frame):
							self.stim_t=frame_count
							stimulation_checked=True
							print('Stimulation onset: at frame '+str(self.stim_t)+'.')

				main_frames.append(frame_project)
				frame_project[frame_project>255]=255
				frame_project=cv2.cvtColor(np.uint8(frame_project),cv2.COLOR_GRAY2BGR)
				images.append(frame_project)

				batch_count+=1

				if batch_count==batch_size:
					batch_count=0
					self.detect_neuro(main_frames,images,batch_size,frame_count)
					main_frames=[]
					images=[]

				if (frame_count+1)%10==0:
					print(str(frame_count+1)+' frames processed...')
					print(datetime.datetime.now())

			if frame_count>=self.full_duration:
				if len(main_frames)>0:
					self.detect_neuro(main_frames,images,batch_size,frame_count)
				break

			frame_count+=1

		print('Information acquisition completed!')


	def craft_data(self):

		print('Crafting data...')
		print(datetime.datetime.now())

		for neuro_name in self.neuro_kinds:

			to_delete=[]
			IDs=list(self.neuro_centers[neuro_name].keys())

			for i in IDs:
				if self.register_counts[neuro_name][i] is None:
					to_delete.append(i)

			if len(IDs)==len(to_delete):
				print('No neural structure detected!')
			
			for i in IDs:
				if i in to_delete:
					del self.to_deregister[neuro_name][i]
					del self.register_counts[neuro_name][i]
					del self.neuro_centers[neuro_name][i]
					del self.neuro_existingcenters[neuro_name][i]
					del self.neuro_contours[neuro_name][i]
					del self.neuro_Fmeans[neuro_name][i]

			centers_for_sort=[]
			centers=[]
			contours=[]
			Fmeans=[]

			for i in self.neuro_centers[neuro_name]:
				centers_for_sort.append([c for c in self.neuro_centers[neuro_name][i] if c is not None][-1])
				centers.append(self.neuro_centers[neuro_name][i])
				contours.append(self.neuro_contours[neuro_name][i])
				Fmeans.append(self.neuro_Fmeans[neuro_name][i])

			self.neuro_centers[neuro_name]={}
			self.neuro_contours[neuro_name]={}
			self.neuro_Fmeans[neuro_name]={}

			sorted_indices=sorted(range(len(centers_for_sort)),key=lambda i:centers_for_sort[i][1])
			centers_for_sort=[centers_for_sort[i] for i in sorted_indices]
			centers=[centers[i] for i in sorted_indices]
			contours=[contours[i] for i in sorted_indices]
			Fmeans=[Fmeans[i] for i in sorted_indices]

			sorted_indices=sorted(range(len(centers_for_sort)),key=lambda i:centers_for_sort[i][0])
			centers=[centers[i] for i in sorted_indices]
			contours=[contours[i] for i in sorted_indices]
			Fmeans=[Fmeans[i] for i in sorted_indices]

			for i in range(len(sorted_indices)):
				self.neuro_centers[neuro_name][i]=centers[i]
				self.neuro_contours[neuro_name][i]=contours[i]
				self.neuro_Fmeans[neuro_name][i]=Fmeans[i]

		print('Data crafting completed!')


	def annotate_video(self):

		print('Annotating video...')
		print(datetime.datetime.now())

		lifdata=LifFile(self.path_to_lif)
		file=[i for i in lifdata.get_iter_image()][0]
		channels=[i for i in file.get_iter_c(t=0,z=0)]

		frame_count=0
		writer=None

		while True:

			if frame_count<self.duration:

				frame_project=[np.array(i) for i in file.get_iter_z(t=frame_count,c=self.main_channel)]
				#frame_project=np.array(frame_project).sum(0)/len(frame_project)
				frame_project=np.array(frame_project).max(0)
				frame_project[frame_project>255]=255
				frame_project=cv2.cvtColor(np.uint8(frame_project),cv2.COLOR_GRAY2BGR)

				if writer is None:
					(h,w)=frame_project.shape[:2]
					out=os.path.join(self.results_path,'Annotated video.avi')
					writer=cv2.VideoWriter(out,cv2.VideoWriter_fourcc(*'MJPG'),1,(w,h),True)

				for neuro_name in self.neuro_kinds:
					for i in self.neuro_centers[neuro_name]:
						if self.neuro_centers[neuro_name][i][frame_count] is not None:
							cx=self.neuro_centers[neuro_name][i][frame_count][0]
							cy=self.neuro_centers[neuro_name][i][frame_count][1]
							cv2.putText(frame_project,neuro_name+str(i),(cx-1,cy+1),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,255,0),1)
							ct=self.neuro_contours[neuro_name][i][frame_count]
							cv2.drawContours(frame_project,[ct],0,(255,255,0),1)

				writer.write(frame_project)

			if frame_count>=self.full_duration:
				break

			frame_count+=1

		print('Video annotation completed!')


	def quantify_parameters(self,F0_period=10,F_period=5):

		# F0_period: the duration (in frames) for calculating F0
		# F_period: the duration (in frames) for calculating dF/F0

		print('Quantifying neural activities...')
		print(datetime.datetime.now())

		for neuro_name in self.neuro_kinds:

			for i in self.neuro_Fmeans[neuro_name]:

				df=pd.DataFrame(self.neuro_Fmeans[neuro_name],index=[i for i in range(self.duration)])
				df.to_excel(os.path.join(self.results_path,neuro_name+'_F.xlsx'),float_format='%.2f',index_label='frame/ID')

				if self.stim_t<=F0_period:
					F_array=self.neuro_Fmeans[neuro_name][i][:(self.stim_t-1)]
				else:
					F_array=self.neuro_Fmeans[neuro_name][i][(self.stim_t-F0_period-1):(self.stim_t-1)]

				F0=np.array(F_array).mean()
				self.all_parameters[neuro_name]['F0'][i]=F0

				if self.stim_t+F_period>=self.duration:
					F_array=self.neuro_Fmeans[neuro_name][i][self.stim_t:]
				else:
					F_array=self.neuro_Fmeans[neuro_name][i][self.stim_t:(self.stim_t+F_period)]

				Fmax=np.array(F_array).max()
				self.all_parameters[neuro_name]['Fmax'][i]=Fmax

				if F0==0.0:
					print('The F0 of '+neuro_name+' '+str(i)+' is 0.')
					self.all_parameters[neuro_name]['dF/F0'][i]=np.nan
				else:
					self.all_parameters[neuro_name]['dF/F0'][i]=(Fmax-F0)/F0

				self.all_parameters[neuro_name]['Stim_t'][i]=self.stim_t

		parameters=[]

		for parameter_name in ['F0','Fmax','dF/F0','Stim_t']:
			df=self.all_parameters[neuro_name][parameter_name]
			parameters.append(pd.DataFrame.from_dict(df,orient='index',columns=[parameter_name]).reset_index(drop=True))

		out_sheet=os.path.join(self.results_path,neuro_name+'_summary.xlsx')
		pd.concat(parameters,axis=1).to_excel(out_sheet,float_format='%.2f',index_label='ID/parameter')

		print('All results exported in: '+str(self.results_path))


	def extract_frames(self,skip_redundant=10):

		print('Generating behavior examples...')
		print(datetime.datetime.now())

		lifdata=LifFile(self.path_to_lif)
		file=[i for i in lifdata.get_iter_image()][0]
		channels=[i for i in file.get_iter_c(t=0,z=0)]

		end_t=self.stim_t+self.duration

		for channel in range(len(channels)):

			for frame_count in range(self.full_duration):

				if self.stim_t<=frame_count<end_t and frame_count%skip_redundant==0:

					frame_project=[np.array(i) for i in file.get_iter_z(t=frame_count,c=channel)]
					#frame_project=np.array(frame_project).sum(0)/len(frame_project)
					frame_project=np.array(frame_project).max(0)
					frame_project[frame_project>255]=255
					out_image=os.path.join(self.results_path,str(channel)+'_'+str(frame_count)+'.jpg')
					cv2.imwrite(out_image,np.uint8(np.array(frame_project)))

		print('The images stored in: '+self.results_path)

