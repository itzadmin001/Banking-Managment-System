import streamlit as st
import pandas as pd
from datetime import datetime
from main import BankingSystem, Account, Audit
import json

# Set page config
st.set_page_config(
    page_title="Banking Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Header styling */
        .header-title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        /* Card styling */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 5px solid #667eea;
        }
        
        /* Balance card */
        .balance-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        .balance-amount {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        /* Success button */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transform: translateY(-2px);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stPasswordInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #667eea;
        }
        
        /* Success message */
        .stSuccess {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        /* Error message */
        .stError {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        /* Info message */
        .stInfo {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        /* Table styling */
        .dataframe {
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Metric styling */
        .metric {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "bank" not in st.session_state:
    st.session_state.bank = BankingSystem()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "account" not in st.session_state:
    st.session_state.account = None
if "pin" not in st.session_state:
    st.session_state.pin = None
if "account_number" not in st.session_state:
    st.session_state.account_number = None

# Helper functions
def format_currency(amount):
    return f"${amount:,.2f}"

def create_account_ui():
    """Create a new account"""
    st.markdown("<div class='header-title'><h1>➕ Create New Account</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        name = st.text_input("Full Name", placeholder="Enter your full name")
        pin = st.text_input("PIN (4 digits)", type="password", placeholder="Enter 4-digit PIN")
    
    with col2:
        confirm_pin = st.text_input("Confirm PIN", type="password", placeholder="Confirm your PIN")
    
    if st.button("Create Account", key="create_account_btn"):
        if not name:
            st.error("❌ Name cannot be empty!")
        elif len(pin) != 4 or not pin.isdigit():
            st.error("❌ PIN must be exactly 4 digits!")
        elif pin != confirm_pin:
            st.error("❌ PINs do not match!")
        else:
            account = st.session_state.bank.create_account(name, pin)
            if account:
                st.success(f"✅ Account created successfully!")
                st.info(f"**Your Account Number:** `{account.get_account_number()}`")
                st.warning("🔐 Please save your account number and PIN safely!")
            else:
                st.error("❌ Failed to create account. Please try again.")

def login_account_ui():
    """Login to an existing account"""
    st.markdown("<div class='header-title'><h1>🔐 Login to Account</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        account_number = st.text_input("Account Number", placeholder="Enter your account number")
    
    with col2:
        pin = st.text_input("PIN", type="password", placeholder="Enter your PIN")
    
    if st.button("Login", key="login_btn"):
        if not account_number or not pin:
            st.error("❌ Please enter both account number and PIN!")
        else:
            account = st.session_state.bank.read_account(account_number, pin)
            if account:
                st.session_state.authenticated = True
                st.session_state.account = account
                st.session_state.pin = pin
                st.session_state.account_number = account_number
                st.success(f"✅ Welcome, {account.get_name()}!")
                st.rerun()
            else:
                st.error("❌ Invalid account number or PIN!")

def logout_ui():
    """Logout from account"""
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.account = None
        st.session_state.pin = None
        st.session_state.account_number = None
        st.success("You have been logged out!")
        st.rerun()

def dashboard_ui():
    """Main dashboard"""
    account = st.session_state.account
    pin = st.session_state.pin
    bank = st.session_state.bank
    
    # Header
    st.markdown(f"<div class='header-title'><h1>👋 Welcome, {account.get_name()}!</h1></div>", unsafe_allow_html=True)
    
    # Account Info and Balance
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric("Account Number", account.get_account_number(), label_visibility="visible")
    
    with col2:
        balance = bank.get_account_balance(account.get_account_number(), pin)
        st.metric("Current Balance", format_currency(balance) if balance else "$0.00", label_visibility="visible")
    
    with col3:
        st.metric("Account Holder", account.get_name(), label_visibility="visible")
    
    st.divider()
    
    # Main Operations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Transactions", "📊 History", "⚙️ Settings", "📋 Audit Logs", "❓ Help"])
    
    with tab1:
        st.subheader("Financial Transactions")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📥 Deposit Money")
            deposit_amount = st.number_input("Amount to Deposit", min_value=0.01, step=0.01, key="deposit_amount")
            
            if st.button("Deposit", key="deposit_btn"):
                if deposit_amount <= 0:
                    st.error("❌ Amount must be greater than 0!")
                else:
                    if bank.deposit(account.get_account_number(), pin, deposit_amount):
                        st.success(f"✅ Successfully deposited {format_currency(deposit_amount)}!")
                        new_balance = bank.get_account_balance(account.get_account_number(), pin)
                        st.info(f"💰 New Balance: {format_currency(new_balance)}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to deposit. Please try again.")
        
        with col2:
            st.markdown("### 📤 Withdraw Money")
            withdraw_amount = st.number_input("Amount to Withdraw", min_value=0.01, step=0.01, key="withdraw_amount")
            
            if st.button("Withdraw", key="withdraw_btn"):
                if withdraw_amount <= 0:
                    st.error("❌ Amount must be greater than 0!")
                else:
                    if bank.withdraw(account.get_account_number(), pin, withdraw_amount):
                        st.success(f"✅ Successfully withdrew {format_currency(withdraw_amount)}!")
                        new_balance = bank.get_account_balance(account.get_account_number(), pin)
                        st.info(f"💰 New Balance: {format_currency(new_balance)}")
                        st.rerun()
                    else:
                        st.error("❌ Insufficient balance or withdrawal failed!")
    
    with tab2:
        st.subheader("Transaction History")
        
        logs = bank.get_one_audit_logs(account.get_account_number())
        
        if not logs:
            st.info("📭 No transaction history found.")
        else:
            # Convert to dataframe for better display
            df = pd.DataFrame(logs)
            df = df[['timestamp', 'action', 'amount', 'holder_name']]
            df.columns = ['Date & Time', 'Action', 'Amount', 'Holder']
            df['Amount'] = df['Amount'].apply(lambda x: format_currency(x))
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download History as CSV",
                data=csv,
                file_name=f"transaction_history_{account.get_account_number()}.csv",
                mime="text/csv"
            )
    
    with tab3:
        st.subheader("Account Settings")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 👤 Update Name")
            new_name = st.text_input("New Name", value=account.get_name(), key="update_name")
            
            if st.button("Update Name", key="update_name_btn"):
                if new_name and new_name != account.get_name():
                    account.set_name(new_name)
                    if bank.update_account(account):
                        st.session_state.account = account
                        Audit.log_action(account.get_account_number(), new_name, "Name Updated", 0.00)
                        st.success("✅ Name updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update name.")
                else:
                    st.warning("⚠️ Please enter a different name.")
        
        with col2:
            st.markdown("### 🔑 Change PIN")
            old_pin_input = st.text_input("Current PIN", type="password", key="old_pin_input")
            new_pin_input = st.text_input("New PIN (4 digits)", type="password", key="new_pin_input")
            confirm_new_pin_input = st.text_input("Confirm New PIN", type="password", key="confirm_new_pin_input")
            
            if st.button("Change PIN", key="change_pin_btn"):
                if old_pin_input != pin:
                    st.error("❌ Incorrect current PIN!")
                elif len(new_pin_input) != 4 or not new_pin_input.isdigit():
                    st.error("❌ New PIN must be exactly 4 digits!")
                elif new_pin_input != confirm_new_pin_input:
                    st.error("❌ New PINs do not match!")
                else:
                    account.set_pin(new_pin_input)
                    if bank.update_account(account):
                        st.session_state.pin = new_pin_input
                        Audit.log_action(account.get_account_number(), account.get_name(), "PIN Updated", 0.00)
                        st.success("✅ PIN updated successfully!")
                    else:
                        st.error("❌ Failed to update PIN.")
    
    with tab4:
        st.subheader("📋 Transaction Audit Logs")
        
        logs = bank.get_one_audit_logs(account.get_account_number())
        
        if not logs:
            st.info("📭 No audit logs found.")
        else:
            df = pd.DataFrame(logs)
            df = df[['timestamp', 'action', 'amount']]
            df.columns = ['Date & Time', 'Action', 'Amount']
            df['Amount'] = df['Amount'].apply(lambda x: format_currency(x))
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🗑️ Clear My Audit Logs", key="clear_my_logs_btn"):
                    if st.session_state.get("confirm_clear", False) == False:
                        st.session_state.confirm_clear = True
                        st.warning("⚠️ Are you sure? This action cannot be undone. Click again to confirm.")
                    else:
                        if bank.clear_single_audit_logs(account.get_account_number()):
                            st.success("✅ Audit logs cleared!")
                            st.session_state.confirm_clear = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to clear logs.")
                        st.session_state.confirm_clear = False
    
    with tab5:
        st.subheader("❓ Help & Information")
        
        st.markdown("""
        ### 💡 How to Use This Banking System
        
        **1. Transactions Tab:**
        - **Deposit:** Add money to your account
        - **Withdraw:** Remove money from your account
        - You need your PIN for all transactions
        
        **2. History Tab:**
        - View all your transactions
        - Download transaction history as CSV
        
        **3. Settings Tab:**
        - Update your name
        - Change your PIN (requires current PIN)
        
        **4. Audit Logs:**
        - View detailed logs of all your account activities
        - Clear logs if desired
        
        ### 🔒 Security Tips
        - Never share your PIN with anyone
        - Keep your account number safe
        - Log out after each session
        - Verify transaction amounts before confirming
        
        ### ⚠️ Important
        - All transactions are logged for security
        - PIN is encrypted in the database
        - Contact support for account issues
        """)
    
    st.divider()
    
    # Danger Zone
    st.subheader("⚠️ Danger Zone")
    
    if st.button("🔴 Close Account", key="close_account_btn"):
        st.session_state.show_close_dialog = True
    
    if st.session_state.get("show_close_dialog", False):
        st.warning("⚠️ This action cannot be undone! Your account and all data will be permanently deleted.")
        
        confirm_pin = st.text_input("Enter your PIN to confirm account closure", type="password", key="close_confirm_pin")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Confirm Closure", key="confirm_close_btn"):
                if confirm_pin == pin:
                    if bank.delete_account(account.get_account_number(), pin):
                        st.success("✅ Account closed successfully!")
                        st.session_state.authenticated = False
                        st.session_state.account = None
                        st.session_state.pin = None
                        st.session_state.account_number = None
                        st.info("Redirecting to home page...")
                        st.rerun()
                    else:
                        st.error("❌ Failed to close account.")
                else:
                    st.error("❌ Incorrect PIN!")
        
        with col2:
            if st.button("❌ Cancel", key="cancel_close_btn"):
                st.session_state.show_close_dialog = False
                st.rerun()

def admin_panel_ui():
    """Admin panel for viewing all audit logs"""
    st.markdown("<div class='header-title'><h1>👨‍💼 Admin Panel</h1></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 All Audit Logs", "🗑️ Management"])
    
    with tab1:
        st.subheader("All System Transactions")
        
        logs = st.session_state.bank.get_allThe_audit_logs()
        
        if not logs:
            st.info("📭 No audit logs found.")
        else:
            df = pd.DataFrame(logs)
            df = df[['timestamp', 'holder_name', 'action', 'amount']]
            df.columns = ['Date & Time', 'Holder Name', 'Action', 'Amount']
            df['Amount'] = df['Amount'].apply(lambda x: format_currency(x))
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Statistics
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                total_deposits = sum([log['amount'] for log in logs if 'Deposited' in log['action']])
                st.metric("Total Deposits", format_currency(total_deposits))
            
            with col2:
                total_withdrawals = sum([log['amount'] for log in logs if 'Withdrawn' in log['action']])
                st.metric("Total Withdrawals", format_currency(total_withdrawals))
            
            with col3:
                st.metric("Total Transactions", len(logs))
    
    with tab2:
        st.subheader("⚙️ Log Management")
        
        if st.button("🗑️ Clear All Audit Logs", key="clear_all_logs_btn"):
            if st.session_state.get("confirm_clear_all", False) == False:
                st.session_state.confirm_clear_all = True
                st.error("⚠️ WARNING: This will delete ALL audit logs! Click again to confirm.")
            else:
                if st.session_state.bank.clear_all_audit_logs():
                    st.success("✅ All audit logs cleared!")
                    st.session_state.confirm_clear_all = False
                    st.rerun()
                else:
                    st.error("❌ Failed to clear logs.")
                st.session_state.confirm_clear_all = False

# Main App
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("<h1 style='text-align: center; color: #667eea;'>🏦 Banking System</h1>", unsafe_allow_html=True)
        st.divider()
        
        if not st.session_state.authenticated:
            st.markdown("## 🔐 Authorization")
            page = st.radio("Select Page:", ["Login", "Create Account"], label_visibility="collapsed")
            st.divider()
            
            if page == "Login":
                login_account_ui()
            else:
                create_account_ui()
        
        else:
            st.markdown(f"### 👤 Logged In As")
            st.info(f"**{st.session_state.account.get_name()}**")
            st.divider()
            
            page = st.radio("Menu:", ["Dashboard", "Admin Panel"], label_visibility="collapsed")
            
            st.divider()
            logout_ui()
    
    # Main content
    if not st.session_state.authenticated:
        st.markdown("<div class='header-title'><h1>🏦 Banking Management System</h1><p>Secure, Fast & Reliable Banking</p></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("""
            ### ✨ Features
            - 🔐 Secure Login
            - 💰 Deposit & Withdraw
            - 📊 Transaction History
            - 📋 Audit Logs
            """)
        
        with col2:
            st.markdown("""
            ### 🎯 Benefits
            - 24/7 Access
            - Instant Transactions
            - Complete Control
            - Full Transparency
            """)
        
        with col3:
            st.markdown("""
            ### 🔒 Security
            - Encrypted PINs
            - Secure Database
            - Activity Logging
            - Data Protection
            """)
    
    else:
        if 'page' in locals():
            if page == "Dashboard":
                dashboard_ui()
            elif page == "Admin Panel":
                admin_panel_ui()
        else:
            dashboard_ui()

if __name__ == "__main__":
    main()
