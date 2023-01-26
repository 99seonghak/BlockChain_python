# 웹 개발
# server.py: Flask를 사용해 웹의 형태 개발
# /chain : 현재 블록체인 보여줌
# /transaction/new : 새 트랜잭션 생성
# /mine : server에게 새 블록 채굴 요청


from flask import Flask, jsonify
from uuid import uuid4
import requests

# Our blockchain.py API
from blockchain import Blockchain

    
app = Flask(__name__)
# Universial Unique Identifier

node_identifier = str(uuid4()).replace('-','') # 유효id 개개인 식별을 하기 위해 사용 (중복X) *지갑 주소

blockchain = Blockchain()

# /mine
# Coinbase transaction
@app.route('/mine',methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    
    proof = blockchain.pow(last_proof)
    
    blockchain.new_transaction(
        sender='0', # 채굴시 생성되는 트랜잭션
        recipient= node_identifier, # 해당 지갑주소로 보냄
        amount=1 # coinbase transaction *보상
    )
    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block) # 전 블록에 대한 hash
    block = blockchain.new_block(proof, previous_hash) # 앞의 블록과 같이 검증하고 블록을 새로 생성
    
    response = {
        'message' : 'new block found',
        'index' : block['index'],
        'transaction' : block['transactions'],
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash'] # 블록이 생성되었다는 메세지를 json형태로 띄워줌
    }
    return jsonify(response), 200

# /transaction/new
# POST 형식으로 데이터를 보냄
# 이때, *POST란? url에 데이터를 붙이는 GET방식과 다르게 숨겨서 보내는 방식
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = requests.get_json() # json형태를 받아서 저장
    
    required = ['sender', 'recipient', 'amount'] # 해당 데이터가 존재해야함 얼마를 보내는지 
    if not all(k in values for k in required): # 만약 해당 데이터가 없으면 에러 뜸 400
        return 'missing values', 400
    
    # Create a new Transaction
    index = blockchain.new_transcation(values['sender'], values['recipient'], values['amount'])
    response = {'message' : 'Transaction will be added to Block {%s}' % index}
    
    return jsonify(response), 201 # json 형태로 반환

# /chain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain, # 블록체인을 출력
        'length': len(blockchain.chain), # 블록체인 길이 출력
    }
    return jsonify(response), 200 # json 형태로 리턴
    # 200은 웹사이트 에러가 없을 때 뜸

# /nodes/register
@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = requests.get_json() # json 형태로 보내기
    
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    
    for node in nodes: # 노드 등록 *
        blockchain.register_node(node)
        
    response = {
        'message': 'New nodes have been added',
        'total_nodes':list(blockchain.nodes),
    }
    return jsonify(response), 201

# /nodes/resolve
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts() # True False return
    
    if replaced: # 체인 변경 알림 메시지
        response = {
            'message' : 'Our chain was replaced',
            'new_chain' : blockchain.chain
        }
    else:
        response = {
            'messagr' : 'Our chain is authoritative',
            'chain' : blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)