# ==========================================
# --- COMMUNITY FEEDBACK DESK (NATIVE PYTHON) ---
# ==========================================
st.markdown("<div style='margin: 30px 0 10px 0;'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div style="background: rgba(18, 19, 26, 0.95); border: 1px solid #27272a; border-top: 3px solid #ef4444; border-radius: 12px; padding: 20px; font-family: system-ui, -apple-system, sans-serif; color: #f4f4f5; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);">
    <h3 style="color: #f87171; margin-top: 0; font-size: 1.2rem;">💬 TSN VIEWER & COMMUNITY FEEDBACK DESK</h3>
    <p style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 15px;">
        Have news tips, weather updates, or suggestions for the network? Send your message directly to the TSN desk at <strong style="color: #fafafa;">wsnk836@gmail.com</strong>.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

with st.form("tsn_feedback_form", clear_on_submit=True):
  fb_name = st.text_input("Viewer Name *", placeholder="Your Name")
  fb_loc = st.text_input("Your Location / Grid (Optional)", placeholder="City or ZIP")
  fb_msg = st.text_area(
      "Feedback or News Tip *",
      placeholder="Enter your message, news tip, or suggestion here...",
  )
  submit_feedback = st.form_submit_button(
      "Transmit Feedback to Desk", use_container_width=True
  )

  if submit_feedback:
    if not fb_name.strip() or not fb_msg.strip():
      st.error(
          "⚠️ Transmission error: Please provide both your name and message."
      )
    else:
      try:
        payload = {
            "access_key": "6f59571f-f519-4655-9b50-095eed178152",
            "subject": (
                "💡 Community Feedback and Suggestions from TSN News Network"
            ),
            "name": fb_name.strip(),
            "location": fb_loc.strip() if fb_loc else "Not provided",
            "message": fb_msg.strip(),
        }
        response = requests.post(
            "https://api.web3forms.com/submit", json=payload, timeout=10
        )
        data = response.json()

        if response.status_code == 200 and data.get("success"):
          st.success(
              "✅ Feedback successfully transmitted directly to"
              " wsnk836@gmail.com!"
          )
        else:
          st.error(
              "❌ Server relay error: "
              + data.get("message", "Please try again shortly.")
          )
      except Exception as e:
        st.error(
            f"❌ Network connection error ({e}). Please check your connection."
        )
