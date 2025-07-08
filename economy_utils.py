def add_coins(user_id, amount):
    # Example using a dictionary or database
    user_data = load_user(user_id)  # Load from DB or JSON
    user_data["coins"] = user_data.get("coins", 0) + amount
    save_user(user_id, user_data)
