### Created on: 09-2023

import os
import TimeTagger
import time
import numpy as np
import random

from datetime import datetime

class Swabian:
    def __init__(self, CHANNELS, TRIGGER, DELAY, FOLDER, FILE, FOLDER_2=None):
        ### Setting the general parameter for the TT measurement ###
        self.tagger = TimeTagger.createTimeTagger()
        self.channels = CHANNELS
        self.trigger = TRIGGER
        self.delay = DELAY
        self.file = FILE

        ### Setting the delays between the TT's channels (necessary to measure coincidences)###
        for i, inp in enumerate(CHANNELS):
            self.tagger.setTriggerLevel(channel=inp, voltage=TRIGGER[i])
            self.tagger.setInputDelay(inp, DELAY[i]) ### Or setdelayhardware???
        #self.tagger.setTestSignal([1,2,3,4,5,6,7,8], True) # Comment if we want a real measurement
        ### Saving a time stamp to use in the filename to avoid overwriting data ###
        self.filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
        #self.filestamp = 123456
        TYPE = f"\{FILE}_" + str(self.filestamp)
        self.data_dir = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data"+f"\\{FOLDER}"+TYPE
        #self.data_dir = r"D:\\Data"+f"\\{FOLDER}"+TYPE


        ### This is useful to calibrate Two WP's at the same time and to adapt the code for one or 2 folder 
        if FOLDER_2 is None:
            self.folder_2=False
        
        if FOLDER_2 is not None:
            self.folder_2=True
            TYPE_2 = f"\{FOLDER_2}_" + str(self.filestamp)
            # Before comitting it was written self.data_dir but I think this is wrong
            self.data_dir_2 = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data"+f"\\{FOLDER}"+TYPE_2
            #self.data_dir = r"D:\\Data"+f"\\{FOLDER}"+TYPE

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
            # raw_dir = self.data_dir + "\\raw"
            raw_dir = self.data_dir + f"\\raw\\{data_filename[:-4]}"
            os.makedirs(raw_dir, exist_ok=True)

            self.filewriter = TimeTagger.FileWriter(sync_tagger_proxy, raw_dir + os.sep + "filewriter", self.channels)

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
        
    def real_time_measure(self,AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW,Buffer_size, data_filename=False, save_raw=True, save_params=True):

        self.n_reps = N_REP
        self.groups = GROUPS
        self.coincidence_window = COINCIDENCE_WINDOW
        self.aquisition_time = AQUISITION_TIME
        self.Buffer_size = Buffer_size

        # We will record the single conunts and coincidences in one file AND the raw time stamps if we want to use it in post-analysis
        self.synchronized = TimeTagger.SynchronizedMeasurements(self.tagger)
        sync_tagger_proxy = self.synchronized.getTagger()

        self.coincidences = TimeTagger.Coincidences(tagger=sync_tagger_proxy,
                                            coincidenceGroups=self.groups,
                                            coincidenceWindow=self.coincidence_window)
        
        # Sets the list of channels to be analysed by the self.counter depending if we want to measure single events or just coincidence events
        self.list_channels = list(self.coincidences.getChannels())

        self.counter = TimeTagger.Counter(tagger=sync_tagger_proxy,
                                    channels= self.list_channels,
                                    binwidth=self.aquisition_time,
                                    n_values=self.n_reps)
        
        self.stream = TimeTagger.TimeTagStream(tagger=sync_tagger_proxy,n_max_events=self.Buffer_size,channels=self.list_channels)

        counts = [0]*len(self.list_channels)
        chan = []
        if save_raw is True:
            # raw_dir = self.data_dir + "\\raw"
            raw_dir = self.data_dir + f"\\raw\\{data_filename[:-4]}"
            os.makedirs(raw_dir, exist_ok=True)

            self.filewriter = TimeTagger.FileWriter(sync_tagger_proxy, raw_dir + os.sep + "filewriter", self.list_channels)
        
        self.synchronized.start()
        while len(chan)< 1 :
            data = self.stream.getData()
            chan = data.getChannels()
        self.synchronized.stop()
        

        counts[self.list_channels.index(chan[0])] = counts[self.list_channels.index(chan[0])] + 1        

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
                self.save_all_groups_real_meas(self.data_dir, data_filename,counts)
        # Starts aquiring data under the defined paramester above
        #self.synchronized.start()
        #while (np.sum(self.counter.getData())==0):
        #    continue
        #self.synchronized.stop()

        # cleans the TT
        self.clean_buffer_stream()

    def real_time_measure_without_TimeTagStream(self,AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, data_filename=False, save_raw=True, save_params=True):

        self.n_reps = N_REP
        self.groups = GROUPS
        self.coincidence_window = COINCIDENCE_WINDOW
        self.aquisition_time = AQUISITION_TIME

        # We will record the single conunts and coincidences in one file AND the raw time stamps if we want to use it in post-analysis
        self.synchronized = TimeTagger.SynchronizedMeasurements(self.tagger)
        sync_tagger_proxy = self.synchronized.getTagger()

        self.coincidences = TimeTagger.Coincidences(tagger=sync_tagger_proxy,
                                            coincidenceGroups=self.groups,
                                            coincidenceWindow=self.coincidence_window)
        
        # Sets the list of channels to be analysed by the self.counter depending if we want to measure single events or just coincidence events
        self.list_channels = list(self.coincidences.getChannels())

        self.counter = TimeTagger.Counter(tagger=sync_tagger_proxy,
                                    channels= self.list_channels,
                                    binwidth=self.aquisition_time,
                                    n_values=self.n_reps)
        
        if save_raw is True:
            # raw_dir = self.data_dir + "\\raw"
            raw_dir = self.data_dir + f"\\raw\\{data_filename[:-4]}"
            os.makedirs(raw_dir, exist_ok=True)

            self.filewriter = TimeTagger.FileWriter(sync_tagger_proxy, raw_dir + os.sep + "filewriter", self.list_channels)
        
        self.synchronized.start()
        while sum(self.counter.getData()[0])< 1 :
            print(self.counter.getData())
        self.synchronized.stop()

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
        # Starts aquiring data under the defined paramester above
        #self.synchronized.start()
        #while (np.sum(self.counter.getData())==0):
        #    continue
        #self.synchronized.stop()

        # cleans the TT
        self.clean_buffer_stream()

    def replay_raw(self, datadir, BINWIDTH, GROUPS, COINCIDENCE_WINDOW, AQUISITION_TIME,file,replay_dir):

        virtual_tagger = TimeTagger.createTimeTaggerVirtual()
        virtual_tagger.setReplaySpeed(speed=-1)
        total = 0

        # We can pass virtual_tagger to the "tagger" argument of any measurement class constructor
        coincidences_replay = TimeTagger.Coincidences(tagger=virtual_tagger,
                                                    coincidenceGroups=GROUPS,
                                                    coincidenceWindow=COINCIDENCE_WINDOW)

        list_channels = list(coincidences_replay.getChannels())
        REP = int(BINWIDTH/AQUISITION_TIME)

        with open(replay_dir + "\\" + file + ".txt" , mode="w") as f:
                for j in range(REP):
                    replay_begin = AQUISITION_TIME*j # Start from the beggining
                    counter_replay = TimeTagger.Counter(tagger=virtual_tagger,
                                    channels=list_channels,
                                    binwidth=AQUISITION_TIME)

                    virtual_tagger.replay(datadir+ f"\\raw_merged\\" + file +f"\\"+"filewriter_merged.ttbin", begin=replay_begin, duration=AQUISITION_TIME)

                    if virtual_tagger.waitForCompletion(timeout=-1) == True:
                        #Save the single counts and coincidences in a file
                        d=""
                        for counts in counter_replay.getData(): d=d+f"{counts[0]} "
                        last_data_block=counter_replay.getData()
                        total = total+last_data_block    
                        f.write(d + "\n")
                print(np.array(total))
        f.close()
        print("End file" + " " + file)


    def replay_raw_counts_random(self, datadir, BINWIDTH, GROUPS, COINCIDENCE_WINDOW, AQUISITION_TIME,file):
    

        os.makedirs(datadir+"\\random", exist_ok=True)
        replay_dir = datadir+"\\random"

        virtual_tagger = TimeTagger.createTimeTaggerVirtual()
        virtual_tagger.setReplaySpeed(speed=-1)
        total = 0

        # We can pass virtual_tagger to the "tagger" argument of any measurement class constructor
        coincidences_replay = TimeTagger.Coincidences(tagger=virtual_tagger,
                                                    coincidenceGroups=GROUPS,
                                                    coincidenceWindow=COINCIDENCE_WINDOW)

        list_channels = list(coincidences_replay.getChannels())

    
        os.makedirs(replay_dir, exist_ok=True)
        REP = int(BINWIDTH/AQUISITION_TIME)

        with open(replay_dir + "\\" + file + ".txt" , mode="w") as f:
                for j in range(REP):
                    replay_begin = AQUISITION_TIME*j # Start from the beggining
                    counter_replay = TimeTagger.Counter(tagger=virtual_tagger,
                                    channels=list_channels,
                                    binwidth=AQUISITION_TIME)

                    virtual_tagger.replay(datadir+ f"\\raw_merged\\" + file +f"\\"+"filewriter_merged.ttbin", begin=replay_begin, duration=AQUISITION_TIME)

                    if virtual_tagger.waitForCompletion(timeout=-1) == True:
                        #Save the single counts and coincidences in a file
                        d=""
                        for counts in counter_replay.getData(): d=d+f"{counts[0]} "
                        last_data_block=counter_replay.getData()
                        total = total+last_data_block    
                        f.write(d + "\n")
                print(np.array(total))
        f.close()
        print("End file" + " " + file)

    def replay_raw_counts_single_count(self, datadir, BINWIDTH, GROUPS, COINCIDENCE_WINDOW, AQUISITION_TIME,file,replay_dir):

        os.makedirs(replay_dir, exist_ok=True)

        virtual_tagger = TimeTagger.createTimeTaggerVirtual()
        virtual_tagger.setReplaySpeed(speed=-1)
        total = 0

        # We can pass virtual_tagger to the "tagger" argument of any measurement class constructor
        coincidences_replay = TimeTagger.Coincidences(tagger=virtual_tagger,
                                                    coincidenceGroups=GROUPS,
                                                    coincidenceWindow=COINCIDENCE_WINDOW)

        list_channels = list(coincidences_replay.getChannels())

    
        os.makedirs(replay_dir, exist_ok=True)
        REP = int(BINWIDTH/AQUISITION_TIME)

        with open(replay_dir + "\\" + file + ".txt" , mode="w") as f:
                for j in range(REP):
                    replay_begin = AQUISITION_TIME*j # Start from the beggining
                    counter_replay = TimeTagger.Counter(tagger=virtual_tagger,
                                    channels=list_channels,
                                    binwidth=AQUISITION_TIME)

                    virtual_tagger.replay(datadir+ f"\\raw_merged\\" + file +f"\\"+"filewriter_merged.ttbin", begin=replay_begin, duration=AQUISITION_TIME)

                    if virtual_tagger.waitForCompletion(timeout=-1) == True:
                        #Save the single counts and coincidences in a file
                        d=""
                        for counts in counter_replay.getData(): d=d+f"{counts[0]} "
                        last_data_block=counter_replay.getData()
                        total = total+last_data_block    
                        f.write(d + "\n")
                print(np.array(total))
        f.close()
        print("End file" + " " + file)

    
    
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
            for j, counts in enumerate(self.counter.getData()): d=d+f"{counts[0]} "
            f.write(d)
            f.close()
                
    def save_all_groups_real_meas(self, dir, filename,counts):
        counts_dir = dir + "\counts"
        os.makedirs(counts_dir, exist_ok=True)
        # Save the single counts and coincidences in a file
        with open(counts_dir + filename, mode="w") as f:
            d=""
            for j, count in enumerate(counts): d=d+f"{count} "
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
    
    def clean_buffer_stream(self):
        del self.filewriter
        del self.synchronized
        del self.counter
        del self.coincidences
        del self.stream

    def free_swabian(self):
        TimeTagger.freeTimeTagger(self.tagger)