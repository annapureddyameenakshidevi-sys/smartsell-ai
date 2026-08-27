import streamlit as st
import json
import re
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import razorpay
load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


# -----------------------------
# Audit Trail
# -----------------------------
def write_audit_log(action, details):
    audit_path = Path("data/audit.log")
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(audit_path, "a", encoding="utf-8") as file:
        file.write(
            f"{timestamp} | {action} | {details}\n"
        )


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="SmartSell AI",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ SmartSell AI")
st.subheader("Agentic Commerce & Merchant Growth Assistant")
st.write(
    "Describe what you are looking for and SmartSell AI will "
    "find suitable products from the catalog."
)


# -----------------------------
# Cart
# -----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []


# -----------------------------
# Product Catalog
# -----------------------------
catalog_path = Path("data/products.json")

if catalog_path.exists():
    products = json.loads(
        catalog_path.read_text(encoding="utf-8")
    )
else:
    products = [
        {
            "id": "P001",
            "name": "Campus Backpack",
            "category": "Bags",
            "price": 1499,
            "description": "Water-resistant college backpack with laptop compartment",
            "tags": "college backpack laptop travel"
        },
        {
            "id": "P002",
            "name": "Urban Laptop Backpack",
            "category": "Bags",
            "price": 1899,
            "description": "Stylish laptop backpack with padded compartments",
            "tags": "college backpack laptop office"
        },
        {
            "id": "P003",
            "name": "Steel Water Bottle",
            "category": "Accessories",
            "price": 499,
            "description": "750ml insulated stainless steel water bottle",
            "tags": "water bottle college fitness"
        },
        {
            "id": "P004",
            "name": "Wireless Earbuds",
            "category": "Electronics",
            "price": 1299,
            "description": "Compact wireless earbuds with charging case",
            "tags": "earbuds music student"
        },
        {
            "id": "P005",
            "name": "Laptop Sleeve",
            "category": "Accessories",
            "price": 799,
            "description": "Protective 15-inch laptop sleeve",
            "tags": "laptop sleeve college office"
        },
        {
            "id": "P006",
            "name": "USB-C Hub",
            "category": "Electronics",
            "price": 999,
            "description": "Multi-port USB-C hub for laptops",
            "tags": "usb hub laptop student"
        }
    ]


# -----------------------------
# Search
# -----------------------------
query = st.text_input(
    "What are you looking for?",
    placeholder="Example: I need a college backpack under 2000"
)

if query:
    write_audit_log(
        "SEARCH",
        f"User searched for: {query}"
    )

    query_lower = query.lower()

    # Find budget
    budget_match = re.search(
        r"(?:under|below|less than|upto|up to)\s*₹?\s*(\d+)",
        query_lower
    )

    budget = None

    if budget_match:
        budget = int(budget_match.group(1))

    # Words that should not affect product matching
    stop_words = {
        "i",
        "need",
        "a",
        "an",
        "the",
        "for",
        "under",
        "below",
        "less",
        "than",
        "upto",
        "up",
        "to",
        "₹"
    }

    words = [
        word
        for word in re.findall(
            r"[a-zA-Z0-9]+",
            query_lower
        )
        if word not in stop_words
        and not word.isdigit()
    ]

    matches = []

    for product in products:

        searchable = (
            f"{product['name']} "
            f"{product['description']} "
            f"{product['tags']}"
        ).lower()

        score = sum(
            1
            for word in words
            if word in searchable
        )

        # Apply budget filter
        if budget is not None:
            if product["price"] > budget:
                continue

        if score > 0:
            matches.append(
                (score, product)
            )

    matches.sort(
        key=lambda item: (
            -item[0],
            item[1]["price"]
        )
    )

    if matches:

        st.success(
            f"Found {len(matches)} matching product(s)."
        )

        for score, product in matches:

            with st.container(border=True):

                st.subheader(
                    product["name"]
                )

                st.write(
                    product["description"]
                )

                st.write(
                    f"**Category:** {product['category']}"
                )

                st.write(
                    f"**Price:** ₹{product['price']}"
                )

                if st.button(
                    f"Add {product['name']} to cart",
                    key=f"cart_{product['id']}"
                ):

                    already_added = any(
                        item["id"] == product["id"]
                        for item in st.session_state.cart
                    )

                    if not already_added:

                        st.session_state.cart.append(
                            product
                        )

                        write_audit_log(
                            "ADD_TO_CART",
                            f"Product: {product['name']} | "
                            f"Price: ₹{product['price']}"
                        )

                        st.success(
                            f"{product['name']} added to cart!"
                        )

                    else:

                        st.info(
                            f"{product['name']} is already "
                            "in your cart."
                        )

    else:

        st.warning(
            "No catalog match found. "
            "Try a different product or budget."
        )


# -----------------------------
# Cart
# -----------------------------
st.divider()

st.header("🛒 Your Cart")

if st.session_state.cart:

    total = 0

    for item in st.session_state.cart:

        st.write(
            f"**{item['name']}** — ₹{item['price']}"
        )

        total += item["price"]

    st.subheader(
        f"Cart Total: ₹{total}"
    )

    if st.button("Clear Cart"):

        write_audit_log(
            "CART_CLEARED",
            f"Previous total: ₹{total}"
        )

        st.session_state.cart = []

        st.rerun()

else:

    st.info(
        "Your cart is empty."
    )


# -----------------------------
# Smart Upsell / Cross-sell
# -----------------------------
if st.session_state.cart:

    st.divider()

    st.header(
        "💡 Smart Suggestion"
    )

    cart_categories = {
        item["category"]
        for item in st.session_state.cart
    }

    cart_ids = {
        item["id"]
        for item in st.session_state.cart
    }

    suggestion = None

    # Backpack → Water Bottle
    if "Bags" in cart_categories:

        suggestion = next(
            (
                product
                for product in products
                if product["name"] == "Steel Water Bottle"
                and product["id"] not in cart_ids
            ),
            None
        )

    # Electronics → Laptop Sleeve
    elif "Electronics" in cart_categories:

        suggestion = next(
            (
                product
                for product in products
                if product["name"] == "Laptop Sleeve"
                and product["id"] not in cart_ids
            ),
            None
        )

    if suggestion:

        st.write(
            f"Complete your purchase with "
            f"**{suggestion['name']}** "
            f"for **₹{suggestion['price']}**."
        )

        st.caption(
            "This suggestion is optional. "
            "It will never be added without "
            "your confirmation."
        )

        if st.button(
            f"Add suggested product — "
            f"{suggestion['name']}",
            key="smart_upsell"
        ):

            already_added = any(
                item["id"] == suggestion["id"]
                for item in st.session_state.cart
            )

            if not already_added:

                st.session_state.cart.append(
                    suggestion
                )

                write_audit_log(
                    "UPSELL_ACCEPTED",
                    f"Product: {suggestion['name']} | "
                    f"Price: ₹{suggestion['price']}"
                )

                st.success(
                    f"{suggestion['name']} "
                    "added to your cart!"
                )

                st.rerun()


# -----------------------------
# Checkout
# -----------------------------
if st.session_state.cart:

    st.divider()

    st.header(
        "💳 Checkout"
    )

    st.write(
        "Review your order before placing it."
    )

    total = sum(
        item["price"]
        for item in st.session_state.cart
    )

    st.write(
        "### Order Summary"
    )

    for item in st.session_state.cart:

        st.write(
            f"- {item['name']} — ₹{item['price']}"
        )

    st.subheader(
        f"Total Amount: ₹{total}"
    )

    with st.form("checkout_form"):

        name = st.text_input(
            "Full Name"
        )

        email = st.text_input(
            "Email"
        )

        address = st.text_area(
            "Delivery Address"
        )

        payment = st.selectbox(
            "Payment Method",
            [
                "Cash on Delivery",
                "Demo Card Payment"
            ]
        )

        submitted = st.form_submit_button(
            "Place Order"
        )

        if submitted:

            if not name or not email or not address:

                st.error(
                    "Please fill in all delivery details."
                )

            else:

                write_audit_log(
                    "CHECKOUT_CONFIRMED",
                    f"Customer: {name} | "
                    f"Amount: ₹{total} | "
                    f"Payment: {payment}"
                )

                st.success(
                    "🎉 Order placed successfully!"
                )

                st.write(
                    f"**Customer:** {name}"
                )

                st.write(
                    f"**Email:** {email}"
                )

                st.write(
                    f"**Payment:** {payment}"
                )

                st.write(
                    f"**Order Total:** ₹{total}"
                )

                st.session_state.cart = []