# https://github.com/dovishwisdom/wisdom_coin
#
# Hackernoon의 Daniel Van Flymen 코드를 리뷰
# 먼저 python으로 블록체인을 구현하기 전에 
# 블록체인 구조를 알아보기
# 파이썬 언어
# 리눅스 환경
# 파이썬 2.7 이상

# 블록체인의 구조?
# 최초의 블록부터 시작해 바로 앞의 블록에 대한 링크를 가지고 있는 형태
# 여러 노드들이 같은 정보, 장부를 갖는지 확인을 함!

# 블록체인의 특징
# 1. 블록체인의 구조
# 트랜잭션
# 전의 블록 해시
# 타임 스탬프
# [ Index      ] 몇번째 블록인지
# [ Timestamp  ] 언제 블록이 생성되었는지
# [ Transation ] 거래 목록
# [ Proof      ] 마이닝의 결과
# [ Prev_hash  ] 블록의 무결성 이해
# 2. 합의 과정
# 분산화된 환경에서 자료 동기화
# (어떻게 이 자료, 장부들이 분산화된 환경에서 갖고 있고 똑같은걸 같고 있구나를 합의할 수 있는지를 봄)

# 블록체인 blockchain.py - 블록구조들, 트랜잭션의 형태, chain과 연결법이 있음
# 서버 server.py - Flask를 사용해 웹의 형태 개발 (이렇게 짠 블록들을 어떻게 나눠줄지, Flask를 사용해서 웹페이지에 뿌림)

import hashlib # 해시의 sha256 사용 가능
import json
from time import time
from urlparse import urlparse
import requests
# 먼저 함수 지정 (함수의 형태만 크게 잡아보자!)
# JSON 형태로 유용하게 저장
# 컴퓨터가 이해하기 쉽게 리스트 방식으로 함. [JSON]
# JavaScriptObjectNotation
# "속성-값"의 쌍으로 이루어진 형식으로 자료를 표현하는 개방형 표준 형식
class Blockchain(object):
## __init__: 클래스의 생성자{Constructor},
# 가장 먼저 Blockchain 객체를 만들면 해당 함수가 무조건 먼저 실행되어짐
# ''' 블록을 저장한 공간 생성 및  트랜잭션 임시공간 생성 '''
    def __init__(self):
        self.chain = [] # 블록체인, 블록이 하나씩 들어감 배열형태로 저장
        self.current_transaction = [] # 임시 트랜잭션이 들어감, Alice가 bob에게 얼마를 줬다 거래내역
    
        # genesis block 첫번째 블록, 가장 첫번째 블록에 hash를 지정해두고
        self.new_block(previous_hash= 1, proof=100)  # Genesis block 생성
    
    # new_block 함수 생성 [사전 형태로 작성, key, value의 쌍]
    def new_block(self, proof, previous_hash=None):
        block = {
            'index' : len(self.chain)+1,
            'timestamp' : time(), # timestamp from 1970
            'transactions' : self.current_transaction,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
            }
        self.current_transaction = []
        self.chain.append(block) # chain에 블록을 삽입
        return block

    # 거래 추가 구조
    # new_Transaction을 하고 새로운 마인을 하면 그때 다음 블록의 Transaction이 들어가는 형태
    def new_transaction(self, sender, recipient, amount):
        self.current_transaction.append( # current_transaction에 트랜잭션 내용 삽입
            {
                'sender' : sender, # 송신자
                'recipient' : recipient, # 수신자
                'amount' : amount # 금액
                }
            )
        return self.last_block['iedex'] + 1

    # 해시
    def hash(block): # python의 sha256함수를 빌려쓰기
        block_string = json.dumps(block, sort_keys=True).encode()
        # 해시라는 함수를 어떨때 직접 짜냐? - json형태로 뽑혀진 블록을 전체 해쉬하기 위해서!
        return hashlib.sha256(block_string).hexdigest() # 무결성 체크하며 저장

    # 작업증명
    # 전 proof p와 현재 구해야할 proof p' hash[p+p']의 앞 4자리 == "0000" 이러한 p'를 구함
    def pow(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False: # 전 proof와 현재 기존 proof 합이 False일 때 까지 반복.
            proof += 1 # proof를 증가시킴.
            return proof # 찾으면 proof 반환.

    def valied_proof(last_proof,proof): # 앞의 4자리가 0000을 찾는 함수
        guess = str(last_proof + proof).encode() # 전 proof와 다음 proof 문자열 연결
        guess_hash = hashlib.sha256(guess).hexdigest() # 이 hash값 저장
        return guess_hash[:4] == "0000" # nonce 앞 4자리가 "0000"이면 True