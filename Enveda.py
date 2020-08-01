import requests
import lxml.html as lh
import pandas as pd
import numpy as np
from collections import defaultdict
import json
import time

# sleep not initiated with every response considering it is not a real time webpage.
# the code is little laggy but can be sped using multithreading.
# encoder used to convert set structure to list as set values cannot be dumped as json.


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


# class used for parsing
class Enveda_parser:
    def __init__(self, url):
        self.pages = np.arange(0, 440, 20)
        self.chemicals = defaultdict(set)
        self.url = url
        self.second_dic = {}

    # extracting tables using xpath
    def first_dictionary(self):
        links = self.get_url_list()
        for link in links:
            tree = lh.fromstring(requests.get(link).content)
            for row in tree.xpath("//table[@class='resultstable']//tr")[1:]:
                chemical_name = row.xpath('td//text()')[1]
                trivial_name = row.xpath('td//text()')[2]
                formula = row.xpath('td//text()')[3]
                mol_weight = row.xpath('td//text()')[5]
                self.chemicals.update({chemical_name: {
                    'trivial_names': trivial_name,
                    'formula': formula,
                    'molecular_weight': mol_weight}})
        return self.chemicals

    # generating url list
    def get_url_list(self):
        url_list = []
        split_url = self.url.split('from=0')
        for page in self.pages:
            link = 'from=' + str(page)
            url_list.append(link.join(split_url))
        return url_list

    # getting unique chemical names to query by sending request
    def unique_chemical_names(self):
        l = set()
        links = self.get_url_list()
        for link in links:
            response = requests.get(link)
            tree = lh.fromstring(response.content)
            for row in tree.xpath("//table[@class='resultstable']//tr")[1:]:
                l.add(row.xpath('td//text()')[4])
        return l

    # function used to generate dictionary using sets as required for second test case
    def second_dictionary(self):
        l = self.unique_chemical_names()
        d = defaultdict(set)
        for query in l:
            response = requests.get('http://alkamid.ugent.be/alkamidresults.php?query=' + query)
            tree = lh.fromstring(response.content)
            for row in tree.xpath("//table[@class='resultstable']//tr")[1:]:
                chemical_name = row.xpath('td//text()')[1]
                d[query].add(chemical_name)
        return d

    def unique_plant_chemical(self, data):
        count = 0
        k = data.T
        for i in k.columns:
            c = k[i].dropna()
            count += len(c)
        return count

    def mean_and_std(self, data):
        l = data.T
        m = []
        for i in l.columns:
            c = l[i].dropna()
            m.append('mean of ' + i + ':' + str(np.mean(len(c))) + ' and standard deviation :' + str(np.std(len(c))))
        return m

    def string_max_legth(self, data):
        c = data.values
        res = max(c, key=len)
        return res

    # seperate function for dictionary 2 as sets cannot be dumped as json
    def return_json1(self, file_name, data):
        with open(file_name + '.json', 'w') as outfile:
            json.dump(data, outfile, indent=1, cls=SetEncoder)

    def return_json(self, file_name, data):
        with open(file_name + '.json', 'w') as outfile:
            json.dump(data, outfile, indent=1)

    # main function to run all process
    def main_function(self):
        print('Please enter a serial number to execute the function \n1. Function to return dictionary 1 \n2. Function to return dictionary 2\
                 \n3. Function to save the json files  \n4. To print Statistics ')
        input_arg = input('>>')
        if input_arg == '1':
            t0 = time.time()
            print('[+]The Function might take some time to load, Please be patient')
            Dictionary_case1 = self.first_dictionary()
            print(Dictionary_case1)

        if input_arg == '2':
            print('[+]The Function might take some time to load, Please be patient')
            Dictionary_case2 = self.second_dictionary()
            print(Dictionary_case2)

        if input_arg == '3':
            file_1 = input('[+] Please enter the name for first input file :')
            data1 = self.first_dictionary()
            self.return_json(file_1, data1)
            print('[+] First json dictionary Downloaded')
            file_2 = input('[+] Please enter the name for second input file :')
            data2 = self.second_dictionary()
            self.return_json1(file_2, data2)
            print('[+] Second json dictionary Downloaded')

        if input_arg == '4':
            print('[+] Retrieving data from Dataframes, please be patient')
            df1 = self.first_dictionary()
            time.sleep(0.25)
            df2 = self.second_dictionary()
            data_dict1 = pd.DataFrame.from_dict(df1, orient='index')
            data_dict2 = pd.DataFrame.from_dict(df2, orient='index')
            print("The number of unique plants: {}".format(len(data_dict2.index) - 1))
            print("The number of unique Chemicals: {}".format(len(data_dict1.index.unique())))
            unique_plant_chemical_count = self.unique_plant_chemical(data_dict2)
            print("The number of unique plant chemical pairs: {}".format(unique_plant_chemical_count))
            mean_and_std = self.mean_and_std(data_dict2)
            print("The mean and standard deviation of chemicals per plant: {}".format(mean_and_std))
            long_string = self.string_max_legth(data_dict1.index)
            print("The longest chemical name: {}".format(long_string))










