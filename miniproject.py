import sqlite3
import hashlib
import re
from datetime import datetime


# ============================================================
# DATABASE CONNECTION
# ============================================================

con = sqlite3.connect("bankmanagement.db")
c = con.cursor()

# Enable foreign key support
c.execute("PRAGMA foreign_keys = ON")


# ============================================================
# CREATE TABLES
# ============================================================

# 1. Registration Table
c.execute("""
CREATE TABLE IF NOT EXISTS registration (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")


# 2. Account Table
c.execute("""
CREATE TABLE IF NOT EXISTS account (
    account_no INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    account_type TEXT NOT NULL,
    balance REAL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES registration(user_id)
)
""")


# 3. Transactions Table
c.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_no INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    date_time TEXT NOT NULL,
    FOREIGN KEY (account_no) REFERENCES account(account_no)
)
""")

con.commit()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# EMAIL VALIDATION
# ============================================================

def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


# ============================================================
# USER REGISTRATION
# ============================================================

def register():

    print("\n" + "=" * 50)
    print("              USER REGISTRATION")
    print("=" * 50)

    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    if not username or not email or not password:
        print("All fields are required!")
        return

    if not valid_email(email):
        print("Invalid email format!")
        return

    if len(password) < 6:
        print("Password must contain at least 6 characters!")
        return

    hashed_password = hash_password(password)

    try:

        c.execute("""
        INSERT INTO registration (username, email, password)
        VALUES (?, ?, ?)
        """, (username, email, hashed_password))

        con.commit()

        print("\nRegistration successful!")
        print("You can now login.")

    except sqlite3.IntegrityError:
        print("\nUsername or email already exists!")


# ============================================================
# USER LOGIN
# ============================================================

def login():

    print("\n" + "=" * 50)
    print("                    LOGIN")
    print("=" * 50)

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    hashed_password = hash_password(password)

    c.execute("""
    SELECT user_id, username
    FROM registration
    WHERE username = ? AND password = ?
    """, (username, hashed_password))

    user = c.fetchone()

    if user:

        print("\nLogin successful!")
        print("Welcome,", username)

        user_id = user[0]

        customer_menu(user_id)

    else:

        print("\nInvalid username or password!")


# ============================================================
# GENERATE ACCOUNT NUMBER
# ============================================================

def generate_account_number():

    c.execute("""
    SELECT MAX(account_no)
    FROM account
    """)

    result = c.fetchone()[0]

    if result is None:
        return 100001

    return result + 1


# ============================================================
# CREATE BANK ACCOUNT
# ============================================================

def create_account(user_id):

    print("\n" + "=" * 50)
    print("              CREATE BANK ACCOUNT")
    print("=" * 50)

    # Check whether user already has an account
    c.execute("""
    SELECT account_no
    FROM account
    WHERE user_id = ?
    """, (user_id,))

    existing_account = c.fetchone()

    if existing_account:

        print("\nYou already have a bank account.")
        print("Account Number:", existing_account[0])
        return

    name = input("Enter your full name: ").strip()

    if not name:
        print("Name cannot be empty!")
        return

    try:

        age = int(input("Enter your age: "))

        if age < 18:
            print("You must be at least 18 years old.")
            return

    except ValueError:

        print("Please enter a valid age!")
        return

    print("\nAccount Types:")
    print("1. Savings")
    print("2. Current")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        account_type = "Savings"

    elif choice == "2":
        account_type = "Current"

    else:
        print("Invalid account type!")
        return

    account_no = generate_account_number()

    try:

        c.execute("""
        INSERT INTO account
        (account_no, user_id, name, age, account_type, balance)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (account_no, user_id, name, age, account_type, 0))

        con.commit()

        print("\nBank account created successfully!")
        print("Your Account Number:", account_no)
        print("Account Type:", account_type)

    except sqlite3.Error as e:

        print("Error creating account:", e)


# ============================================================
# GET ACCOUNT DETAILS
# ============================================================

def get_account(user_id):

    c.execute("""
    SELECT account_no, name, age, account_type, balance
    FROM account
    WHERE user_id = ?
    """, (user_id,))

    return c.fetchone()


# ============================================================
# VIEW ACCOUNT DETAILS
# ============================================================

def view_account(user_id):

    print("\n" + "=" * 50)
    print("              ACCOUNT DETAILS")
    print("=" * 50)

    account = get_account(user_id)

    if not account:

        print("No bank account found.")
        print("Please create an account first.")
        return

    account_no, name, age, account_type, balance = account

    print("Account Number :", account_no)
    print("Name           :", name)
    print("Age            :", age)
    print("Account Type   :", account_type)
    print("Balance        : ₹{:.2f}".format(balance))


# ============================================================
# CHECK BALANCE
# ============================================================

def check_balance(user_id):

    account = get_account(user_id)

    if not account:

        print("\nNo bank account found.")
        return

    account_no = account[0]
    balance = account[4]

    print("\n" + "=" * 50)
    print("                 BALANCE")
    print("=" * 50)

    print("Account Number :", account_no)
    print("Available Balance : ₹{:.2f}".format(balance))


# ============================================================
# DEPOSIT MONEY
# ============================================================

def deposit(user_id):

    print("\n" + "=" * 50)
    print("                DEPOSIT MONEY")
    print("=" * 50)

    account = get_account(user_id)

    if not account:

        print("No bank account found.")
        return

    account_no = account[0]
    current_balance = account[4]

    try:

        amount = float(input("Enter amount to deposit: ₹"))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:

        print("Please enter a valid amount!")
        return

    new_balance = current_balance + amount

    try:

        # Update balance
        c.execute("""
        UPDATE account
        SET balance = ?
        WHERE account_no = ?
        """, (new_balance, account_no))

        # Record transaction
        c.execute("""
        INSERT INTO transactions
        (account_no, transaction_type, amount, description, date_time)
        VALUES (?, ?, ?, ?, ?)
        """, (
            account_no,
            "DEPOSIT",
            amount,
            "Money deposited",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        con.commit()

        print("\nDeposit successful!")
        print("Deposited Amount : ₹{:.2f}".format(amount))
        print("New Balance      : ₹{:.2f}".format(new_balance))

    except sqlite3.Error as e:

        con.rollback()
        print("Transaction failed:", e)


# ============================================================
# WITHDRAW MONEY
# ============================================================

def withdraw(user_id):

    print("\n" + "=" * 50)
    print("               WITHDRAW MONEY")
    print("=" * 50)

    account = get_account(user_id)

    if not account:

        print("No bank account found.")
        return

    account_no = account[0]
    current_balance = account[4]

    try:

        amount = float(input("Enter amount to withdraw: ₹"))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:

        print("Please enter a valid amount!")
        return

    if amount > current_balance:

        print("\nInsufficient balance!")
        print("Available Balance: ₹{:.2f}".format(current_balance))
        return

    new_balance = current_balance - amount

    try:

        # Update balance
        c.execute("""
        UPDATE account
        SET balance = ?
        WHERE account_no = ?
        """, (new_balance, account_no))

        # Record transaction
        c.execute("""
        INSERT INTO transactions
        (account_no, transaction_type, amount, description, date_time)
        VALUES (?, ?, ?, ?, ?)
        """, (
            account_no,
            "WITHDRAW",
            amount,
            "Money withdrawn",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        con.commit()

        print("\nWithdrawal successful!")
        print("Withdrawn Amount : ₹{:.2f}".format(amount))
        print("Remaining Balance: ₹{:.2f}".format(new_balance))

    except sqlite3.Error as e:

        con.rollback()
        print("Transaction failed:", e)


# ============================================================
# MONEY TRANSFER
# ============================================================

def transfer_money(user_id):

    print("\n" + "=" * 50)
    print("                MONEY TRANSFER")
    print("=" * 50)

    sender_account = get_account(user_id)

    if not sender_account:

        print("No bank account found.")
        return

    sender_account_no = sender_account[0]
    sender_balance = sender_account[4]

    print("Your Account Number:", sender_account_no)

    try:

        receiver_account_no = int(
            input("Enter receiver account number: ")
        )

        amount = float(
            input("Enter amount to transfer: ₹")
        )

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:

        print("Please enter valid details!")
        return

    if receiver_account_no == sender_account_no:

        print("You cannot transfer money to your own account!")
        return

    # Check receiver account
    c.execute("""
    SELECT account_no, name, balance
    FROM account
    WHERE account_no = ?
    """, (receiver_account_no,))

    receiver = c.fetchone()

    if not receiver:

        print("Receiver account does not exist!")
        return

    if amount > sender_balance:

        print("Insufficient balance!")
        return

    receiver_balance = receiver[2]

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:

        # Deduct money from sender
        c.execute("""
        UPDATE account
        SET balance = ?
        WHERE account_no = ?
        """, (new_sender_balance, sender_account_no))

        # Add money to receiver
        c.execute("""
        UPDATE account
        SET balance = ?
        WHERE account_no = ?
        """, (new_receiver_balance, receiver_account_no))

        # Sender transaction
        c.execute("""
        INSERT INTO transactions
        (account_no, transaction_type, amount, description, date_time)
        VALUES (?, ?, ?, ?, ?)
        """, (
            sender_account_no,
            "TRANSFER",
            amount,
            "Transferred to account " + str(receiver_account_no),
            current_time
        ))

        # Receiver transaction
        c.execute("""
        INSERT INTO transactions
        (account_no, transaction_type, amount, description, date_time)
        VALUES (?, ?, ?, ?, ?)
        """, (
            receiver_account_no,
            "CREDIT",
            amount,
            "Received from account " + str(sender_account_no),
            current_time
        ))

        con.commit()

        print("\nTransfer successful!")
        print("Receiver         :", receiver[1])
        print("Transferred      : ₹{:.2f}".format(amount))
        print("Remaining Balance: ₹{:.2f}".format(new_sender_balance))

    except sqlite3.Error as e:

        con.rollback()
        print("Transfer failed:", e)


# ============================================================
# TRANSACTION HISTORY
# ============================================================

def transaction_history(user_id):

    print("\n" + "=" * 70)
    print("                    TRANSACTION HISTORY")
    print("=" * 70)

    account = get_account(user_id)

    if not account:

        print("No bank account found.")
        return

    account_no = account[0]

    c.execute("""
    SELECT transaction_id,
           transaction_type,
           amount,
           description,
           date_time
    FROM transactions
    WHERE account_no = ?
    ORDER BY transaction_id DESC
    """, (account_no,))

    transactions = c.fetchall()

    if not transactions:

        print("No transactions found.")
        return

    print(
        "{:<5} {:<12} {:<12} {:<30} {:<20}".format(
            "ID",
            "TYPE",
            "AMOUNT",
            "DESCRIPTION",
            "DATE"
        )
    )

    print("-" * 90)

    for transaction in transactions:

        transaction_id = transaction[0]
        transaction_type = transaction[1]
        amount = transaction[2]
        description = transaction[3]
        date_time = transaction[4]

        print(
            "{:<5} {:<12} ₹{:<10.2f} {:<30} {:<20}".format(
                transaction_id,
                transaction_type,
                amount,
                description,
                date_time
            )
        )


# ============================================================
# VIEW PROFILE
# ============================================================

def view_profile(user_id):

    print("\n" + "=" * 50)
    print("                  MY PROFILE")
    print("=" * 50)

    c.execute("""
    SELECT username, email
    FROM registration
    WHERE user_id = ?
    """, (user_id,))

    user = c.fetchone()

    if not user:

        print("User not found.")
        return

    print("Username :", user[0])
    print("Email    :", user[1])


# ============================================================
# UPDATE PROFILE
# ============================================================

def update_profile(user_id):

    print("\n" + "=" * 50)
    print("                UPDATE PROFILE")
    print("=" * 50)

    c.execute("""
    SELECT username, email
    FROM registration
    WHERE user_id = ?
    """, (user_id,))

    user = c.fetchone()

    if not user:

        print("User not found.")
        return

    print("Current Username:", user[0])
    print("Current Email   :", user[1])

    print("\nLeave blank to keep the current value.")

    new_username = input("Enter new username: ").strip()
    new_email = input("Enter new email: ").strip()

    if not new_username:
        new_username = user[0]

    if not new_email:
        new_email = user[1]

    if not valid_email(new_email):

        print("Invalid email format!")
        return

    try:

        c.execute("""
        UPDATE registration
        SET username = ?, email = ?
        WHERE user_id = ?
        """, (new_username, new_email, user_id))

        con.commit()

        print("\nProfile updated successfully!")

    except sqlite3.IntegrityError:

        print("Username or email already exists!")


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

def customer_menu(user_id):

    while True:

        print("\n" + "=" * 50)
        print("             CUSTOMER DASHBOARD")
        print("=" * 50)

        print("1. Create Bank Account")
        print("2. View Account Details")
        print("3. Check Balance")
        print("4. Deposit Money")
        print("5. Withdraw Money")
        print("6. Transfer Money")
        print("7. Transaction History")
        print("8. View Profile")
        print("9. Update Profile")
        print("10. Logout")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            create_account(user_id)

        elif choice == "2":
            view_account(user_id)

        elif choice == "3":
            check_balance(user_id)

        elif choice == "4":
            deposit(user_id)

        elif choice == "5":
            withdraw(user_id)

        elif choice == "6":
            transfer_money(user_id)

        elif choice == "7":
            transaction_history(user_id)

        elif choice == "8":
            view_profile(user_id)

        elif choice == "9":
            update_profile(user_id)

        elif choice == "10":

            print("\nLogged out successfully!")
            break

        else:

            print("\nInvalid choice! Please try again.")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print("\n" + "=" * 50)
        print("          BANK MANAGEMENT SYSTEM")
        print("=" * 50)

        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            register()

        elif choice == "2":

            login()

        elif choice == "3":

            print("\nThank you for using Bank Management System!")
            break

        else:

            print("\nInvalid choice! Please enter 1, 2 or 3.")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print("\n\nProgram interrupted.")

    finally:

        con.close()