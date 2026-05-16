from flask import Flask, jsonify, request

app = Flask(__name__)

# ✅ Only ONE home route
@app.route('/')
def home():
    return jsonify(employees)

employees = [
    {'id': 1, 'name': 'Ashley'},
    {'id': 2, 'name': 'Kate'},
    {'id': 3, 'name': 'Joe'}
]

nextEmployeeId = 4


def get_employee(id):
    return next((e for e in employees if e['id'] == id), None)


def employee_is_valid(employee):
    for key in employee.keys():
        if key != 'name':
            return False
    return True


@app.route('/employees', methods=['GET'])
def get_employees():
    return jsonify(employees)


@app.route('/employees', methods=['POST'])
def create_employee():
    global nextEmployeeId
    employee = request.get_json()

    if not employee_is_valid(employee):
        return jsonify({'error': 'Invalid employee properties.'}), 400

    employee['id'] = nextEmployeeId
    nextEmployeeId += 1
    employees.append(employee)

    return jsonify(employee), 201


@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    employee = get_employee(id)

    if employee is None:
        return jsonify({'error': 'Employee does not exist.'}), 404

    updated_employee = request.get_json()

    if not employee_is_valid(updated_employee):
        return jsonify({'error': 'Invalid employee properties.'}), 400

    employee.update(updated_employee)
    return jsonify(employee)


@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    global employees
    employee = get_employee(id)

    if employee is None:
        return jsonify({'error': 'Employee does not exist.'}), 404

    employees = [e for e in employees if e['id'] != id]
    return jsonify(employee), 200


if __name__ == '__main__':
    app.run(port=5000)