import numpy as np
import pandas as pd
import os
import random
import math
from sklearn.model_selection import train_test_split

class DistributedDataSet:
    def __init__(self, data, seed, clients_num):
        self.data = data
        self.seed = seed
        self.clients_num = clients_num

        self.data_size = None
        self.n_classes = None
        self.client_datasets = {}

    def data_split(self, test_size, y_name):
        train, test = train_test_split(self.data, random_state=self.seed, test_size=test_size, stratify=self.data[y_name])
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

    def get_distributed_dataset(self, test_size, y_name):
        self.data.rename(columns={y_name: "y"}, inplace=True)
        y_name = "y"
        train, test = self.data_split(test_size, y_name)
        min_class_num = min(train[y_name].value_counts().values)
        self.n_classes = self.data[y_name].nunique()
        self.data_size = len(self.data)
        label_dict = self.split_and_shuffle_labels(train[y_name].values, self.seed, min_class_num, self.n_classes) 

        clients_labels_dict = {}
        for labels, values in label_dict.items():
            a = np.array_split(values, self.clients_num)
            client_count = 0
            for i in a:
                try:
                    clients_labels_dict[client_count] = pd.concat([clients_labels_dict[client_count], i])
                except:
                    clients_labels_dict[client_count] = i
                client_count+=1

        for client in clients_labels_dict.keys():
            clients_labels_dict[client] = train.iloc[clients_labels_dict[client].i].sample(frac=1).reset_index(drop=True)

        self.client_datasets = clients_labels_dict

        return self.client_datasets, test