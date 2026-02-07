from database import connect_to_database
import random
import string

# Encoding and verifying PINs using SHA-256 hashing for security
def hash_pin(pin):
    import hashlib
    return hashlib.sha256(pin.encode()).hexdigest()


def verify_pin(pin, hashed_pin):
    import hashlib
    return hashlib.sha256(pin.encode()).hexdigest() == hashed_pin


# Databse initialization to create necessary tables if they don't exist

def initialize_database():

    connection = connect_to_database()
    if not connection:
        print("Failed to connect to the database. Exiting.")
        return False

    try:
        cursor = connection.cursor()
        create_accounts_table = """
        CREATE TABLE IF NOT EXISTS accounts (
        account_number VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        pin VARCHAR(65) NOT NULL,
        balance DECIMAL(15, 2) DEFAULT 0.00,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_audit_table = """
        CREATE TABLE IF NOT EXISTS audit (
        iD SERIAL PRIMARY KEY,
        account_number VARCHAR(50),
        holder_name VARCHAR(100),
        action VARCHAR(50) NOT NULL,
        amount DECIMAL(15, 2) DEFAULT 0.00,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_number) REFERENCES accounts(account_number) ON DELETE CASCADE
        );
        """
    
        cursor.execute(create_accounts_table)
        cursor.execute(create_audit_table)
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print("Error initializing the database:", e)
        return False



# ACCOUTN class
class Account:
    def __init__(self,name="",account_number="",pin=""):
        self.account_number = (
            account_number if account_number else self.__generate_account_number()
        )
        self.name = name
        self.pin = hash_pin(pin) if pin else None
        self.balance = 0.00

    @staticmethod
    def __generate_account_number():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    #Getters 
    def get_account_number(self):
        return self.account_number
    def get_name(self):
        return self.name
    def get_balance(self):
        return self.balance
    def get_pin(self):
        return self.pin
    
    #Setters
    def set_name(self, name):
        self.name = name
    def set_pin(self, pin):
        self.pin = hash_pin(pin)
    def set_balance(self, balance):
        self.balance = balance
    
    # UTILIY METHODS
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False
    
    # Databse operations
    @classmethod
    def load_from_db(cls, account_number, pin):
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return None

        try:
            cursor = connection.cursor()
            query = "SELECT account_number ,name, pin, balance FROM accounts WHERE account_number = %s"
            cursor.execute(query, (account_number,))
            result = cursor.fetchone()
            if result:
                stored_pin_hash = result[2]
                if verify_pin(pin, stored_pin_hash):
                    account = cls(result[1], result[0], pin)
                    account.set_balance(float(result[3]))
                    return account
        except Exception as e:
            print("Error loading account from database:", e)
        finally:
            cursor.close()
            connection.close()

    def save_to_db(self):
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO accounts (account_number, name, pin, balance)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (account_number) DO UPDATE
            SET name = EXCLUDED.name,
                pin = EXCLUDED.pin,
                balance = EXCLUDED.balance;
            """
            cursor.execute(query, (self.account_number, self.name, self.pin, self.balance))
            connection.commit()
            return True
        except Exception as e:
            print("Error saving account to database:", e)
            return False
        finally:
            cursor.close()
            connection.close()
    
    def delete_to_db(self):
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM audit WHERE account_number = %s", (self.account_number,))
            cursor.execute("DELETE FROM accounts WHERE account_number = %s", (self.account_number,))
            connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Error deleting account from database:", e)
            return False
        finally:
            cursor.close()
            connection.close()


# Audit Class

class Audit:
    @staticmethod
    def log_action(account_number, holder_name, action, amount=0.00):
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO audit (account_number, holder_name, action, amount)
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (account_number, holder_name, action, amount))
            connection.commit()
            return True
        except Exception as e:
            print("Error logging audit action:", e)
            return False
        finally:
            cursor.close()
            connection.close()   
    

    @staticmethod
    def get_sigle_audit_logs(account_number):
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            query = "SELECT id, holder_name, action, amount, timestamp FROM audit WHERE account_number = %s ORDER BY timestamp DESC"
            cursor.execute(query, (account_number,))
            results = cursor.fetchall()
            logs = []
            for row in results:
                logs.append({
                    "id": row[0],
                    "holder_name": row[1],
                    "action": row[2],
                    "amount": float(row[3]),
                    "timestamp": row[4]
                })
            return logs
        except Exception as e:
            print("Error retrieving audit logs:", e)
            return []
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_all_audit_logs():
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            query = "SELECT id, holder_name, action, amount, timestamp FROM audit  ORDER BY timestamp DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            logs = []
            for row in results:
                logs.append({
                    "id": row[0],
                    "holder_name": row[1],
                    "action": row[2],
                    "amount": float(row[3]),
                    "timestamp": row[4]
                })
            return logs
        except Exception as e:
            print("Error retrieving audit logs:", e)
            return []
        finally:
            cursor.close()
            connection.close()


    @staticmethod
    def clear_sigle_audit_logs(account_number):
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            query = "DELETE FROM audit WHERE account_number = %s"
            cursor.execute(query, (account_number,))
            connection.commit()
            return True
        except Exception as e:
            print("Error clearing audit logs:", e)
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def clear_all_audit_logs():
        connection = connect_to_database()
        if not connection:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = connection.cursor()
            query = "DELETE FROM audit"
            cursor.execute(query)
            connection.commit()
            return True
        except Exception as e:
            print("Error clearing audit logs:", e)
            return False
        finally:
            cursor.close()
            connection.close()
             


# Banking System Class
class BankingSystem:
    def __init__(self):
        initialize_database()

    def create_account(self, name, pin):
        account = Account(name, "", pin)
        if account.save_to_db():
            Audit.log_action(account.get_account_number(), account.get_name(), "Account Created",0.00)
            return account
        return None
    
    def read_account(self, account_number, pin):
        account = Account.load_from_db(account_number, pin)
        if account:
            Audit.log_action(account_number, account.get_name(), "Details Checked",0.00)
            return account
        return None
    
    def update_account(self,account):
       return account.save_to_db()
     
    def delete_account(self, account_number, pin):
        account = Account.load_from_db(account_number, pin)
        if account:
            success = account.delete_to_db()
            if success:
                Audit.log_action(account_number, account.get_name(), "Account Deleted",0.00)
                return True
            
        return False
    

    def deposit(self, account_number, pin,amount):
        account = Account.load_from_db(account_number, pin)
        if account and account.deposit(amount):
            if account.save_to_db():
                Audit.log_action(account_number, account.get_name(), "Amount Deposited",amount)
                return True
        return None
    
    def withdraw(self, account_number, pin, amount):
        account = Account.load_from_db(account_number, pin)
        if account and account.withdraw(amount):
            if account.save_to_db():
                Audit.log_action(account_number, account.get_name(), "Amount Withdrawn",amount)
                return True
        return None
    
    def get_account_balance(self, account_number, pin):
        account = Account.load_from_db(account_number, pin)
        if account:
            Audit.log_action(account_number, account.get_name(), "Balance Checked",0.00)
            return account.get_balance()
        return None
    

    def get_one_audit_logs(self, account_number):
        return Audit.get_sigle_audit_logs(account_number)
    
    def get_allThe_audit_logs(self):
        return Audit.get_all_audit_logs()
    
    def clear_single_audit_logs(self, account_number):
        return Audit.clear_sigle_audit_logs(account_number)
    
    def clear_all_audit_logs(self):
        return Audit.clear_all_audit_logs()
    

def get_valid_amount(prompt):
    while True:
        try:
            amount = float(input(prompt))
            if amount < 0:
                print("Amount must be positive. Please try again.")
                continue
            else:
                return amount
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


# CLI Menu functions
# create account CLI 
def create_account_cli(bank):
    print("\n--- Create Account ---")
    name = input("Enter your name: ").strip()
    if not name:
        print("Name cannot be empty. Please try again.")
        input("Press Enter to continue...")
        return
    pin = input("Enter your PIN: ").strip()
    if len(pin) != 4 or not pin.isdigit():
        print("PIN cannot be less than 4 digits or contain non-numeric characters. Please try again.")
        input("Press Enter to continue...")
        return
    
    confirm_pin = input("Confirm your PIN: ").strip()
    if confirm_pin != pin:
        print("PINs do not match. Please try again.")
        input("Press Enter to continue...")
        return

    account = bank.create_account(name, pin)
    if account:
        print(f"Account created successfully! Your account number is: {account.get_account_number()}")
        print("Please keep your account number and PIN safe.")
       
    else:
        print("Failed to create account. Please try again.")
        input("Press Enter to continue...")
    
# Chack balance CLI
def check_balance_cli(bank, account, pin):
    print("=" * 30)
    print("\n--- Check Balance ---")
    print("=" * 30)
    balance = bank.get_account_balance(account.get_account_number(), pin)
    if balance is not None:
        print(f"Your current balance is: ${balance:.2f}")
    else:
        print("Failed to retrieve balance. Please try again.")

def deposit_money_cli(bank, account, pin):
    print("\n--- Deposit Money ---")
    print("=" * 30)
    amount = get_valid_amount("Enter the amount to deposit: $")
    if bank.deposit(account.get_account_number(), pin, amount):
        print(f"Successfully deposited ${amount:.2f}.")
        balance = bank.get_account_balance(account.get_account_number(), pin)
        if balance is not None:
            print(f"Your current balance is: ${balance:.2f}")
    else:
        print("Failed to deposit money. Please try again.")
    
    
def withdraw_money_cli(bank, account, pin):
    print("\n--- Withdraw Money ---")
    print("=" * 30)
    amount = get_valid_amount("Enter the amount to withdraw: $")
    if bank.withdraw(account.get_account_number(), pin, amount):
        print(f"Successfully withdrew ${amount:.2f}.")
        balance = bank.get_account_balance(account.get_account_number(), pin)
        if balance is not None:
            print(f"Your current balance is: ${balance:.2f}")
    else:
        print("Failed to withdraw money. Please try again.")

def view_transaction_history_cli(bank, account):
    print("\n--- Transaction History ---")
    print("=" * 30)
    logs = bank.get_one_audit_logs(account.get_account_number())
    if not logs:
        print("No transaction history found.")
    else:
        for log in logs:
            print(f"{log['timestamp']} - {log['action']} - Amount: ${log['amount']:.2f} By {log['holder_name']}")
         
def update_account_cli(bank, account, pin):
    print("\n--- Update Account ---")
    print("=" * 30)
    new_name = input("Enter your new name: ").strip()

    if new_name :
        account.set_name(new_name)
        if bank.update_account(account):
            print("Name updated successfully!")
            Audit.log_action(account.get_account_number(), account.get_name(), "Name Updated",0.00)
        else:
            print("Failed to update name. Please try again.")
    else:
        print("Invalid choice. Please try again.")

def update_pin_cli(bank, account, pin):
    print("\n--- Update PIN ---")
    print("=" * 30)
    old_pin = input("Enter your current PIN: ").strip()
    if old_pin != pin:
        print("Incorrect current PIN. Please try again.")
        input("Press Enter to continue...")
        return

    new_pin = input("Enter your new PIN (4 digits): ").strip()
    if len(new_pin) != 4 or not new_pin.isdigit():
        print("New PIN must be exactly 4 digits. Please try again.")
        input("Press Enter to continue...")
        return

    confirm_new_pin = input("Confirm your new PIN: ").strip()
    if confirm_new_pin != new_pin:
        print("PINs do not match. Please try again.")
        input("Press Enter to continue...")
        return

    account.set_pin(new_pin)
    if bank.update_account(account):
        print("PIN updated successfully!")
        Audit.log_action(account.get_account_number(), account.get_name(), "PIN Updated",0.00)
        return True
    else:
        print("Failed to update PIN. Please try again.")

def close_account_cli(bank, account, pin):
    print("\n--- Close Account ---")
    print("=" * 30)
    confirm = input("Are you sure you want to close your account? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Account closing cancelled.")
        input("Press Enter to continue...")
        return
    re_pin = input("Please enter your 4-digit PIN to confirm: ").strip()

    if re_pin != pin:
        print("PINs do not match. Account closing cancelled.")
        input("Press Enter to continue...")
        return

    if bank.delete_account(account.get_account_number(), pin):
        print("Account closed successfully!")
        Audit.log_action(account.get_account_number(), account.get_name(), "Account Closed",0.00)
    else:
        print("Account closing cancelled.")


def login_account_cli(bank):
    print("\n--- Create Account ---")
    account_number = input("Enter your account number: ").strip()
    if not account_number:
        print("Account number cannot be empty. Please try again.")
        input("Press Enter to continue...")
        return
    
    pin = input("Enter your PIN: ").strip()

    account = bank.read_account(account_number, pin)
    if not account:
        print("Invalid account number or PIN. Please try again.")
        input("Press Enter to continue...")
        return
    while True:
        print("\n--- Account Menu ---")
        print(f"Welcome, {account.get_name()}!")
        print(f"Your account number: {account.get_account_number()}")
        print("=" * 30)

        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transaction History")
        print("5. Update Account")
        print("6. Update PIN")
        print("7. Close Account")

        print("8. Logout")

        print("=" * 30)

        choice = input("Enter your choice: (1-8)").strip()

        if choice == "1":
            check_balance_cli(bank, account, pin)
        elif choice == "2":
            deposit_money_cli(bank, account, pin)
        elif choice == "3":
            withdraw_money_cli(bank, account, pin)
        elif choice == "4":
            view_transaction_history_cli(bank, account)
        elif choice == "5":
            update_account_cli(bank, account, pin)
        elif choice == "6":
            if update_pin_cli(bank, account, pin):
                break
        elif choice == "7":
            close_account_cli(bank, account, pin)
        elif choice == "8":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("Press Enter to continue...")



# Main function to run the CLI
def main_menu_cli():
    bank = BankingSystem()
    while True:
        print("=" * 40)
        print("\n--- Banking Management System ---")
        print("1. Create Account")
        print("2. Login Account ")
        print("=" * 40)
        # print("\n--- ADMINS ONLY ---")
        # print("3. View ALL Audit Logs ")
        # print("4. View Single Audit Logs ")
        # print("5. Clear All Audit Logs")
        # print("6. Clear Single Audit Logs")
        # print("=" * 40)  
        print("0. Exit")
        choice = input("Enter your choice: (1-5)").strip()

        if choice == "1":
            create_account_cli(bank)
            
        elif choice == "2":
            login_account_cli(bank)

        elif choice == "0":
            print("Thank you for using the Banking. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main_menu_cli()
    