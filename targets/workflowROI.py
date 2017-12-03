


import cv2
import os
import numpy as np
from osgeo import gdal
from ROIExtraction import *
import sys
sys.path.append("..")
import geoTIFF
import csv
import getpass
userName = getpass.getuser()

## USER INPUTS
geotiffFolderName = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/'
tsvFilename = '/cis/otherstu/gvs6104/DIRS/20171102/GroundDocumentation/datasheets/Flight_Notes.tsv'
txtDestination = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/Flight1445_' + userName + '.csv'
stepNumber = 2 #do every other image, or every image, ...

startFrameNumber = 0 #can equal int or filename as string
startFrameNumber = 'IMG_0000.tiff'
##


# Get all filenames within this flight directory
fileNames = sorted(os.listdir(geotiffFolderName))
imageCount = len(fileNames)
imageNameDict = dict(enumerate(fileNames))
imageNameDict = {v:k for k,v in imageNameDict.items()}

if type(startFrameNumber) == str:
	try:
		startFrameNumber = int(imageNameDict[startFrameNumber])
	except:
		startFrameNumber = 0

##Create windows outside of loop so they aren't constantly being deleted/created
currentIm_tag = 'Current Geotiff'
cv2.namedWindow(currentIm_tag, cv2.WINDOW_AUTOSIZE) #resize and display the image

zoomName = 'Zoomed region for easier point selection.'
cv2.namedWindow(zoomName, cv2.WINDOW_AUTOSIZE)
zoom = cv2.imshow(zoomName, np.zeros((200,200)))

## Data to be read in once-per-flight
times,targets,targetdescriptor = fieldData(tsvFilename)

##Create the textfile that the data will be written out to
if os.path.isfile(txtDestination) == True:
	writeMode = 'a'
else:
	writeMode = 'w'

with open(txtDestination, writeMode) as currentTextFile:
	writer = csv.writer(currentTextFile, delimiter = ',')
	if writeMode == 'w':
		writer.writerow(['Target Number', 'Frame Number(s) [geoTiff]', 'ELM/Profile', 'Pixel Resolution', 'Flight Altitude', 'Mean B', 'Mean G', 'Mean R', 'Mean RE', 'Mean IR', 'Std B', 'Std G', 'Std R', 'Std RE', 'Std IR', 'Centroid Coord X', 'Centroid Coord Y', 'Nadir Angle'])

	##START MAIN LOOP
	currentImIndex = startFrameNumber
	while True:

		if currentImIndex == imageCount:
			print('You have reached the end of the imagery. Nice job.')
			print('You can find the csv file at:' + txtDestination)
			break

		currentFilename = geotiffFolderName + fileNames[currentImIndex]
		currentGeotiff, displayImage = getDisplayImage(currentFilename)
		im = cv2.imshow(currentIm_tag, displayImage)

		print("Do you want to get ROIs in this frame? 'y' for yes, 'a' for back, 'd' for forward.")
		print(fileNames[currentImIndex], 'Index = ', currentImIndex)
		userInput = cv2.waitKey(0)
		if userInput == ord('y'):
			print('Ready to accept points.')
			print("Once you are done, press 'y' to accept, 'n' to redo.")



			#get the coordinates of the ROI from the user
			pointsX, pointsY = selectROI(currentIm_tag, displayImage)

			#ask user for input of the current target
			currentTargetNumber = assignTargetNumber()

			#compute the statistics that will be written out, from the ROI coords
			maskedIm, ROI_image, mean, stdev, centroid = computeStats(currentGeotiff, currentFilename, pointsX, pointsY)

			#get metadata
			irradianceDict, frametime, altitude, resolution= micasenseRawData(currentFilename)
			filenumber = bestSVC(frametime,currentTargetNumber,times,targets,targetdescriptor)
			#writer.writerow([currentTargetNumber, fileNames[currentImIndex], '', 'Pixel Resolution', 'Flight Altitude', str(mean[0]), str(mean[1]), str(mean[2]), str(mean[3]), str(mean[4]), str(stdev[0]), str(stdev[1]), str(stdev[2]), str(stdev[3]), str(stdev[4]), str(centroid), 'Nadir Angle'])
			writer.writerow([currentTargetNumber, fileNames[currentImIndex], '', resolution, altitude, str(mean[0]), str(mean[1]), str(mean[2]), str(mean[3]), str(mean[4]), str(stdev[0]), str(stdev[1]), str(stdev[2]), str(stdev[3]), str(stdev[4]), str(centroid[0]), str(centroid[1]), ''])

			print('Line has been written to file.')


		#elif userInput == ord('n'):	
			# print("Press 'a' for back, 'd' for forward.")	
			# motionInput = cv2.waitKey(0)


		elif userInput == ord('d'):
			currentImIndex += stepNumber
		elif userInput == ord('a'):
			currentImIndex += -stepNumber
		elif userInput == 27:
			break
		else:
			continue






	cv2.destroyWindow(currentIm_tag)
	currentTextFile.close()
	print('You can find the csv file at:' + txtDestination)

