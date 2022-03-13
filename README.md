# metadata-csv

1. use opensea API (or other ethereum APIs) to get the list of all the tokens for a given contract (totalSupply())
2. Iterate through the list of tokens and for each token: call: tokenURI()
3. get the address: ex: ipfs://QmYGgEFqTRkWvNZ6u7gfk9HDdh55bQAbYVyc16TF1zX658/69
4. make GET request to: https://ipfs.io/ipfs/{address that we fetched via tokenURI()}
5. convert the JSON data to csv data
6. insert into the csv data array


the data returns json with random order of `attribute_type`s. 
we want a uniform order 
