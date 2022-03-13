from retry import retry
from web3 import Web3
import argparse
import requests
import csv
import time
import json


class MetadataReader:
    def __init__(self, provider, abi, contract, csv_file) -> None:
        self.provider = Web3.HTTPProvider(provider)
        self.contract = Web3(self.provider).eth.contract(address=contract, abi=abi)
        self.metadatas = []
        self.trait_types = []
        self.baseURI = self.contract.functions['baseURI']().call()[7:-1]
        self.start_token_id = 0
        self.end_token_id = 100
        # self.contract.functions['totalSupply'].call()
        self.total_supply = 300
        self.csv_file = csv_file

        print(f"self.provider = {self.provider}")
        print(f"self.contract = {self.contract}")
        print(f"self.baseURI = {self.baseURI}")
        print(f"self.csv_file = {self.csv_file}")

    def get_metadata(self, tokenURI):
        request_url = f"https://ipfs.io/ipfs/{tokenURI}"
        get_metadata_response = requests.get(request_url)
        metadata_json = get_metadata_response.json()
        return metadata_json

    def update_trait_types(self, metadata_json):
        for attribute in metadata_json['attributes']:
            trait_type = attribute['trait_type']
            if not trait_type in self.trait_types:
                self.trait_types.append(trait_type)

    def create_trait_type_to_value(self, metadata_json) -> dict:
        trait_type_to_value = {}

        for attribute in metadata_json['attributes']:
            trait_type = attribute['trait_type']
            trait_value = attribute['value']
            trait_type_to_value[trait_type] = trait_value

        return trait_type_to_value

    def return_trait_row(self, trait_type_to_value) -> list:
        trait_row = []
        for trait_type in self.trait_types:
            if trait_type in trait_type_to_value:
                trait_row.append(trait_type_to_value[trait_type])
            else:
                trait_row.append("")

        return trait_row

    def process_metadata(self, tokenURI) -> list:
        metadata_json = self.get_metadata(tokenURI)
        self.update_trait_types(metadata_json)
        trait_type_to_value = self.create_trait_type_to_value(metadata_json)

        return self.return_trait_row(trait_type_to_value)

    def process_metadatas_in_increment_of_100(self):
        temp_metadatas = []
        for tokenId in range(self.start_token_id, self.end_token_id):
            tokenURI = f"{self.baseURI}/{tokenId}"
            trait_row = self.process_metadata(tokenURI)
            temp_metadatas.append(trait_row)
            print(f"FIRST - Token Id = {tokenId}")

        return temp_metadatas

    def populate_partial_metadatas(self):
        get_metadata_start_time = time.time()
        while self.start_token_id < self.total_supply:
            print ("we're here")
            temp_metadatas = []
            temp_metadatas = self.process_metadatas_in_increment_of_100()

            self.metadatas += temp_metadatas

            self.start_token_id += 100
            self.end_token_id += 100
        get_metadata_end_time = time.time()
        print(f"Duration of getting metadata: {get_metadata_end_time - get_metadata_start_time}")

    def populate_csv(self):
        with open(self.csv_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(self.trait_types)
            count = 0
            add_csv_start_time = time.time()
            for metadata in self.metadatas:
                csv_writer.writerow(metadata)
                print(f"FINAL - Token Id = {count}")
                count += 1
            add_csv_end_time = time.time()
        print(
            f"Duration of adding to csv: {add_csv_end_time - add_csv_start_time}")


    def start(self):
        self.populate_partial_metadatas()
        self.populate_csv()


def main(args):
    collection_json_file = args.collection
    csv_file = args.csv_file

    with open(collection_json_file) as collection:
        data = json.load(collection)
        address = data['address']
        abi = data['abi']
        provider = data['provider']

        metadata_reader = MetadataReader(
            provider=provider, abi=abi, contract=address, csv_file=csv_file)

        metadata_reader.start()


def parse_arg():
    parser = argparse.ArgumentParser(
        description='Reads metadata for a collection, and exports a csv file.')
    parser.add_argument('collection')
    parser.add_argument('csv_file')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arg()
    main(args)
