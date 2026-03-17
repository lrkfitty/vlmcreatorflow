from __future__ import annotations
import os
import stripe


B2B_PRICE_ID = "price_1TBzOvKIWXG1ZQJE9LYl49Ix"  # $997/mo Enterprise


def _secret_key() -> str:
    """Read fresh from env every call — avoids module-load timing issues."""
    return os.getenv("STRIPE_SECRET_KEY", "")


def create_checkout_session(email: str = "", company: str = "") -> str | None:
    key = _secret_key()
    if not key or "PLACEHOLDER" in key:
        return None
    stripe.api_key = key
    success_url = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:8502/?checkout=success")
    cancel_url  = os.getenv("STRIPE_CANCEL_URL",  "http://localhost:8502/?checkout=cancel")
    kwargs = dict(
        mode="subscription",
        line_items=[{"price": B2B_PRICE_ID, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        billing_address_collection="required",
    )
    if email:
        kwargs["customer_email"] = email
    session = stripe.checkout.Session.create(**kwargs)
    return session.url


def handle_stripe_button(label: str, email: str = "", company: str = ""):
    import streamlit as st

    if st.button(label, type="primary", use_container_width=True):
        with st.spinner("Creating secure checkout..."):
            url = create_checkout_session(email, company)
        if url:
            st.session_state["stripe_url"] = url
        else:
            st.warning("Stripe not configured. Add STRIPE_SECRET_KEY to .env.")

    # Render the link outside the button block so it persists on rerun
    if st.session_state.get("stripe_url"):
        url = st.session_state["stripe_url"]
        st.link_button("Continue to Secure Checkout →", url, use_container_width=True)
        st.markdown(
            f"<p style='text-align:center;font-size:0.8rem;color:#334155;margin-top:6px;'>"
            f"Secured by Stripe &nbsp;·&nbsp; "
            f"<a href='{url}' target='_blank' style='color:#10B981;'>Open in new tab</a></p>",
            unsafe_allow_html=True
        )
