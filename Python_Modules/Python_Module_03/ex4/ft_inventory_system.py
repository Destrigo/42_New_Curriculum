if __name__ == "__main__":
    """
    • Manage player inventories (like your personal treasure chest!)
    • Track item details: quantities, types, values (is it worth keeping?)
    • Calculate total inventory value (how rich are you?)
    • Organize items by categories (weapons, potions, armor, etc.)
    • Generate cool inventory reports (show off your collection!)
    """
    print("=== Player Inventory System ===")
    print("")
    alice = dict()
    alice.update({
        "sword": {"qty": 1, "type": "weapon",
                  "rarity": "rare", "value": 500},
        "potion": {"qty": 5, "type": "consumable",
                   "rarity": "common", "value": 50},
        "shield": {"qty": 1, "type": "armor",
                   "rarity": "uncommon", "value": 200},
    })
    bob = dict()
    bob.update({
        "potion": {"qty": 0, "type": "consumable",
                   "rarity": "common", "value": 50},
    })

    def total_value(inv):
        keys_list = list(inv.keys())
        total = 0
        i = 0
        while i < len(keys_list):
            k = keys_list[i]
            v = inv.get(k)
            total += v.get("qty") * v.get("value")
            i += 1
        return total

    def total_items(inv):
        keys_list = list(inv.keys())
        count = 0
        i = 0
        while i < len(keys_list):
            k = keys_list[i]
            v = inv.get(k)
            count += v.get("qty")
            i += 1
        return count

    def get_categories(inv):
        cats = dict()
        keys_list = list(inv.keys())
        i = 0
        while i < len(keys_list):
            k = keys_list[i]
            v = inv.get(k)
            t = v.get("type")
            qty = v.get("qty")
            if cats.get(t) is None:
                cats.update({t: qty})
            else:
                cats.update({t: cats.get(t) + qty})
            i += 1
        return cats

    print("=== Alice's Inventory ===")
    keys_list = list(alice.keys())
    i = 0
    while i < len(keys_list):
        name = keys_list[i]
        data = alice.get(name)
        qty = data.get("qty")
        t = data.get("type")
        rarity = data.get("rarity")
        val = data.get("value")
        print(f"{name} ({t}, {rarity}): {qty}x @ {val} gold "
              f"each = {qty * val} gold")
        i += 1

    print("Inventory value: " + str(total_value(alice)) + " gold")
    print("Item count: " + str(total_items(alice)) + " items")
    cats = get_categories(alice)
    cat_keys = list(cats.keys())
    i = 0
    cat_str = ""
    while i < len(cat_keys):
        k = cat_keys[i]
        cat_str = cat_str + k + "(" + str(cats.get(k)) + ")"
        if i < len(cat_keys) - 1:
            cat_str = cat_str + ", "
        i += 1
    print("Categories: " + cat_str)
    print("=== Transaction: Alice gives Bob 2 potions ===")
    amount = 2
    if alice.get("potion").get("qty") >= amount:
        alice.get("potion").update(
            {"qty": alice.get("potion").get("qty") - amount})
        bob.get("potion").update(
            {"qty": bob.get("potion").get("qty") + amount})
        print("Transaction successful!")
    else:
        print("Transaction failed!")

    print("=== Updated Inventories ===")
    print("Alice potions: " + str(alice.get("potion").get("qty")))
    print("Bob potions: " + str(bob.get("potion").get("qty")))

    players = dict()
    players.update({"Alice": alice})
    players.update({"Bob": bob})

    player_keys = list(players.keys())
    i = 0
    most_val = -1
    most_val_name = ""
    while i < len(player_keys):
        name = player_keys[i]
        inv = players.get(name)
        val = total_value(inv)
        if val > most_val:
            most_val = val
            most_val_name = name
        i += 1
    print("Most valuable player: " + most_val_name + " "
          "(" + str(most_val) + " gold)")

    i = 0
    most_items = -1
    most_items_name = ""
    while i < len(player_keys):
        name = player_keys[i]
        inv = players.get(name)
        c = total_items(inv)
        if c > most_items:
            most_items = c
            most_items_name = name
        i += 1
    print("Most items: " + most_items_name + " "
          "(" + str(most_items) + " items)")

    rare_items = dict()
    i = 0
    while i < len(player_keys):
        name = player_keys[i]
        inv = players.get(name)
        item_keys = list(inv.keys())
        j = 0
        while j < len(item_keys):
            item_name = item_keys[j]
            data = inv.get(item_name)
            if data.get("rarity") in ("rare",
                                      "unique") and rare_items.get(
                                          item_name) is None:
                rare_items.update({item_name: 1})
            j += 1
        i += 1

    rare_keys = list(rare_items.keys())
    i = 0
    rare_str = ""
    while i < len(rare_keys):
        rare_str = rare_str + rare_keys[i]
        if i < len(rare_keys) - 1:
            rare_str = rare_str + ", "
        i += 1
    print("Rarest items: " + rare_str)
