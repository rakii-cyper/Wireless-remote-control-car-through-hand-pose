import pandas as pd
import numpy as np
import os


def merge_dataset(path):
    dataset = os.listdir(path)
    merged_dataset = None

    for d in dataset:
        file_path = os.path.join(path, d)
        df = pd.read_csv(file_path, sep=',')
        df.drop_duplicates(inplace=True)

        if merged_dataset is None:
            merged_dataset = df
        else:
            merged_dataset = pd.concat([merged_dataset, df], ignore_index=True)

    return merged_dataset


def dataset_reader(df):
    y_train = df['class'].squeeze().array
    x_train = np.ndarray((len(df.index), 42), dtype=np.int64)

    count = 0
    for i in range(df.index[-1]):
        temp = df.loc[i].squeeze().array[1:]
        x_train[count] = temp
        count += 1

    return y_train, x_train


def preprocess_lm_list(lm_list):
    if not len(lm_list):
        return False

    count = 0
    temp = []

    for i in range(21):
        if i == lm_list[count][0]:
            temp.append(lm_list[count][1])
            temp.append(lm_list[count][2])
            if count + 1 < len(lm_list):
                count += 1
        else:
            temp.append(0)
            temp.append(0)

    return np.array(temp)
