import numpy as np
import pandas as pd
import os
import random
import math
from sklearn.model_selection import train_test_split

class DistributedDataSet:
    def __init__(self, data, seed, batch_size, clients_num):
        self.data = data
        self.seed = seed
        self.batch_size = batch_size
        self.clients_num = clients_num

        self.data_size = None
        self.n_classes = None
        self.client_datasets = {}

    def data_split(self, test_size):
        train, test = train_test_split(self.data, random_state=self.seed, test_size=test_size, stratify=self.data.y)
        train.index = np.arange(len(train))
        test.index = np.arange(len(test))
        return train, test

    def split_and_shuffle_labels(self, y_data, seed, amount, n_classes):
        y_data=pd.DataFrame(y_data,columns=["labels"])
        y_data["i"]=np.arange(len(y_data))
        label_dict = dict()
        for i in range(n_classes):
            var_name="label" + str(i)
            label_info=y_data[y_data["labels"]==i]
            np.random.seed(seed)
            label_info=np.random.permutation(label_info)
            label_info=label_info[0:amount]
            label_info=pd.DataFrame(label_info, columns=["labels","i"])
            label_dict.update({var_name: label_info })
        return label_dict

    def get_iid_subsamples_indices(self, label_dict, number_of_samples, batch_size, n_classes):
        sample_dict= dict()
        batch_size = int(batch_size/n_classes)
        for i in range(number_of_samples):
            sample_name="sample"+str(i)
            dumb=pd.DataFrame()
            for j in range(n_classes):
                label_name=str("label")+str(j)
                a=label_dict[label_name][i*batch_size:(i+1)*batch_size]
                dumb=pd.concat([dumb,a], axis=0)
            dumb.reset_index(drop=True, inplace=True)    
            sample_dict.update({sample_name: dumb}) 
        return sample_dict

    def create_iid_subsamples(self, sample_dict, data):
        data_li = []
        
        for i in range(len(sample_dict)):  ### len(sample_dict)= number of samples
            sample_name="sample"+str(i)
            indices=np.sort(np.array(sample_dict[sample_name]["i"]))
            df = data.loc[indices]
            data_li.append(df)
                    
        return data_li

    def get_distributed_dataset(self, test_size):
        train, test = self.data_split(test_size)
        min_class_num = min(train.y.value_counts().values)
        self.n_classes = self.data.y.nunique()
        self.data_size = len(self.data)
        label_dict = self.split_and_shuffle_labels(train.y.values, self.seed, min_class_num, self.n_classes) 
        
        clients_labels_dict = {}
        for labels, values in label_dict.items():
            a = np.array_split(values, self.clients_num)
            client_count = 0
            for i in a:
                try:
                    clients_labels_dict[client_count][labels] = i
                except:
                    clients_labels_dict[client_count] = {}
                    clients_labels_dict[client_count][labels] = i
                client_count+=1

        for cl, cl_label_dict in clients_labels_dict.items():
            subsample_indices = self.get_iid_subsamples_indices(cl_label_dict, int(self.data_size*(1-test_size)/(self.clients_num*self.batch_size)), self.batch_size, self.n_classes)
            iid_samples = self.create_iid_subsamples(subsample_indices, train)
            self.client_datasets[cl] = iid_samples

        return self.client_datasets, test