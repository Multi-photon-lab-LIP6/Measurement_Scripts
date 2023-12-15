### Created on: 09-2023

import os
import TimeTagger

from datetime import datetime

class Swabian:
    def __init__(self, CHANNELS, TRIGGER, DELAY, FOLDER, FILE, FOLDER_2=None):
        ### Setting the general parameter for the TT measurement ###
        self.tagger = TimeTagger.createTimeTagger()
        self.channels = CHANNELS
        self.trigger = TRIGGER
        self.delay = DELAY

        ### Setting the delays between the TT's channels (necessary to measure coincidences)###
        for i, inp in enumerate(CHANNELS):
            self.tagger.setTriggerLevel(channel=inp, voltage=TRIGGER[i])
            self.tagger.setInputDelay(inp, DELAY[i]) ### Or setdelayhardware???
            # tagger.setTestSignal(inp, True) # Comment if we want a real measurement
        ### Saving a time stamp to use in the filename to avoid overwriting data ###
        self.filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
        TYPE = f"\{FILE}_" + str(self.filestamp)
        self.data_dir = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data"+f"\\{FOLDER}"+TYPE

        ### This is useful to calibrate Two WP's at the same time and to adapt the code for one or 2 folder 
        if FOLDER_2 is None:
            self.folder_2=False
        
        if FOLDER_2 is not None:
            self.folder_2=True
            TYPE_2 = f"\{FOLDER_2}_" + str(self.filestamp)
            self.data_dir_2 = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data"+f"\\{FOLDER}"+TYPE_2

    """
    measure():
    - Takes AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW as parameters to define the parameters of the measurement we want to take
    - Set count_singles=True if we want to count the events on the single CHANNELS (can be used for control of laser power, determine heralding efficiency, etc)
    - Set datafilename allows to choose the name of the file that saves the number of coincidence events (and single events if count_singles=True) determined by GROUPS (+CHANNELS if count_singles=True)
    - save_raw=True: saves the raw timestamps of all events detected by the TT, such that we can post analyse them later with differenct functions and params (e.g.: different AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW)
    - save_params=True: saves CHANNELS, TRIGGER, DELAY, AQUISITION_TIME, N_REP, GROUPS and COINCIDENCE_WINDOW values in a file
    """
    def measure(self, AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=False, save_raw=True, save_params=True):

        self.aquisition_time = AQUISITION_TIME
        self.n_reps = N_REP
        self.groups = GROUPS
        self.coincidence_window = COINCIDENCE_WINDOW

        # We will record the single conunts and coincidences in one file AND the raw time stamps if we want to use it in post-analysis
        self.synchronized = TimeTagger.SynchronizedMeasurements(self.tagger)
        sync_tagger_proxy = self.synchronized.getTagger()

        self.coincidences = TimeTagger.Coincidences(tagger=sync_tagger_proxy,
                                            coincidenceGroups=self.groups,
                                            coincidenceWindow=self.coincidence_window)
        
        # Sets the list of channels to be analysed by the self.counter depending if we want to measure single events or just coincidence events
        self.list_channels = list(self.coincidences.getChannels())
        if count_singles is True:
            self.list_channels = self.list_channels + self.channels

        self.counter = TimeTagger.Counter(tagger=sync_tagger_proxy,
                                    channels=self.list_channels,
                                    binwidth=self.aquisition_time,
                                    n_values=self.n_reps)
        
        # To save the raw timestamps we need to write them in files in real time such that the buffer doesn't overflow
        # These are saved only once in the first folder, even if self.folder_2 is True
        if save_raw is True:
            raw_dir = self.data_dir + "\\raw"
            os.makedirs(raw_dir, exist_ok=True)

            self.filewriter = TimeTagger.FileWriter(sync_tagger_proxy, raw_dir + os.sep + "filewriter", self.channels)
            self.filewriter.setMaxFileSize(500 * 1024)


        # Starts aquiring data under the defined paramester above
        self.synchronized.startFor(self.aquisition_time)
        self.synchronized.waitUntilFinished()
        
        # Save the params
        if save_params is True:
            self.save_params(self.data_dir)
            if self.folder_2 is True:
                self.save_params(self.data_dir_2)


        # Saves the aquired data
        if data_filename is not False:
            if self.folder_2 is True:
                self.save_group(self.data_dir, data_filename, 0)
                self.save_group(self.data_dir_2, data_filename, 1)
            else:
                self.save_all_groups(self.data_dir, data_filename)

        # cleans the TT
        self.clean_buffer()
        


    def save_params(self, dir):
        param_dir = dir + "\params"
        os.makedirs(param_dir, exist_ok=True)
        with open(param_dir+"\params.txt", mode="w") as f:
            f.write(f"CHANNELS: {self.channels} \n TRIGGER: {self.trigger} \n DELAY: {self.delay} \n AQUISITION_TIME: {self.aquisition_time} \n N_REP: {self.n_reps} \n GROUPS: {self.list_channels} \n COINCIDENCE WINDOW: {self.coincidence_window}")
            f.close()

    def save_all_groups(self, dir, filename):
        counts_dir = dir + "\counts"
        os.makedirs(counts_dir, exist_ok=True)
        # Save the single counts and coincidences in a file
        with open(counts_dir + filename, mode="w") as f:
            d=""
            for j, counts in enumerate(self.counter.getData()): d=d+f"{counts[0]}   "
            f.write(d)
            f.close()

    def save_group(self, dir, filename, group):
        counts_dir = dir + "\counts"
        os.makedirs(counts_dir, exist_ok=True)
        # Save the single counts and coincidences in a file
        with open(counts_dir + filename, mode="w") as f:
            f.write(str(self.counter.getData()[group][0]))
            f.close()

    def clean_buffer(self):
        del self.filewriter
        del self.synchronized
        del self.counter
        del self.coincidences

    def free_swabian(self):
        TimeTagger.freeTimeTagger(self.tagger)