from flask import Flask,jsonify, request

app = Flask(__name__)

transactions=[]

@app.route('/')
def home():
    return jsonify({
        "message" : "welcome to the finanace tracker api",
        "status" : "running"
    })
    
@app.route('/transactions', methods=['POST'])
def add_transaction():
    data=request.get_json()
    
    transaction={
        'id':len(transactions)+1,
        'title':data['title'],
        'amount':data['amount'],
        'type':data['type']
    }
    transactions.append(transaction)
    
    return jsonify({
        'message':"transaction added successfully",
        'transaction':transaction
    })
    
@app.route('/transactions',methods=['GET'])
def get_transactions():
    return jsonify({
        'transaction':transactions
    })
    
@app.route('/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    data=request.get_json()
    
    for transaction in transactions:
        if transaction['id']==id:
            transaction['title']=data.get('title',transaction['title'])
            transaction['amount']=data.get('amount',transaction['amount'])
            transaction['type']=data.get('type',transaction['type'])
            
            return jsonify({
                'message':"transaction updated successfully",
                'transaction':transaction
            })
        return jsonify({
            'message':"transaction not found"
        }), 400
            
@app.route('/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    
    for transaction in transactions:
        if transaction['id']==id:
            transactions.remove(transaction)
            return jsonify({
                'message':"transaction deleted successfully",
                'transaction':transactions
            })
        return jsonify({
            'message':"tranasaction not found"
        }), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)