from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import date

app = Flask(__name__)

# ─── DB CONNECTION ─────────────────────────────────────────────────────────────
# Table names in your database (all lowercase):
#   customer, account, transaction, loan, loan_payment,
#   branch, employee, user_login, card, beneficiary

def get_connection():
    return mysql.connector.connect(
        host="zd8sp5.h.filess.io",
        port=3306,
        user="bank_db_beyondbut",
        password="8e5b8764ca60e2fbd22a87017a9c4c4814a1ba",
        database="bank_db_beyondbut"
    )

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ─── CUSTOMER ──────────────────────────────────────────────────────────────────

@app.route("/api/customer", methods=["POST"])
def add_customer():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customer (Name, Address, Date_of_Birth, Contact_Number, Email_ID, Identification_Proof)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (d["name"], d["address"], d["dob"], d["contact"], d["email"], d["id_proof"]))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "Customer added successfully", "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/customer", methods=["GET"])
def get_customers():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer ORDER BY Customer_ID DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── ACCOUNT ───────────────────────────────────────────────────────────────────

@app.route("/api/account", methods=["POST"])
def create_account():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO account (Account_Type, Opening_Date, Balance, Customer_ID, Branch_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (d["account_type"], d["opening_date"], d["balance"], d["customer_id"], d["branch_id"]))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "Account created successfully", "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/account", methods=["GET"])
def get_accounts():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM account ORDER BY Account_Number DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── TRANSACTION ───────────────────────────────────────────────────────────────
# Note: `transaction` is a reserved word in MySQL so we use backticks

@app.route("/api/transaction", methods=["POST"])
def add_transaction():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO `transaction` (Transaction_Type, Transaction_Date, Amount, Account_Number)
            VALUES (%s, CURDATE(), %s, %s)
        """, (d["transaction_type"], d["amount"], d["account_number"]))

        if d["transaction_type"] == "Deposit":
            cursor.execute("UPDATE account SET Balance = Balance + %s WHERE Account_Number = %s",
                           (d["amount"], d["account_number"]))
        else:
            cursor.execute("UPDATE account SET Balance = Balance - %s WHERE Account_Number = %s",
                           (d["amount"], d["account_number"]))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Transaction completed successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/transaction", methods=["GET"])
def get_transactions():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `transaction` ORDER BY Transaction_ID DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── LOAN ─────────────────────────────────────────────────────────────────────

@app.route("/api/loan", methods=["POST"])
def apply_loan():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loan (Loan_Type, Loan_Amount, Interest_Rate, Loan_Tenure, Customer_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (d["loan_type"], d["loan_amount"], d["interest_rate"], d["loan_tenure"], d["customer_id"]))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "Loan applied successfully", "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/loan", methods=["GET"])
def get_loans():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM loan ORDER BY Loan_ID DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── LOAN PAYMENT ──────────────────────────────────────────────────────────────

@app.route("/api/loan-payment", methods=["POST"])
def loan_payment():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loan_payment (Payment_Date, Payment_Amount, Loan_ID)
            VALUES (CURDATE(), %s, %s)
        """, (d["payment_amount"], d["loan_id"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Loan payment recorded successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── BRANCH ────────────────────────────────────────────────────────────────────
# Branch_ID is AUTO_INCREMENT in your DB, so we don't insert it manually

@app.route("/api/branch", methods=["POST"])
def add_branch():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO branch (Branch_Name, IFSC_Code, Location, Contact_Number)
            VALUES (%s, %s, %s, %s)
        """, (d["branch_name"], d["ifsc_code"], d["location"], d["contact_number"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Branch added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/branch", methods=["GET"])
def get_branches():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM branch ORDER BY Branch_ID DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── EMPLOYEE ──────────────────────────────────────────────────────────────────

@app.route("/api/employee", methods=["POST"])
def add_employee():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employee (Name, Designation, Salary, Contact_Number, Branch_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (d["name"], d["designation"], d["salary"], d["contact"], d["branch_id"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Employee added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/employee", methods=["GET"])
def get_employees():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee ORDER BY Employee_ID DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── USER LOGIN ────────────────────────────────────────────────────────────────
# Table is `user_login` (lowercase) with UNIQUE constraint on Username

@app.route("/api/user", methods=["POST"])
def add_user():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_login (Username, Password, Role)
            VALUES (%s, %s, %s)
        """, (d["username"], d["password"], d["role"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User created successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── CARD ──────────────────────────────────────────────────────────────────────
# Card_Number is a BIGINT primary key (not auto increment), entered manually

@app.route("/api/card", methods=["POST"])
def add_card():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO card (Card_Number, Card_Type, Issue_Date, Expiry_Date, Account_Number)
            VALUES (%s, %s, %s, %s, %s)
        """, (d["card_number"], d["card_type"], d["issue_date"], d["expiry_date"], d["account_number"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Card issued successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/card", methods=["GET"])
def get_cards():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM card ORDER BY Card_Number DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── BENEFICIARY ───────────────────────────────────────────────────────────────
# Beneficiary_ID is AUTO_INCREMENT, so we don't insert it manually

@app.route("/api/beneficiary", methods=["POST"])
def add_beneficiary():
    try:
        d = request.json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO beneficiary (Beneficiary_Name, Bank_Name, Beneficiary_Account_Number, IFSC_Code, Customer_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (d["beneficiary_name"], d["bank_name"], d["beneficiary_account"], d["ifsc_code"], d["customer_id"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Beneficiary added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/beneficiary", methods=["GET"])
def get_beneficiaries():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM beneficiary ORDER BY Beneficiary_ID DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ─── STATS ─────────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        stats = {}
        for table, key in [("customer","customer"), ("account","account"), ("loan","loan"), ("employee","employee")]:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
            stats[key] = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COALESCE(SUM(Balance),0) as total FROM account")
        stats["total_balance"] = float(cursor.fetchone()["total"])
        conn.close()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))