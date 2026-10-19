import streamlit as st
from blockchain import Blockchain

st.set_page_config(page_title="Fake Product Detection", page_icon="X", layout="centered")
st.title("Fake Product Detection on Blockchain")
st.caption("Register authentic products and verify any product ID against the chain.")

RPC = st.sidebar.text_input("RPC URL", "http://127.0.0.1:8545")
PRIVATE_KEY = st.sidebar.text_input(
    "Manufacturer private key",
    type="password",
    help="Use a private key belonging to an authorized manufacturer account.",
)

try:
    bc = Blockchain(RPC)
except Exception as exc:
    st.error("Blockchain connection failed: " + str(exc))
    st.stop()

account_address = None
if PRIVATE_KEY:
    try:
        account_address = bc.w3.eth.account.from_key(PRIVATE_KEY).address
    except Exception:
        st.sidebar.warning("Private key is not valid for this RPC network.")

try:
    if account_address:
        is_authorized = bc.is_authorized_manufacturer(account_address)
        expected_name = bc.manufacturer_name_for(account_address) if is_authorized else ""
        if is_authorized:
            st.sidebar.success(f"Authorized manufacturer: {expected_name}")
        else:
            st.sidebar.warning("This account is not yet authorized to register products.")
except Exception as exc:
    st.sidebar.warning(f"Could not read manufacturer status: {exc}")


tab_register, tab_verify = st.tabs(["Register product", "Verify product"])

with tab_register:
    with st.form("register"):
        pid = st.text_input("Product ID", placeholder="SN-2026-0001")
        name = st.text_input("Product name", placeholder="Wireless Earbuds X")
        mfr = st.text_input("Manufacturer", placeholder="Acme Electronics")
        mfg_at = st.number_input(
            "Manufactured at (epoch seconds)",
            min_value=0,
            value=0,
            step=1,
        )
        submitted = st.form_submit_button("Register on chain")

    if submitted:
        if not (pid and name and mfr and PRIVATE_KEY):
            st.warning("Fill all fields and provide a valid private key.")
        elif not account_address:
            st.error("The private key is invalid.")
        else:
            try:
                if not bc.is_authorized_manufacturer(account_address):
                    st.warning(
                        "This account is not authorized. Ask the contract owner to authorize it first."
                    )
                else:
                    expected_name = bc.manufacturer_name_for(account_address)
                    if expected_name and expected_name.strip() != mfr.strip():
                        st.warning(
                            "This account is registered as '"
                            + expected_name
                            + "'. Please use the exact manufacturer name."
                        )
                    else:
                        receipt = bc.register(pid, name, mfr, int(mfg_at), PRIVATE_KEY)
                        st.success("Registered! Tx: " + receipt.transactionHash.hex())
            except Exception as exc:
                st.error("Registration failed: " + str(exc))

with tab_verify:
    q = st.text_input("Enter product ID to verify")
    if st.button("Verify"):
        try:
            res = bc.verify(q)
        except Exception as exc:
            st.error("Verification failed: " + str(exc))
        else:
            if res["exists"]:
                st.success("Authentic product found on chain")
                st.json(res)
            else:
                st.error("Product not found - possible counterfeit")
