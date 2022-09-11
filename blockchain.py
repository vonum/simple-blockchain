import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests

from block.block import Block

class Blockchain:
  def __init__(self):
    self.chain = []
    self.mempool = []
    self.nodes = set()

    self.create_block(1, "0")

  def create_block(self, proof, previous_hash):
    block = Block(len(self.chain) + 1,
                  str(datetime.datetime.now()),
                  proof,
                  previous_hash,
                  self.mempool)
    """
    block = {
      "index": len(self.chain) + 1,
      "timestamp": str(datetime.datetime.now()),
      "proof": proof,
      "previous_hash": previous_hash,
      "transactions": self.mempool
    }
    """
    self.mempool = []
    self.chain.append(block)

    return block

  def length(self):
    return len(self.chain)

  def mempool_length(self):
    return len(self.mempool)

  def previous_block(self):
    return self.chain[-1]

  def proof_of_work(self, previous_proof):
    new_proof = 1
    check_proof = False

    while (not check_proof):
      hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()

      if (hash_operation[:4] == "0000"):
        check_proof = True
      else:
        new_proof += 1

    return new_proof

  def hash(self, block):
    # encoded_block = json.dumps(block, sort_keys=True).encode()
    encoded_block = block.to_string().encode()
    return hashlib.sha256(encoded_block).hexdigest()

  def is_chain_valid(self, chain):
    previous_block = chain[0]
    block_index = 1

    while (block_index < self.length()):
      block = self.chain[block_index]
      if (block.previous_hash != self.hash(previous_block)):
        return False

      previous_proof = previous_block.proof
      proof = block.proof

      hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()

      if (hash_operation[:4] != "0000"):
        return False

      previous_block = block
      block_index += 1

    return True

  def add_transaction(self, tx):
    self.mempool.append(tx)
    return self.previous_block().index + 1

  def add_nodes(self, node_urls):
    self.nodes = self.nodes.union(node_urls)
    return self.nodes

  def sync_chain(self):
    longest_chain = self.chain
    max_length = len(self.chain)

    for node in self.nodes:
      resp = requests.get(f"{node}/chain").json()
      chain = resp["chain"]
      length = resp["length"]

      if (self.is_chain_valid(chain) and length > len(longest_chain)):
        longest_chain = chain
        max_length = length

    self.chain = longest_chain