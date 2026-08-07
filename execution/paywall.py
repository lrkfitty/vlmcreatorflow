import os
import stripe
import time

def _secret_key() -> str:
    """Read fresh from env every call to avoid timing issues with dotenv."""
    return os.getenv("STRIPE_SECRET_KEY", "")

def create_credit_checkout(user_email: str, amount: int, price_in_cents: int) -> str | None:
    """
    Creates a Stripe Checkout Session to buy credits.
    amount: number of credits to award
    price_in_cents: price for these credits in USD cents
    """
    key = _secret_key()
    if not key or "PLACEHOLDER" in key:
        return None
        
    stripe.api_key = key
    
    # We use Streamlit query parameters to handle callbacks
    # e.g., http://localhost:8502/?checkout=success&session_id={CHECKOUT_SESSION_ID}
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8502")
    success_url = f"{base_url}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}/?checkout=cancel"
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{amount} CreateFlow Credits",
                            "description": "Credits for AI Content Generation",
                        },
                        "unit_amount": price_in_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user_email if user_email else None,
            metadata={
                "credits": amount
            }
        )
        return session.url
    except Exception as e:
        print(f"Stripe Error: {e}")
        return None

def verify_checkout_session(session_id: str) -> dict:
    """
    Verifies the session via Stripe to prevent spoofing.
    Returns the metadata and status.
    """
    key = _secret_key()
    if not key:
        return {"valid": False, "error": "No Stripe Config"}
        
    stripe.api_key = key
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            return {
                "valid": True, 
                "credits": int(session.metadata.get("credits", 0)),
                "customer": session.customer_details.email if session.customer_details else None
            }
        else:
            return {"valid": False, "error": "Not paid yet"}
    except Exception as e:
        return {"valid": False, "error": str(e)}
