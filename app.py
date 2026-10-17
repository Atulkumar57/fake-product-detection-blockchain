import streamlit as st
from blockchain import Blockchain

st.set_page_config(page_title="Fake Product Detection", page_icon="X", layout="centered")
st.title("Fake Product Detection on Blockchain")
st.caption("Register authentic products and verify any product ID against the chain.")

RPC = st.sidebar.text_input("RPC URL", "http://127.0.0.1:8545")
PRIVATE_KEY = st.sidebar.text_input(
    "Manufacturer private key (Hardhat account #0)", type="password",
    help="Use one of the private keys printed by `npx hardhat node`."
)

try:
    bc = Blockchain(RPC)
except Exception as e:
    st.error("Blockchain connection failed: " + str(e))
    st.stop()

tab_register, tab_verify = st.tabs(["Register product", "Verify product"])

with tab_register:
    with st.form("register"):
        pid = st.text_input("Product ID", placeholder="SN-2026-0001")
        name = st.text_input("Product name", placeholder="Wireless Earbuds X")
        mfr = st.text_input("Manufacturer", placeholder="Acme Electronics")
        mfg_at = st.number_input("Manufactured at (epoch seconds)", min_value=0, value=0, step=1)
        submitted = st.form_submit_button("Register on chain")
    if submitted:
        if not (pid and name and mfr and PRIVATE_KEY):
            st.warning("Fill all fields and provide a private key.")
        else:
            try:
                receipt = bc.register(pid, name, mfr, int(mfg_at), PRIVATE_KEY)
                st.success("Registered! Tx: " + receipt.transactionHash.hex())
            except Exception as e:
                st.error("Registration failed: " + str(e))

with tab_verify:
    q = st.text_input("Enter product ID to verify")
    if st.button("Verify"):
        try:
            res = bc.verify(q)
        except Exception as e:
            st.error("Verification failed: " + str(e))
        else:
            if res["exists"]:
                st.success("Authentic product found on chain")
                st.json(res)
            else:
                st.error("Product not found - possible counterfeit")
