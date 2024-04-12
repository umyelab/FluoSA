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
import wx
import wx.lib.agw.hyperlink as hl
from pathlib import Path
import torch
import json
import shutil
from .analyzer import AnalyzeCalciumSignal
from .detector import traindetector,testdetector
from FluoSA import __version__

the_absolute_current_path=str(Path(__file__).resolve().parent)



class InitialWindow(wx.Frame):

	def __init__(self,title):

		super(InitialWindow,self).__init__(parent=None,title=title,size=(750,440))
		self.dispaly_window()


	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)

		self.text_welcome=wx.StaticText(panel,label='Welcome to FluoSA!',style=wx.ALIGN_CENTER|wx.ST_ELLIPSIZE_END)
		boxsizer.Add(0,60,0)
		boxsizer.Add(self.text_welcome,0,wx.LEFT|wx.RIGHT|wx.EXPAND,5)
		boxsizer.Add(0,60,0)
		self.text_developers=wx.StaticText(panel,
			label='Developed by Yujia Hu\n\nBing Ye Lab, Life Sciences Institute, University of Michigan',
			style=wx.ALIGN_CENTER|wx.ST_ELLIPSIZE_END)
		boxsizer.Add(self.text_developers,0,wx.LEFT|wx.RIGHT|wx.EXPAND,5)
		boxsizer.Add(0,60,0)
		
		links=wx.BoxSizer(wx.HORIZONTAL)
		homepage=hl.HyperLinkCtrl(panel,0,'Home Page',URL='https://github.com/umyelab/FluoSA')
		userguide=hl.HyperLinkCtrl(panel,0,'Extended Guide',URL='')
		links.Add(homepage,0,wx.LEFT|wx.EXPAND,10)
		links.Add(userguide,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(links,0,wx.ALIGN_CENTER,50)
		boxsizer.Add(0,50,0)

		module_modules=wx.BoxSizer(wx.HORIZONTAL)
		button_train=wx.Button(panel,label='Training Module',size=(200,40))
		button_train.Bind(wx.EVT_BUTTON,self.window_train)
		wx.Button.SetToolTip(button_train,'Teach FluoSA to recognize the neural structures of your interest.')
		button_analyze=wx.Button(panel,label='Analysis Module',size=(200,40))
		button_analyze.Bind(wx.EVT_BUTTON,self.window_analyze)
		wx.Button.SetToolTip(button_analyze,'Use FluoSA to analyze activity of the detected neural structures.')
		module_modules.Add(button_train,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_modules.Add(button_analyze,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_modules,0,wx.ALIGN_CENTER,50)
		boxsizer.Add(0,50,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def window_train(self,event):

		WindowLv1_TrainingModule('Training Module')


	def window_analyze(self,event):

		WindowLv1_AnalysisModule('Analysis Module')



class WindowLv1_TrainingModule(wx.Frame):

	def __init__(self,title):

		super(WindowLv1_TrainingModule,self).__init__(parent=None,title=title,size=(500,360))
		self.dispaly_window()


	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)
		boxsizer.Add(0,60,0)

		button_generateimages=wx.Button(panel,label='Generate Image Examples',size=(300,40))
		button_generateimages.Bind(wx.EVT_BUTTON,self.generate_images)
		wx.Button.SetToolTip(button_generateimages,
			'Extract frames from LIF files to annotate the neural structures of your interest. See Extended Guide for how to select images to annotate.')
		boxsizer.Add(button_generateimages,0,wx.ALIGN_CENTER,10)
		boxsizer.Add(0,5,0)

		link_annotate=wx.lib.agw.hyperlink.HyperLinkCtrl(panel,0,'\nAnnotate images with Roboflow\n',URL='https://roboflow.com')
		boxsizer.Add(link_annotate,0,wx.ALIGN_CENTER,10)
		boxsizer.Add(0,5,0)

		button_traindetectors=wx.Button(panel,label='Train Detectors',size=(300,40))
		button_traindetectors.Bind(wx.EVT_BUTTON,self.train_detectors)
		wx.Button.SetToolTip(button_traindetectors,
			'The trained Detectors can detect the neural structures of your interest. See Extended Guide for how to set parameters for training.')
		boxsizer.Add(button_traindetectors,0,wx.ALIGN_CENTER,10)
		boxsizer.Add(0,5,0)

		button_testdetectors=wx.Button(panel,label='Test Detectors',size=(300,40))
		button_testdetectors.Bind(wx.EVT_BUTTON,self.test_detectors)
		wx.Button.SetToolTip(button_testdetectors,
			'Test trained Detectors on the annotated ground-truth image dataset (similar to the image dataset used for training a Detector).')
		boxsizer.Add(button_testdetectors,0,wx.ALIGN_CENTER,10)
		boxsizer.Add(0,50,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def generate_images(self,event):

		WindowLv2_GenerateImages('Generate Image Examples')


	def train_detectors(self,event):

		WindowLv2_TrainDetectors('Train Detectors')


	def test_detectors(self,event):

		WindowLv2_TestDetectors('Test Detectors')



class WindowLv1_AnalysisModule(wx.Frame):

	def __init__(self,title):

		super(WindowLv1_AnalysisModule,self).__init__(parent=None,title=title,size=(500,150))
		self.dispaly_window()


	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)
		boxsizer.Add(0,40,0)

		button_analyzebehaviors=wx.Button(panel,label='Analyze Calcium Signal',size=(300,40))
		button_analyzebehaviors.Bind(wx.EVT_BUTTON,self.analyze_calcium)
		wx.Button.SetToolTip(button_analyzebehaviors,
			'Automatically detect neural structures of your interest and analyze their calcium signals.')
		boxsizer.Add(button_analyzebehaviors,0,wx.ALIGN_CENTER,10)
		boxsizer.Add(0,30,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def analyze_calcium(self,event):

		WindowLv2_AnalyzeCalcium('Analyze Calcium Signal')



class WindowLv2_GenerateImages(wx.Frame):

	def __init__(self,title):

		super(WindowLv2_GenerateImages,self).__init__(parent=None,title=title,size=(1000,330))
		self.path_to_lifs=None
		self.result_path=None
		self.t=0
		self.duration=10
		self.skip_redundant=10

		self.dispaly_window()

	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)

		module_inputvideos=wx.BoxSizer(wx.HORIZONTAL)
		button_inputvideos=wx.Button(panel,label='Select the *.LIF file(s) to generate\nimage examples',size=(300,40))
		button_inputvideos.Bind(wx.EVT_BUTTON,self.select_videos)
		wx.Button.SetToolTip(button_inputvideos,'Select one or more *.LIF files.')
		self.text_inputvideos=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_inputvideos.Add(button_inputvideos,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_inputvideos.Add(self.text_inputvideos,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,10,0)
		boxsizer.Add(module_inputvideos,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_outputfolder=wx.BoxSizer(wx.HORIZONTAL)
		button_outputfolder=wx.Button(panel,label='Select a folder to store the\ngenerated image examples',size=(300,40))
		button_outputfolder.Bind(wx.EVT_BUTTON,self.select_outpath)
		wx.Button.SetToolTip(button_outputfolder,'The generated image examples (extracted frames) will be stored in this folder.')
		self.text_outputfolder=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_outputfolder.Add(button_outputfolder,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_outputfolder.Add(self.text_outputfolder,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_outputfolder,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_startgenerate=wx.BoxSizer(wx.HORIZONTAL)
		button_startgenerate=wx.Button(panel,label='Specify when generating image examples\nshould begin (unit: frame)',size=(300,40))
		button_startgenerate.Bind(wx.EVT_BUTTON,self.specify_timing)
		wx.Button.SetToolTip(button_startgenerate,'Enter a beginning time point for all files')
		self.text_startgenerate=wx.StaticText(panel,label='Default: at the beginning of the file(s).',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_startgenerate.Add(button_startgenerate,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_startgenerate.Add(self.text_startgenerate,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_startgenerate,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_duration=wx.BoxSizer(wx.HORIZONTAL)
		button_duration=wx.Button(panel,label='Specify how long generating examples\nshould last (unit: frame)',size=(300,40))
		button_duration.Bind(wx.EVT_BUTTON,self.input_duration)
		wx.Button.SetToolTip(button_duration,'This duration will be used for all the files.')
		self.text_duration=wx.StaticText(panel,label='Default: 10 frames.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_duration.Add(button_duration,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_duration.Add(self.text_duration,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_duration,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_skipredundant=wx.BoxSizer(wx.HORIZONTAL)
		button_skipredundant=wx.Button(panel,label='Specify how many frames to skip when\ngenerating two consecutive images',size=(300,40))
		button_skipredundant.Bind(wx.EVT_BUTTON,self.specify_redundant)
		wx.Button.SetToolTip(button_skipredundant,'Set an interval between the two consecutively extracted images.')
		self.text_skipredundant=wx.StaticText(panel,label='Default: generate an image example every 10 frames.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_skipredundant.Add(button_skipredundant,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_skipredundant.Add(self.text_skipredundant,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_skipredundant,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		generate=wx.BoxSizer(wx.HORIZONTAL)
		button_generate=wx.Button(panel,label='Start to generate image examples',size=(300,40))
		button_generate.Bind(wx.EVT_BUTTON,self.generate_images)
		wx.Button.SetToolTip(button_generate,'Press the button to start generating image examples.')
		generate.Add(button_generate,0,wx.LEFT,50)
		boxsizer.Add(0,5,0)
		boxsizer.Add(generate,0,wx.RIGHT|wx.ALIGN_RIGHT,90)
		boxsizer.Add(0,10,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def select_videos(self,event):

		wildcard='LIF files(*.lif)|*.lif;*.LIF'
		dialog=wx.FileDialog(self,'Select LIF file(s)','','',wildcard,style=wx.FD_MULTIPLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.path_to_lifs=dialog.GetPaths()
			path=os.path.dirname(self.path_to_lifs[0])
			self.text_inputvideos.SetLabel('Selected '+str(len(self.path_to_lifs))+' file(s) in: '+path+'.')
		dialog.Destroy()


	def select_outpath(self,event):

		dialog=wx.DirDialog(self,'Select a directory','',style=wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.result_path=dialog.GetPath()
			self.text_outputfolder.SetLabel('Generate image examples in: '+self.result_path+'.')
		dialog.Destroy()


	def specify_timing(self,event):

		dialog=wx.NumberEntryDialog(self,'Enter beginning time to generate examples','The unit is frame:','Beginning time to generate examples',0,0,100000000000000)
		if dialog.ShowModal()==wx.ID_OK:
			self.t=float(dialog.GetValue())
		self.text_startgenerate.SetLabel('Start to generate image examples at the: '+str(self.t)+' frame.')
		dialog.Destroy()


	def input_duration(self,event):

		dialog=wx.NumberEntryDialog(self,'Enter the duration for generating examples','The unit is frame:','Duration for generating examples',10,1,100000000000000)
		if dialog.ShowModal()==wx.ID_OK:
			self.duration=int(dialog.GetValue())
		self.text_duration.SetLabel('The generation of image examples lasts for '+str(self.duration)+' frames.')
		dialog.Destroy()


	def specify_redundant(self,event):

		dialog=wx.NumberEntryDialog(self,'How many frames to skip?','Enter a number:','Interval for generating examples',10,1,100000000000000)
		if dialog.ShowModal()==wx.ID_OK:
			self.skip_redundant=int(dialog.GetValue())
		self.text_skipredundant.SetLabel('Generate an image example every '+str(self.skip_redundant)+' frames.')
		dialog.Destroy()


	def generate_images(self,event):

		if self.path_to_lifs is None or self.result_path is None:

			wx.MessageBox('No input file(s) / output folder selected.','Error',wx.OK|wx.ICON_ERROR)

		else:

			do_nothing=True

			dialog=wx.MessageDialog(self,'Start to generate image examples?','Start to generate examples?',wx.YES_NO|wx.ICON_QUESTION)
			if dialog.ShowModal()==wx.ID_YES:
				do_nothing=False
			else:
				do_nothing=True
			dialog.Destroy()

			if do_nothing is False:
				print('Generating image examples...')
				for i in self.path_to_lifs:
					ACS=AnalyzeCalciumSignal(i,self.result_path,self.t,self.duration)
					ACS.extract_frames(skip_redundant=self.skip_redundant)
				print('Image example generation completed!')



class WindowLv2_TrainDetectors(wx.Frame):

	def __init__(self,title):

		super(WindowLv2_TrainDetectors,self).__init__(parent=None,title=title,size=(1000,280))
		self.path_to_trainingimages=None
		self.path_to_annotation=None
		self.inference_size=512
		self.iteration_num=1000
		self.detector_path=os.path.join(the_absolute_current_path,'detectors')
		self.path_to_detector=None

		self.dispaly_window()


	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)

		module_selectimages=wx.BoxSizer(wx.HORIZONTAL)
		button_selectimages=wx.Button(panel,label='Select the folder containing\nall the training images',size=(300,40))
		button_selectimages.Bind(wx.EVT_BUTTON,self.select_images)
		wx.Button.SetToolTip(button_selectimages,'The folder that stores all the training images.')
		self.text_selectimages=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_selectimages.Add(button_selectimages,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_selectimages.Add(self.text_selectimages,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,10,0)
		boxsizer.Add(module_selectimages,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_selectannotation=wx.BoxSizer(wx.HORIZONTAL)
		button_selectannotation=wx.Button(panel,label='Select the *.json\nannotation file',size=(300,40))
		button_selectannotation.Bind(wx.EVT_BUTTON,self.select_annotation)
		wx.Button.SetToolTip(button_selectannotation,'The .json file that stores the annotation for the training images. Should be in “COCO instance segmentation” format.')
		self.text_selectannotation=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_selectannotation.Add(button_selectannotation,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_selectannotation.Add(self.text_selectannotation,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_selectannotation,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_inferencingsize=wx.BoxSizer(wx.HORIZONTAL)
		button_inferencingsize=wx.Button(panel,label='Specify the inferencing framesize\nfor the Detector to train',size=(300,40))
		button_inferencingsize.Bind(wx.EVT_BUTTON,self.input_inferencingsize)
		wx.Button.SetToolTip(button_inferencingsize,'Should be an even number. Larger size means higher accuracy but slower speed.')
		self.text_inferencingsize=wx.StaticText(panel,label='Default: 512.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_inferencingsize.Add(button_inferencingsize,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_inferencingsize.Add(self.text_inferencingsize,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_inferencingsize,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_iterations=wx.BoxSizer(wx.HORIZONTAL)
		button_iterations=wx.Button(panel,label='Specify the iteration number\nfor the Detector training',size=(300,40))
		button_iterations.Bind(wx.EVT_BUTTON,self.input_iterations)
		wx.Button.SetToolTip(button_iterations,'More training iterations typically yield higher accuracy but take longer.')
		self.text_iterations=wx.StaticText(panel,label='Default: 1000.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_iterations.Add(button_iterations,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_iterations.Add(self.text_iterations,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_iterations,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		button_train=wx.Button(panel,label='Train the Detector',size=(300,40))
		button_train.Bind(wx.EVT_BUTTON,self.train_detector)
		wx.Button.SetToolTip(button_train,'English letters, numbers, “_”, or “-” are acceptable for the names but no “@” or “^”.')
		boxsizer.Add(0,5,0)
		boxsizer.Add(button_train,0,wx.RIGHT|wx.ALIGN_RIGHT,90)
		boxsizer.Add(0,10,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def select_images(self,event):

		dialog=wx.DirDialog(self,'Select a directory','',style=wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.path_to_trainingimages=dialog.GetPath()
			self.text_selectimages.SetLabel('Path to training images: '+self.path_to_trainingimages+'.')
		dialog.Destroy()


	def select_annotation(self,event):

		wildcard='Annotation File (*.json)|*.json'
		dialog=wx.FileDialog(self, 'Select the annotation file (.json)','',wildcard=wildcard,style=wx.FD_OPEN)
		if dialog.ShowModal()==wx.ID_OK:
			self.path_to_annotation=dialog.GetPath()
			f=open(self.path_to_annotation)
			info=json.load(f)
			classnames=[]
			for i in info['categories']:
				if i['id']>0:
					classnames.append(i['name'])
			self.text_selectannotation.SetLabel('Neural structure categories in annotation file: '+str(classnames)+'.')
		dialog.Destroy()


	def input_inferencingsize(self,event):

		dialog=wx.NumberEntryDialog(self,'Input the inferencing frame size\nof the Detector to train','Enter a number:','Divisible by 2',512,1,2048)
		if dialog.ShowModal()==wx.ID_OK:
			self.inference_size=int(dialog.GetValue())
			self.text_inferencingsize.SetLabel('Inferencing frame size: '+str(self.inference_size)+'.')
		dialog.Destroy()
		

	def input_iterations(self,event):

		dialog=wx.NumberEntryDialog(self,'Input the iteration number\nfor the Detector training','Enter a number:','Iterations',1000,1,10000)
		if dialog.ShowModal()==wx.ID_OK:
			self.iteration_num=int(dialog.GetValue())
			self.text_iterations.SetLabel('Training iteration number: '+str(self.iteration_num)+'.')
		dialog.Destroy()


	def train_detector(self,event):

		if self.path_to_trainingimages is None or self.path_to_annotation is None:

			wx.MessageBox('No training images / annotation file selected.','Error',wx.OK|wx.ICON_ERROR)

		else:

			do_nothing=False

			stop=False
			while stop is False:
				dialog=wx.TextEntryDialog(self,'Enter a name for the Detector to train','Detector name')
				if dialog.ShowModal()==wx.ID_OK:
					if dialog.GetValue()!='':
						self.path_to_detector=os.path.join(self.detector_path,dialog.GetValue())
						if not os.path.isdir(self.path_to_detector):
							stop=True
						else:
							wx.MessageBox('The name already exists.','Error',wx.OK|wx.ICON_ERROR)
				else:
					do_nothing=True
					stop=True
				dialog.Destroy()

			if do_nothing is False:

				traindetector(self.path_to_annotation,self.path_to_trainingimages,self.path_to_detector,self.iteration_num,self.inference_size)



class WindowLv2_TestDetectors(wx.Frame):

	def __init__(self,title):

		super(WindowLv2_TestDetectors,self).__init__(parent=None,title=title,size=(1000,280))
		self.path_to_testingimages=None
		self.path_to_annotation=None
		self.detector_path=os.path.join(the_absolute_current_path,'detectors')
		self.path_to_detector=None
		self.output_path=None

		self.dispaly_window()


	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)

		module_selectdetector=wx.BoxSizer(wx.HORIZONTAL)
		button_selectdetector=wx.Button(panel,label='Select a Detector\nto test',size=(300,40))
		button_selectdetector.Bind(wx.EVT_BUTTON,self.select_detector)
		wx.Button.SetToolTip(button_selectdetector,'The names of neural structures in the testing dataset should match those in the selected Detector.')
		self.text_selectdetector=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_selectdetector.Add(button_selectdetector,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_selectdetector.Add(self.text_selectdetector,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,10,0)
		boxsizer.Add(module_selectdetector,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_selectimages=wx.BoxSizer(wx.HORIZONTAL)
		button_selectimages=wx.Button(panel,label='Select the folder containing\nall the testing images',size=(300,40))
		button_selectimages.Bind(wx.EVT_BUTTON,self.select_images)
		wx.Button.SetToolTip(button_selectimages,'The folder that stores all the testing images.')
		self.text_selectimages=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_selectimages.Add(button_selectimages,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_selectimages.Add(self.text_selectimages,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_selectimages,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_selectannotation=wx.BoxSizer(wx.HORIZONTAL)
		button_selectannotation=wx.Button(panel,label='Select the *.json\nannotation file',size=(300,40))
		button_selectannotation.Bind(wx.EVT_BUTTON,self.select_annotation)
		wx.Button.SetToolTip(button_selectannotation,'The .json file that stores the annotation for the testing images. Should be in “COCO instance segmentation” format.')
		self.text_selectannotation=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_selectannotation.Add(button_selectannotation,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_selectannotation.Add(self.text_selectannotation,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_selectannotation,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_selectoutpath=wx.BoxSizer(wx.HORIZONTAL)
		button_selectoutpath=wx.Button(panel,label='Select the folder to\nstore testing results',size=(300,40))
		button_selectoutpath.Bind(wx.EVT_BUTTON,self.select_outpath)
		wx.Button.SetToolTip(button_selectoutpath,'The folder will stores the testing results.')
		self.text_selectoutpath=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_selectoutpath.Add(button_selectoutpath,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_selectoutpath.Add(self.text_selectoutpath,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_selectoutpath,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		testanddelete=wx.BoxSizer(wx.HORIZONTAL)
		button_test=wx.Button(panel,label='Test the Detector',size=(300,40))
		button_test.Bind(wx.EVT_BUTTON,self.test_detector)
		wx.Button.SetToolTip(button_test,'Test the selected Detector on the annotated, ground-truth testing images.')
		button_delete=wx.Button(panel,label='Delete a Detector',size=(300,40))
		button_delete.Bind(wx.EVT_BUTTON,self.remove_detector)
		wx.Button.SetToolTip(button_delete,'Permanently delete a Detector. The deletion CANNOT be restored.')
		testanddelete.Add(button_test,0,wx.RIGHT,50)
		testanddelete.Add(button_delete,0,wx.LEFT,50)
		boxsizer.Add(0,5,0)
		boxsizer.Add(testanddelete,0,wx.RIGHT|wx.ALIGN_RIGHT,90)
		boxsizer.Add(0,10,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def select_detector(self,event):

		detectors=[i for i in os.listdir(self.detector_path) if os.path.isdir(os.path.join(self.detector_path,i))]
		if '__pycache__' in detectors:
			detectors.remove('__pycache__')
		if '__init__' in detectors:
			detectors.remove('__init__')
		if '__init__.py' in detectors:
			detectors.remove('__init__.py')
		detectors.sort()

		dialog=wx.SingleChoiceDialog(self,message='Select a Detector to test',caption='Test a Detector',choices=detectors)
		if dialog.ShowModal()==wx.ID_OK:
			detector=dialog.GetStringSelection()
			self.path_to_detector=os.path.join(self.detector_path,detector)
			neuromapping=os.path.join(self.path_to_detector,'model_parameters.txt')
			with open(neuromapping) as f:
				model_parameters=f.read()
			neuro_names=json.loads(model_parameters)['neuro_names']
			self.text_selectdetector.SetLabel('Selected: '+str(detector)+' (neural structures: '+str(neuro_names)+').')
		dialog.Destroy()


	def select_images(self,event):

		dialog=wx.DirDialog(self,'Select a directory','',style=wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.path_to_testingimages=dialog.GetPath()
			self.text_selectimages.SetLabel('Path to testing images: '+self.path_to_testingimages+'.')
		dialog.Destroy()


	def select_annotation(self,event):

		wildcard='Annotation File (*.json)|*.json'
		dialog=wx.FileDialog(self, 'Select the annotation file (.json)','',wildcard=wildcard,style=wx.FD_OPEN)
		if dialog.ShowModal()==wx.ID_OK:
			self.path_to_annotation=dialog.GetPath()
			f=open(self.path_to_annotation)
			info=json.load(f)
			classnames=[]
			for i in info['categories']:
				if i['id']>0:
					classnames.append(i['name'])
			self.text_selectannotation.SetLabel('Neural structure categories in annotation file: '+str(classnames)+'.')
		dialog.Destroy()


	def select_outpath(self,event):

		dialog=wx.DirDialog(self,'Select a directory','',style=wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.output_path=dialog.GetPath()
			self.text_selectoutpath.SetLabel('Path to testing images: '+self.output_path+'.')
		dialog.Destroy()


	def test_detector(self,event):

		if self.path_to_detector is None or self.path_to_testingimages is None or self.path_to_annotation is None or self.output_path is None:
			wx.MessageBox('No Detector / training images / annotation file / output path selected.','Error',wx.OK|wx.ICON_ERROR)
		else:
			testdetector(self.path_to_annotation,self.path_to_testingimages,self.path_to_detector,self.output_path)


	def remove_detector(self,event):

		detectors=[i for i in os.listdir(self.detector_path) if os.path.isdir(os.path.join(self.detector_path,i))]
		if '__pycache__' in detectors:
			detectors.remove('__pycache__')
		if '__init__' in detectors:
			detectors.remove('__init__')
		if '__init__.py' in detectors:
			detectors.remove('__init__.py')
		detectors.sort()

		dialog=wx.SingleChoiceDialog(self,message='Select a Detector to delete',caption='Delete a Detector',choices=detectors)
		if dialog.ShowModal()==wx.ID_OK:
			detector=dialog.GetStringSelection()
			dialog1=wx.MessageDialog(self,'Delete '+str(detector)+'?','CANNOT be restored!',wx.YES_NO|wx.ICON_QUESTION)
			if dialog1.ShowModal()==wx.ID_YES:
				shutil.rmtree(os.path.join(self.detector_path,detector))
			dialog1.Destroy()
		dialog.Destroy()



class WindowLv2_AnalyzeCalcium(wx.Frame):

	def __init__(self,title):

		super(WindowLv2_AnalyzeCalcium,self).__init__(parent=None,title=title,size=(1000,400))
		self.detector_path=None
		self.path_to_detector=None
		self.detector_batch=1
		self.neuro_kinds=[]
		self.path_to_lifs=None
		self.result_path=None
		self.decode_neuronumber=False
		self.neuro_number=None
		self.autofind_t=False
		self.decode_t=False
		self.t=5
		self.stimulation_channel=0
		self.main_channel=1
		self.duration=0
		self.F0_period=10
		self.F_period=5
		self.dispaly_window()


	def dispaly_window(self):

		panel=wx.Panel(self)
		boxsizer=wx.BoxSizer(wx.VERTICAL)

		module_inputvideos=wx.BoxSizer(wx.HORIZONTAL)
		button_inputvideos=wx.Button(panel,label='Select the *.LIF file(s)\nfor analyzing calcium signals',size=(300,40))
		button_inputvideos.Bind(wx.EVT_BUTTON,self.select_videos)
		wx.Button.SetToolTip(button_inputvideos,'Select one or more *.LIF file(s).')
		self.text_inputvideos=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_inputvideos.Add(button_inputvideos,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_inputvideos.Add(self.text_inputvideos,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,10,0)
		boxsizer.Add(module_inputvideos,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_outputfolder=wx.BoxSizer(wx.HORIZONTAL)
		button_outputfolder=wx.Button(panel,label='Select a folder to store\nthe analysis results',size=(300,40))
		button_outputfolder.Bind(wx.EVT_BUTTON,self.select_outpath)
		wx.Button.SetToolTip(button_outputfolder,'Will create a subfolder for each LIF file in the selected folder.')
		self.text_outputfolder=wx.StaticText(panel,label='None.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_outputfolder.Add(button_outputfolder,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_outputfolder.Add(self.text_outputfolder,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_outputfolder,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_detection=wx.BoxSizer(wx.HORIZONTAL)
		button_detection=wx.Button(panel,label='Select the Detector to\ndetect neural structures',size=(300,40))
		button_detection.Bind(wx.EVT_BUTTON,self.select_detector)
		wx.Button.SetToolTip(button_detection,'A trained Detector can detect neural structures of your interest.')
		self.text_detection=wx.StaticText(panel,label='None',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_detection.Add(button_detection,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_detection.Add(self.text_detection,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_detection,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_startanalyze=wx.BoxSizer(wx.HORIZONTAL)
		button_startanalyze=wx.Button(panel,label='Specify when the stimulation\nis started (unit: frame)',size=(300,40))
		button_startanalyze.Bind(wx.EVT_BUTTON,self.specify_timing)
		wx.Button.SetToolTip(button_startanalyze,'Enter a time for all LIF files or use "Decode from filenames" for different times of different files. See Extended Guide for details.')
		self.text_startanalyze=wx.StaticText(panel,label='Default: at the 5th frame.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_startanalyze.Add(button_startanalyze,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_startanalyze.Add(self.text_startanalyze,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_startanalyze,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_duration=wx.BoxSizer(wx.HORIZONTAL)
		button_duration=wx.Button(panel,label='Specify the analysis\nduration (unit: frame)',size=(300,40))
		button_duration.Bind(wx.EVT_BUTTON,self.input_duration)
		wx.Button.SetToolTip(button_duration,'The duration is the same for all the selected files.')
		self.text_duration=wx.StaticText(panel,label='Default: the entire duration.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_duration.Add(button_duration,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_duration.Add(self.text_duration,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_duration,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		module_neuronumber=wx.BoxSizer(wx.HORIZONTAL)
		button_neuronumber=wx.Button(panel,label='Specify the number of\nneural structures',size=(300,40))
		button_neuronumber.Bind(wx.EVT_BUTTON,self.specify_neuronumber)
		wx.Button.SetToolTip(button_neuronumber,'Enter a number for all files or use "Decode from filenames" for different numbers in different files. See Extended Guide for details.')
		self.text_neuronumber=wx.StaticText(panel,label='Default: 1.',style=wx.ALIGN_LEFT|wx.ST_ELLIPSIZE_END)
		module_neuronumber.Add(button_neuronumber,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		module_neuronumber.Add(self.text_neuronumber,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(module_neuronumber,0,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
		boxsizer.Add(0,5,0)

		button_analyze=wx.Button(panel,label='Start to analyze calcium signals',size=(300,40))
		button_analyze.Bind(wx.EVT_BUTTON,self.analyze_calsignals)
		wx.Button.SetToolTip(button_analyze,'Will output F0, dF/F0, Fmax, and frame-wise F.')
		boxsizer.Add(0,5,0)
		boxsizer.Add(button_analyze,0,wx.RIGHT|wx.ALIGN_RIGHT,90)
		boxsizer.Add(0,10,0)

		panel.SetSizer(boxsizer)

		self.Centre()
		self.Show(True)


	def select_videos(self,event):

		wildcard='LIF files(*.lif)|*.lif;*.LIF'
		dialog=wx.FileDialog(self,'Select LIF file(s)','','',wildcard,style=wx.FD_MULTIPLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.path_to_lifs=dialog.GetPaths()
			path=os.path.dirname(self.path_to_lifs[0])
			self.text_inputvideos.SetLabel('Selected '+str(len(self.path_to_lifs))+' file(s) in: '+path+'.')
		dialog.Destroy()


	def select_outpath(self,event):

		dialog=wx.DirDialog(self,'Select a directory','',style=wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal()==wx.ID_OK:
			self.result_path=dialog.GetPath()
			self.text_outputfolder.SetLabel('Results will be in: '+self.result_path+'.')
		dialog.Destroy()


	def select_detector(self,event):

		self.neuro_number={}
		self.detector_path=os.path.join(the_absolute_current_path,'detectors')

		detectors=[i for i in os.listdir(self.detector_path) if os.path.isdir(os.path.join(self.detector_path,i))]
		if '__pycache__' in detectors:
			detectors.remove('__pycache__')
		if '__init__' in detectors:
			detectors.remove('__init__')
		if '__init__.py' in detectors:
			detectors.remove('__init__.py')
		detectors.sort()
		if 'Choose a new directory of the Detector' not in detectors:
			detectors.append('Choose a new directory of the Detector')

		dialog=wx.SingleChoiceDialog(self,message='Select a Detector',caption='Select a Detector',choices=detectors)
		if dialog.ShowModal()==wx.ID_OK:
			detector=dialog.GetStringSelection()
			if detector=='Choose a new directory of the Detector':
				dialog1=wx.DirDialog(self,'Select a directory','',style=wx.DD_DEFAULT_STYLE)
				if dialog1.ShowModal()==wx.ID_OK:
					self.path_to_detector=dialog1.GetPaths()
				dialog1.Destroy()
			else:
				self.path_to_detector=os.path.join(self.detector_path,detector)
			with open(os.path.join(self.path_to_detector,'model_parameters.txt')) as f:
				model_parameters=f.read()
			neuro_names=json.loads(model_parameters)['neuro_names']
			if len(neuro_names)>1:
				dialog1=wx.MultiChoiceDialog(self,message='Specify which neural structures involved in analysis',
					caption='Neuro kind',choices=neuro_names)
				if dialog1.ShowModal()==wx.ID_OK:
					self.neuro_kinds=[neuro_names[i] for i in dialog1.GetSelections()]
				else:
					self.neuro_kinds=neuro_names
				dialog1.Destroy()
			else:
				self.neuro_kinds=neuro_names
			for neuro_name in self.neuro_kinds:
				self.neuro_number[neuro_name]=1
			self.text_neuronumber.SetLabel('The number of '+str(self.neuro_kinds)+' is: '+str(list(self.neuro_number.values()))+'.')
			self.text_detection.SetLabel('Detector: '+detector+'; '+'The neuro structures: '+str(self.neuro_kinds)+'.')
		dialog.Destroy()


		if torch.cuda.is_available():
			dialog=wx.NumberEntryDialog(self,"Enter the batch size for faster processing",
				"GPU is available in this device for Detectors.\nYou may use batch processing for faster speed.",'Batch size',1,1,100)
			if dialog.ShowModal()==wx.ID_OK:
				self.detector_batch=int(dialog.GetValue())
			else:
				self.detector_batch=1
			dialog.Destroy()


	def specify_timing(self,event):

		methods=['Automatic (stimulation channel)','Decode from filenames: "_bt_"','Enter a time point']

		dialog=wx.SingleChoiceDialog(self,message='Specify stimulation time (frame)',caption='Stimulation onset',choices=methods)
		if dialog.ShowModal()==wx.ID_OK:
			method=dialog.GetStringSelection()
			if method=='Automatic (stimulation channel)':
				self.autofind_t=True
				self.decode_t=False
				dialog1=wx.NumberEntryDialog(self,'Stimulation channel','Enter 0,1,2','Stimulation channel',0,0,2)
				if dialog1.ShowModal()==wx.ID_OK:
					self.stimulation_channel=int(dialog1.GetValue())
				dialog1.Destroy()
				text='Automatically find the stimulation onset in stimulation channel ('+str(self.stimulation_channel)+');'
			elif method=='Decode from filenames: "_bt_"':
				self.autofind_t=False
				self.decode_t=True
				text='Decode the time from the filenames: the "t" immediately after the letter "b"" in "_bt_";'
			else:
				self.autofind_t=False
				self.decode_t=False
				dialog1=wx.NumberEntryDialog(self,'Enter a time','The unit is frame:','Stimulation onset',5,0,100000000000000)
				if dialog1.ShowModal()==wx.ID_OK:
					self.t=int(dialog1.GetValue())
				dialog1.Destroy()
				text='Stimulation onset at: '+str(self.t)+' frame.'
		dialog.Destroy()

		dialog=wx.NumberEntryDialog(self,'Main channel','Enter 0,1,2','Main channel',1,0,2)
		if dialog.ShowModal()==wx.ID_OK:
			self.main_channel=int(dialog.GetValue())
		dialog.Destroy()

		self.text_startanalyze.SetLabel(text+' main channel: '+str(self.main_channel)+'.')


	def input_duration(self,event):

		dialog=wx.NumberEntryDialog(self,'Enter the duration of the analysis','The unit is frame:','Analysis duration',0,0,100000000000000)
		if dialog.ShowModal()==wx.ID_OK:
			self.duration=int(dialog.GetValue())
			if self.duration!=0:
				self.text_duration.SetLabel('The analysis duration is '+str(self.duration)+' frames.')
			else:
				self.text_duration.SetLabel('The analysis duration is to the end of a file.')
		dialog.Destroy()


	def specify_neuronumber(self,event):

		methods=['Decode from filenames: "_nn_"','Enter the number of neural structures']

		dialog=wx.SingleChoiceDialog(self,message='Specify the number of neural structures',caption='The number of neural structures',
			choices=methods)
		if dialog.ShowModal()==wx.ID_OK:
			method=dialog.GetStringSelection()
			if method=='Enter the number of neural structures':
				self.decode_neuronumber=False
				self.neuro_number={}
				for neuro_name in self.neuro_kinds:
					dialog1=wx.NumberEntryDialog(self,'','The number of '+str(neuro_name)+': ',str(neuro_name)+' number',1,1,100)
					if dialog1.ShowModal()==wx.ID_OK:
						self.neuro_number[neuro_name]=int(dialog1.GetValue())
					else:
						self.neuro_number[neuro_name]=1
					dialog1.Destroy()
				self.text_neuronumber.SetLabel('The number of '+str(self.neuro_kinds)+' is: '+str(list(self.neuro_number.values()))+'.')
			else:
				self.decode_neuronumber=True
				self.text_neuronumber.SetLabel('Decode from the filenames: the "n" immediately after the letter "n" in _"nn"_.')
		dialog.Destroy()


	def analyze_calsignals(self,event):

		if self.path_to_lifs is None or self.result_path is None or self.path_to_detector is None:

			wx.MessageBox('No input file(s) / result folder / Detector.','Error',wx.OK|wx.ICON_ERROR)

		else:

			for i in self.path_to_lifs:

				filename=os.path.splitext(os.path.basename(i))[0].split('_')
				if self.decode_neuronumber is True:
					self.neuro_number={}
					number=[x[1:] for x in filename if len(x)>1 and x[0]=='n']
					for a,neuro_name in enumerate(self.neuro_kinds):
						self.neuro_number[neuro_name]=int(number[a])
				if self.decode_t is True:
					for x in filename:
						if len(x)>1:
							if x[0]=='b':
								self.t=int(x[1:])
				if self.neuro_number is None:
					self.neuro_number={}
					for neuro_name in self.neuro_kinds:
						self.neuro_number[neuro_name]=1

				ACS=AnalyzeCalciumSignal(i,self.result_path,self.t,self.duration)
				ACS.prepare_analysis(self.path_to_detector,self.neuro_number,self.neuro_kinds)
				ACS.acquire_information(batch_size=self.detector_batch,autofind_t=self.autofind_t,
					stimulation_channel=self.stimulation_channel,main_channel=self.main_channel)
				ACS.craft_data()
				ACS.annotate_video()
				ACS.quantify_parameters(F0_period=self.F0_period,F_period=self.F_period)



def main_window():

	the_absolute_current_path=str(Path(__file__).resolve().parent)
	app=wx.App()
	InitialWindow(f"FluoSA v{__version__}")
	print('The user interface initialized!')
	app.MainLoop()


if __name__=='__main__':

	main_window()


