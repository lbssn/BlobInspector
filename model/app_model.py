# This file is distributed under the terms of the GNU General Public License v3.0

class AppModel(object):
    def __init__(self):
        self.stacks = {}
        self.stack_names = []
        self.included_images = {}
        self.corrected_images = {}
        self.rolling_ball_param = {}
        self.rolling_ball_background = {}

        self.threshold_algo = {}
        self.first_threshold = {}
        self.second_threshold = {}
        self.thresholded_images = {}

        self.blobs_detection_algo = {}
        self.blobs_radius = {}
        self.blobs_thresholded_images = {}

        self.labeling_option = {}
        self.labeling_sieve_size = {}
        self.labeling_coordinates = {}
        self.labeling_labels = {}
        self.labeling_images_with_labels = {}
        self.labeling_images_conserved_blobs = {}

        self.contours_algo = {}
        self.contours_background = {}
        self.contours_mask = {}
        self.contours_centroids = {}
        self.contours_main_slice = {}

        self.density_target_layers = {}
        self.density_map_kernel_size = {}
        self.density_target_heatmap = {}
        self.density_map_heatmap = {}
        self.density_taget_centroid_heatmap = {}
        self.density_map_centroid_heatmap = {}

        self.results_count = {}
        self.results_density = {}
        self.results_distance = {}

        self.stack_infos = {}

        