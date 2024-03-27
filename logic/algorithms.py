# This file is distributed under the terms of the GNU General Public License v3.0

from skimage import exposure, color, restoration
from skimage.feature import blob_dog, blob_log, blob_doh, peak_local_max
from skimage.segmentation import watershed
from skimage import measure
from scipy.ndimage import binary_dilation
from scipy import ndimage as ndi
import numpy as np
from math import sqrt, ceil

def convert_to_8_bits(image):
    ''' Normalise and convert image to 8 bits
    Parameters:
    image: image as a numpy array
    Returns:
    Image converted to 8-bits and normalised'''
    if image.shape[-1] == 4:
        output = color.rgba2rgb(image)
        image = color.rgb2gray(output)
    if image.shape[-1] == 3:
        image = color.rgb2gray(image)
    image = exposure.rescale_intensity(image, in_range=(0, np.max(image)), out_range=(0, 255))
    image=image.astype(np.uint8)
    return image

def rolling_ball(image,rad):
    """Determines the background and corrected image using rolling ball algorithm
    Parameters:
    window : an instance of the app
    image : the image to process
    rad : the rolling ball radius in pixels"""
    background = restoration.rolling_ball(image, radius = rad)
    return background, image - background

def segmentation_two_thresholds(image, thresh1, thresh2):
    """Segments the image based on two threshold values
    Parameters:
    image : the image to threshold as a numpy array
    thresh1 : value of the highest threshold
    thresh2 : value of the secon threshold
    Returns:
    mask : the thresholded image"""
    mask_thresh1 = image >= thresh1
    dilated_mask_thresh1 = binary_dilation(mask_thresh1, structure=np.ones((3, 3)))
    mask_thresh2 = image >= thresh2
    mask = dilated_mask_thresh1 & mask_thresh2
    return mask

def blobs_mask(image,blobs_list):
    """Creates a binary image with the blobs
    Parameters:
    blobs_list : list of the blobs with y and x coordinates and the radius in pixels
    Returns:
    binary_image: the image with the blobs"""
    binary_image = np.zeros_like(image, dtype=bool)
    for blob in blobs_list:
        y, x, r = blob
        y, x, r= int(y+0.5),int(x+0.5),ceil(r)
        y_indices, x_indices = np.ogrid[-r:r+1, -r:r+1]
        mask = x_indices**2 + y_indices**2 <= r**2
        y_start, x_start = max(0, y - r), max(0, x - r)
        y_end, x_end = min(image.shape[0], y + r + 1), min(image.shape[1], x + r + 1)
        mask_region = mask[max(0, r-y):min(mask.shape[0], r+y_end-y), max(0, r-x):min(mask.shape[1], r+x_end-x)]
        region_to_update = binary_image[y_start:y_start+mask_region.shape[0], x_start:x_start+mask_region.shape[1]]
        region_to_update |= mask_region
    return binary_image

def return_blobs_algorithms():
    '''Returns the list of the blobs detection algorithms so that they can be added in the proper combobox'''
    return ["None","LoG","DoG","DoH"]

def blobs_detection(image,algo_index,min_radius,max_radius):
    """Use a blob detection algorithm
    Parameters:
    image: the binary image to analyse
    algo: a string indicating the chosen algorithm
    min_radius: the minimum radius in pixels
    max_radius: the maximum radius in pixels
    Returns:
    blobs_list: list of the blobs with y and x coordinates and the radius in pixels"""
    blobs_list = None
    if algo_index == 1:
        blobs_list= blob_log(image, min_sigma=min_radius/sqrt(2),  max_sigma=max_radius/sqrt(2), num_sigma=max_radius-min_radius+1, threshold=.2)
        blobs_list[:, 2] = blobs_list[:, 2] * sqrt(2)
    elif algo_index == 2:
        blobs_list = blob_dog(image, min_sigma=min_radius/sqrt(2),  max_sigma=max_radius/sqrt(2), threshold=.2)
        blobs_list[:, 2] = blobs_list[:, 2] * sqrt(2)
    elif algo_index == 3:
        blobs_list = blob_doh(image, min_sigma=min_radius, max_sigma=max_radius, num_sigma=max_radius-min_radius+1, threshold=.01)
    return blobs_list

def return_labeling_algorithms():
    '''Returns the list of the labeling algorithms so that they can be added in the proper combobox'''
    return["No separation","Watershed"]

def watershed_custom(binary_image, dots):
    '''Determines the labels of a binary image using the watershed algorithm
    Parameters:
    binary_image: the binary image to label
    dots: list of the coordinates of the True pixels in the binary image
    Return:
    new_dots: list of the coordinates of the pixels labeled by the watershed
    ws_list: list of the corresponding labels to the coordinates (0 is the value of the first label)'''
    distance = ndi.distance_transform_edt(binary_image)
    # labeled_image = measure.label(binary_image,connectivity=2) # Ajouté
    max_coords = peak_local_max(distance, labels=binary_image, min_distance=3) # , labels = binary_image , footprint=np.ones((3, 3)) , min_distance=4
    local_maxima = np.zeros(distance.shape, dtype=bool)
    local_maxima[tuple(max_coords.T)] = True
    markers, _ = ndi.label(local_maxima)
    labels = watershed(-distance, markers, mask=binary_image)
    ws_labels=[]
    new_dots=[]
    for i in range(len(dots)):
        if labels[dots[i][0]][dots[i][1]] !=0:
            ws_labels.append(labels[dots[i][0]][dots[i][1]])
            new_dots.append(dots[i])
    return new_dots, ws_labels

def labeling_custom(binary_image, dots):
    '''Labels a binary image
    Parameters:
    binary_image: the binary image to label
    dots: list of the coordinates of the True pixels in the binary image'''
    labeled_image = measure.label(binary_image,connectivity=2)
    labels = []
    for i in range(len(dots)):
        labels.append(labeled_image[dots[i][0]][dots[i][1]])
    return labels

def binary_to_dots(binary_image):
    '''Transforms a binary image into a list a coordinates
    Parameters:
    binary_image: the binary image to transform'''
    coord = np.where(binary_image)
    dots = [[y,x] for y,x in zip(coord[0],coord[1])]
    return dots

def sieve_labels(dots,labels,sieve_size):
    '''Removes labeled objects with a size inferior or equal to the sieve size
    Parameters:
    dots: list of the coordinates of the True pixels in the binary image
    labels: list of the labels for each coordinate in dots (the first label has the value 0)
    sieve_size: all objects with a pixel size inferior or equal to this parameter will be removed
    Return:
    sieved_dots: the coordinates of the points after the sieve was applied
    sieved_labels: the labels corresponding to each dot (the first label has the value 0)'''
    sieved_dots = []
    sieved_labels = []
    unique_labels = set(labels)
    latest_label = 0
    for label in unique_labels:
        label_coordinates = [dots[i] for i in range(len(labels)) if labels[i] == label]
        if len(label_coordinates) > sieve_size:
            sieved_dots.extend(label_coordinates)
            sieved_labels.extend([latest_label]*len(label_coordinates))
            latest_label += 1
    return sieved_dots, sieved_labels

def mean_SD_size(labels):
    '''Calculates the mean size and the standard deviation of a list of labels
    labels: the list of labels for the calculation'''
    if len(labels) == 0:
        return 0,0
    nb_labels = max(labels)+1
    sizes = []
    sizes = [labels.count(i) for i in range(nb_labels)]
    return round(np.mean(sizes),2),round(np.std(sizes),2)

def mean_median_size(labels):
    '''Calculates the mean size and the median of a list of labels
    labels: the list of labels for the calculation'''
    if len(labels) == 0:
        return 0,0
    nb_labels = max(labels)+1
    sizes = []
    sizes = [labels.count(i) for i in range(nb_labels)]
    return round(np.mean(sizes),2),round(np.median(sizes),2)


def return_contouring_algorithms():
    '''Returns the list of the contouring algorithms so that they can be added in the proper combobox'''
    return ["Scan","Spreading 4-connect","Spreading 8-connect","Shrinking box","Threshold"]

def contour_scan(image,threshold):
    '''Contours an object in an image 
    image: the image with the object to contour
    threshold: pixel with a value inferior or equal to this parameter will be considered as background if selected by the algorithm
    Returns:
    mask: a binary image with the contoured object'''
    mask = np.ones_like(image, dtype=bool)
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            if image[y,x] <= threshold:
                mask[y,x] = False
            else:
                break
    for x in range(image.shape[1]):
        for y in reversed(range(image.shape[0])):
            if image[y,x] <= threshold:
                mask[y,x] = False
            else:
                break
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            if image[y,x] <= threshold:
                mask[y,x] = False
            else:
                break
    for y in range(image.shape[0]):
        for x in reversed(range(image.shape[1])):
            if image[y,x] <= threshold:
                mask[y,x] = False
            else:
                break
    return mask

def contour_spreading_4(image, threshold):
    '''Contours an object in an image 
    image: the image with the object to contour
    threshold: pixel with a value inferior or equal to this parameter will be considered as background if selected by the algorithm
    Return:
    mask: a binary image with the contoured object'''
    mask = np.ones_like(image, dtype=bool)
    stack = [(i, j) for i in range(image.shape[0]) for j in range(image.shape[1])
             if i in [0, image.shape[0] - 1] or j in [0, image.shape[1] - 1]]
    while stack:
        i, j = stack.pop()
        if image[i][j] <= threshold and mask[i][j]:
            mask[i][j] = False
            stack.extend((i + y, j + x) for y in [-1, 0, 1] for x in [-1, 0, 1] 
             if (abs(y) != abs(x)) and 0 <= i + y < image.shape[0] and 0 <= j + x < image.shape[1]
             and image[i + y, j + x] <= threshold and mask[i + y, j + x])
    return mask

def contour_spreading_8(image, threshold):
    '''Contours an object in an image 
    image: the image with the object to contour
    threshold: pixel with a value inferior or equal to this parameter will be considered as background if selected by the algorithm
    Return:
    mask: a binary image with the contoured object'''
    mask = np.ones_like(image, dtype=bool)
    stack = [(i, j) for i in range(image.shape[0]) for j in range(image.shape[1])
             if i in [0, image.shape[0] - 1] or j in [0, image.shape[1] - 1]]
    while stack:
        i, j = stack.pop()
        if image[i][j] <= threshold and mask[i][j]:
            mask[i][j] = False
            stack.extend((i + y, j + x) for y in [-1, 0, 1] for x in [-1, 0, 1] 
             if not (y == 0 and x == 0) and 0 <= i + y < image.shape[0] and 0 <= j + x < image.shape[1]
             and image[i + y, j + x] <= threshold and mask[i + y, j + x])
    return mask

def contour_shrinking_box(image, threshold):
    '''Contours an object in an image 
    image: the image with the object to contour
    threshold: pixel with a value inferior or equal to this parameter will be considered as background if selected by the algorithm
    Return:
    mask: a binary image with the contoured object'''
    mask = np.zeros_like(image, dtype=bool)
    beginx,beginy = 0,0
    height,width = image.shape[0],image.shape[1]
    endy,endx = image.shape[0],image.shape[1]
    outerbox = np.zeros_like(image, dtype=bool)
    outerbox[beginy:endy,beginx] = image[beginy:endy,beginx]<= threshold
    outerbox[beginy:endy,endx-1] = image[beginy:endy,endx-1]<= threshold
    outerbox[beginy,beginx:endx] = image[beginy,beginx:endx]<= threshold
    outerbox[endy-1,beginx:endx] = image[endy-1,beginx:endx]<= threshold
    beginx += 1
    beginy +=1
    endx -=1
    endy -=1
    while endx-beginx>1 and endy-beginy>1:
        innerbox = np.zeros_like(image, dtype=bool)
        # innerbox[beginy:endy,beginx] = image[beginy:endy,beginx]<= threshold
        # innerbox[beginy:endy,endx-1] = image[beginy:endy,endx-1]<= threshold
        # innerbox[beginy,beginx:endx] = image[beginy,beginx:endx]<= threshold
        # innerbox[endy-1,beginx:endx] = image[endy-1,beginx:endx]<= threshold
        innerbox[0:beginy,0:width] = image[0:beginy,0:width]<= threshold
        innerbox[0:height,endx:width] = image[0:height,endx:width]<= threshold
        innerbox[endy:height,0:width] = image[endy:height,0:width]<= threshold
        innerbox[0:height,0:beginx] = image[0:height,0:beginx] <= threshold
        outerbox_dil = binary_dilation(outerbox, structure=np.ones((3, 3))) # ,iterations=3
        mask = outerbox_dil & innerbox
        if mask.any():
            outerbox = outerbox | mask
        else:
            return ~outerbox
        beginx += 1
        beginy +=1
        endx -=1
        endy -=1
    return ~outerbox

def calculate_contours_centroid(image):
    '''Calculates the centroid coordinates of a contoured object
    image: the binary image with the contoured object
    Return:
    A list with the y and x coordinates of the centroid'''
    coord = np.where(image)
    return [np.mean(coord[0]),np.mean(coord[1])]

def return_colormaps():
    '''Returns the list of the colormaps so that they can be added in the proper combobox'''
    return ["afmhot","autumn","bone","cividis","cool","copper","gist_gray","gist_heat","gray","hot","inferno","magma","plasma","spring","summer","viridis","winter","Wistia"]

def get_target(mask_thresh, mask_contour, nb_layers, centroid_y, centroid_x):
    '''Calculates the percentage of pixels in mask_thresh compared to mask_contour in concentric regions
    mask_thresh: a binary image with the primary objects
    mask_contour: a binary image with the contoured object containing the primary objects
    nb_layers: number of concentric regions
    centroid_y: y coordinates of the contoured object in mask_contour
    centroid_x: x coordinates of the contoured object in mask_contour
    Return:
    image: a heatmap with the percentage as pixel value'''
    coordinates = np.where(mask_contour)
    distances_to_centroid = np.sqrt((coordinates[1] - centroid_x)**2 + (coordinates[0] - centroid_y)**2)
    max_distance = np.max(distances_to_centroid)
    layer_thickness_list = np.linspace (0,max_distance,num=nb_layers+1)
    image=np.zeros_like(mask_thresh, dtype=np.float32)
    for i in range(nb_layers):
        mask = (layer_thickness_list[i] < distances_to_centroid) & (distances_to_centroid <= layer_thickness_list[i+1])
        th = np.sum(mask_thresh[coordinates[0][mask], coordinates[1][mask]])
        cont = np.sum(mask_contour[coordinates[0][mask], coordinates[1][mask]])
        if cont != 0:
            density = th / cont * 100
        else:
            density = 0
        image[coordinates[0][mask], coordinates[1][mask]] = density
    return image

def get_targets(mask_thresh, mask_contour,mask_centroids,nb_layers, centroid_y, centroid_x):
    '''Calculates the percentage of pixels and their count in mask_thresh compared to mask_contour in concentric regions
    mask_thresh: a binary image with the primary objects
    mask_contour: a binary image with the contoured object containing the primary objects
    mask_centroid: a binary image with the centroids of the blobs
    nb_layers: number of concentric regions
    centroid_y: y coordinates of the contoured object in mask_contour
    centroid_x: x coordinates of the contoured object in mask_contour
    Return:
    image_percentage: a heatmap with the percentage as pixel value
    image_count: a heatmap with the count of blobs as pixel value'''
    coordinates = np.where(mask_contour)
    distances_to_centroid = np.sqrt((coordinates[1] - centroid_x)**2 + (coordinates[0] - centroid_y)**2)
    max_distance = np.max(distances_to_centroid)
    layer_thickness_list = np.linspace (0,max_distance,num=nb_layers+1)
    image_percentage=np.zeros_like(mask_thresh, dtype=np.float32)
    image_count=np.zeros_like(mask_thresh, dtype=np.float32)
    for i in range(nb_layers):
        mask = (layer_thickness_list[i] < distances_to_centroid) & (distances_to_centroid <= layer_thickness_list[i+1])
        th = np.sum(mask_thresh[coordinates[0][mask], coordinates[1][mask]])
        cont = np.sum(mask_contour[coordinates[0][mask], coordinates[1][mask]])
        centroids_sum = np.sum(mask_centroids[coordinates[0][mask], coordinates[1][mask]])
        if cont != 0:
            density = th / cont * 100
        else:
            density = 0
        image_percentage[coordinates[0][mask], coordinates[1][mask]] = density
        image_count[coordinates[0][mask], coordinates[1][mask]] = centroids_sum
    return image_percentage, image_count

def density_map(mask_thresh, mask_contour, kernel_size):
    '''Calculates the percentage of pixels in mask_thresh compared to mask_contour with a convolution
    mask_thresh: a binary image with the primary objects
    mask_contour: a binary image with the contoured object containing the primary objects
    kernel_size: the size of the kernel in pixels (preferably an odd number)
    Return:
    density_map: a heatmap with the percentage as pixel value'''
    half_kernel = int((kernel_size-1)/2)
    height,width = mask_thresh.shape
    density_map = np.zeros_like(mask_thresh,dtype=np.float32)
    for y in range(height):
        for x in range(width):
            if mask_contour[y][x]:
                ymin=max(0,y-half_kernel)
                ymax=min(height,y+1+half_kernel)
                xmin=max(0,x-half_kernel)
                xmax=min(width,x+1+half_kernel)
                th=np.sum(mask_thresh[ymin:ymax,xmin:xmax])
                cont=np.sum(mask_contour[ymin:ymax,xmin:xmax])
                if cont>0:
                    density_map[y][x]=th/cont*100
    return density_map

def density_maps(mask_thresh, mask_contour, mask_centroids, kernel_size):
    '''Calculates the percentage of pixels and the count of blobs in mask_thresh compared to mask_contour with a convolution
    mask_thresh: a binary image with the primary objects
    mask_contour: a binary image with the contoured object containing the primary objects
    mask_centroid: a binary image with the centroids of the blobs
    kernel_size: the size of the kernel in pixels (preferably an odd number)
    Return:
    density_map_percentage: a heatmap with the percentage as pixel value
    density_map_count: a heatmap with the count of blobs as pixel value'''
    half_kernel = int((kernel_size-1)/2)
    height,width = mask_thresh.shape
    density_map_percentage = np.zeros_like(mask_thresh,dtype=np.float32)
    density_map_count = np.zeros_like(mask_thresh,dtype=np.float32)
    for y in range(height):
        for x in range(width):
            if mask_contour[y,x]:
                ymin=max(0,y-half_kernel)
                ymax=min(height,y+1+half_kernel)
                xmin=max(0,x-half_kernel)
                xmax=min(width,x+1+half_kernel)
                th=np.sum(mask_thresh[ymin:ymax,xmin:xmax])
                cont=np.sum(mask_contour[ymin:ymax,xmin:xmax])
                centroids_count=np.sum(mask_centroids[ymin:ymax,xmin:xmax])
                if cont>0:
                    density_map_percentage[y,x]=th/cont*100
                density_map_count[y,x] = centroids_count
    return density_map_percentage, density_map_count

def min_max_mean_SD_density(d_map,mask_contour):
    '''Returns the minimal, maximal, mean and the standard deviation of the density in a heatmap
    d_map: the heatmap with the densities
    mask_contour: a binary image with the contoured object'''
    return round(np.min(d_map[mask_contour]),3),round(np.max(d_map[mask_contour]),3),round(np.mean(d_map[mask_contour]),3),round(np.std(d_map[mask_contour]),3)

def min_max_mean_median_density(d_map,mask_contour):
    '''Returns the minimal, maximal, mean and median of the density in a heatmap
    d_map: the heatmap with the densities
    mask_contour: a binary image with the contoured object'''
    return round(np.min(d_map[mask_contour]),3),round(np.max(d_map[mask_contour]),3),round(np.mean(d_map[mask_contour]),3),round(np.median(d_map[mask_contour]),3)

def is_float(string):
    '''Returns True if the string can be converted into a float'''
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def calculate_centroids_sizes(dots,labels):
    '''Calculates the y and x coordinates of labeled objects as well as their size in pixels
    Parameters:
    dots: list of the coordinates of the True pixels in the binary image
    labels: list of the labels for each coordinate in dots (the first label has the value 0)
    Return:
    A numpy array with the y and x coordinates and the size of the objects'''
    unique_labels = np.unique(labels)
    centroidsAndSizes = []
    for label in unique_labels:
        label_coordinates = [dots[i] for i in range(len(labels)) if labels[i] == label]
        centroid = np.mean(label_coordinates, axis=0)
        size = len(label_coordinates)
        centroidsAndSizes.append([centroid[0],centroid[1],size])
    return np.array(centroidsAndSizes)

def calculate_centroids(dots,labels):
    '''Calculates the y and x coordinates of labeled objects
    Parameters:
    dots: list of the coordinates of the True pixels in the binary image
    labels: list of the labels for each coordinate in dots (the first label has the value 0)
    Return:
    A numpy array with the y and x coordinates'''
    unique_labels = np.unique(labels)
    centroids = []
    for label in unique_labels:
        label_coordinates = [dots[i] for i in range(len(labels)) if labels[i] == label]
        centroid = np.mean(label_coordinates, axis=0)
        centroids.append([centroid[0],centroid[1]])
    return np.array(centroids)

def calculate_blobs_centroids_and_DTOC(dots,labels,centroid_x,centroid_y):
    '''Calculates the y and x coordinates of labeled objects as well as their distance to a centroid
    Parameters:
    dots: list of the coordinates of the True pixels in the binary image
    labels: list of the labels for each coordinate in dots (the first label has the value 0)
    centroid_x: the x coordinate of the centroid
    centroid_y: the y coordinate of the centroid
    Return:
    A numpy array with the y and x coordinates of the labeled objects and a list with their distance to the centroid in pixels'''
    if labels == []:
        return [],[]
    unique_labels = np.unique(labels)
    centroids = []
    for label in unique_labels:
        label_coordinates = [dots[i] for i in range(len(labels)) if labels[i] == label]
        centroid = np.mean(label_coordinates, axis=0)
        centroids.append(centroid)
    centroids = np.array(centroids)
    DTOC = np.sqrt((centroids[:, 0] - centroid_y) ** 2 + (centroids[:, 1] - centroid_x) ** 2)
    return np.array(centroids), DTOC.tolist()

def get_filename(absolutePath):
    '''Returns the file name with the extension of an absolute path'''
    last_slash_index = max(absolutePath.rfind('/'), absolutePath.rfind('\\'))
    return absolutePath[last_slash_index + 1:]

def get_folder(absolutePath):
    '''Returns the folder of an absolute path'''
    last_slash_index = max(absolutePath.rfind('/'), absolutePath.rfind('\\'))
    return absolutePath[:last_slash_index+1]

   
def get_filename_without_extension(absolutePath):
    '''Returns the file name without the extension of an absolute path'''
    last_slash_index = max(absolutePath.rfind('/'), absolutePath.rfind('\\'))
    dot_index = absolutePath.rfind('.')
    if last_slash_index != -1:
        return absolutePath[last_slash_index + 1:dot_index]
    else:
        return absolutePath[0:dot_index]

def dots_to_binary(mask_thresh,dots):
    '''Transforms a list of coordinates y and x into a binary image
    Parameters:
    mask_thresh: the image with the expected shape
    dots: a list of the [y,x] coordinates
    Return:
    mask: a binary image'''
    mask = np.zeros_like(mask_thresh,dtype=bool)
    for coord in dots:
        y, x = round(coord[0]), round(coord[1])
        mask[y,x] = True
    return mask
