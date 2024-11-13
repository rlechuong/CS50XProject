import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lostark.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Queries the database for each character the user owns and displays it in a table as the homepage.
    characters = db.execute("SELECT * FROM characters WHERE user_id = ?", session["user_id"])
    return render_template("index.html", characters=characters)


@app.route("/addcharacter", methods=["GET", "POST"])
@login_required
def addcharacter():
    # The list of available classes in the game
    classes = sorted(["Aeromancer", "Berserker", "Destroyer", "Gunlancer", "Paladin", "Slayer", "Glaivier", "Scrapper", "Soulfist", "Striker",
                      "Wardancer", "Artillerist", "Artist", "Breaker", "Deadeye", "Gunslinger", "Machinist", "Sharpshooter", "Arcanist", "Bard",
                      "Sorceress", "Summoner", "Deatblade", "Reaper", "Shadowhunter", "Soul Eater"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("name")
        item_level = request.form.get("item_level")
        character_class = request.form.get("character_class")

        # Ensure character name was submitted
        if not name:
            flash(f"Add Failed: Please Enter Character Name")
            return render_template("addcharacter.html", classes=classes)

        # Ensure character item level was submitted
        elif not item_level:
            flash(f"Add Failed: Please Enter Item Level")
            return render_template("addcharacter.html", classes=classes)

        # Ensure character class was selected
        elif not character_class:
            flash(f"Add Failed: Please Select Character Class")
            return render_template("addcharacter.html", classes=classes)

        # Ensure character item level is positive integer
        try:
            if int(item_level) < 0:
                flash(f"Add Failed: Please Enter Positive Item Level")
                return render_template("addcharacter.html", classes=classes)
        except ValueError:
            flash(f"Add Failed: Please Enter Positive Item Level")
            return render_template("addcharacter.html", classes=classes)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM characters WHERE name = ?", name)

        # Ensure username exists and password is correct
        if len(rows) == 1:
            flash(f"Add Failed: Character Name Already Exists")
            return render_template("addcharacter.html", classes=classes)

        # Update character table
        db.execute("INSERT INTO characters (user_id, name, class, item_level) VALUES (?, ?, ?, ?)",
                   session["user_id"], name, character_class, item_level)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("addcharacter.html", classes=classes)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    # Queries the database for a list of all the current user's characters for use in a form select option.
    characters_list_raw = db.execute(
        "SELECT name FROM characters WHERE user_id = ?", session["user_id"])
    characters_list = []
    for _ in characters_list_raw:
        characters_list.append(_["name"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensures that one of the user's characters is selected in the form.
        if not request.form.get("character"):
            flash(f"Please Select A Character")
            return redirect("/edit")

        # Deletes the user's selectecd character from the characters database, as well all the gear from the qualities database.
        db.execute("DELETE FROM qualities WHERE character_name = ?", request.form.get("character"))
        db.execute("DELETE from characters WHERE name = ?", request.form.get("character"))

        # Returns the user to the homepage on successful deletion of a character.
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect("/edit")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    # Queries the database for a list of all the current user's characters for use in a form select option.
    characters_list_raw = db.execute(
        "SELECT name FROM characters WHERE user_id = ?", session["user_id"])
    characters_list = []
    for _ in characters_list_raw:
        characters_list.append(_["name"])

    # The list of available classes in the game
    classes = sorted(["Aeromancer", "Berserker", "Destroyer", "Gunlancer", "Paladin", "Slayer", "Glaivier", "Scrapper", "Soulfist", "Striker",
                      "Wardancer", "Artillerist", "Artist", "Breaker", "Deadeye", "Gunslinger", "Machinist", "Sharpshooter", "Arcanist", "Bard",
                      "Sorceress", "Summoner", "Deatblade", "Reaper", "Shadowhunter", "Soul Eater"])

    # This currently is not use since I couldn't figure it out, but this retreives all the useer's characters' item levels and puts them in a dictionary as values
    # with the character as the key. I wanted to dynamically update the item level input field when a character is selected, but apparently need AJAX.
    item_level_list_raw = db.execute(
        "SELECT item_level FROM Characters WHERE user_id = ?", session["user_id"])
    item_level_list = []
    for _ in item_level_list_raw:
        item_level_list.append(_["item_level"])

    item_level_dict = {}

    for _ in range(len(characters_list)):
        item_level_dict[characters_list[_]] = item_level_list[_]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("name_edit")
        item_level = request.form.get("item_level_edit")
        character_class = request.form.get("class_edit")

        # Ensure character name was submitted
        if not name:
            flash(f"Please Select A Character")
            return redirect("/edit")

        # Ensure character item level was submitted
        elif not item_level:
            flash(f"Please Enter Item Level")
            return redirect("/edit")

        # Ensure character class was selected
        elif not character_class:
            flash(f"Please Select Character Class")
            return redirect("/edit")

        # Ensure character item level is positive integer
        try:
            if int(item_level) < 0:
                flash(f"Please Enter Positive Item Level")
                return redirect("/edit")
        except ValueError:
            flash(f"Please Enter Positive Item Level")
            return redirect("/edit")

        # It the user has input everything correctly, this will edit the character's information in the database and return the homepage.
        db.execute("UPDATE characters SET class = ?, item_level = ? WHERE name = ?",
                   character_class, item_level, name)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("edit.html", characters_list=characters_list, classes=classes, item_level_dict=item_level_dict)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash(f"Please Enter A Username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(f"Please Enter A Password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash(f"Invalid Username Or Password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/oreha", methods=["GET", "POST"])
@login_required
def oreha():

    # Queries the oreha database to get all the prices for each material to be used in input forms.
    oreha_materials = db.execute("SELECT * FROM oreha_materials")

    oreha_solar_carp_price = oreha_materials[0]["price"]
    natural_pearl_price = oreha_materials[1]["price"]
    fish_price = oreha_materials[2]["price"]

    oreha_thick_meat_price = oreha_materials[3]["price"]
    tough_leather_price = oreha_materials[4]["price"]
    thick_raw_meat_price = oreha_materials[5]["price"]

    oreha_relic_price = oreha_materials[6]["price"]
    rare_relic_price = oreha_materials[7]["price"]
    ancient_relic_price = oreha_materials[8]["price"]

    oreha_fusion_material_price = oreha_materials[9]["price"]

    # Formuals to calculate the price of crafting oreha fusion materials based on the three potential methods.
    oreha_fish_indprice = ((((oreha_solar_carp_price / 10) * 52) +
                           ((natural_pearl_price / 10) * 69) + ((fish_price / 100) * 142)) + 264) / 15
    oreha_meat_indprice = ((((oreha_thick_meat_price / 10) * 52) +
                           ((tough_leather_price / 10) * 69) + ((thick_raw_meat_price / 100) * 142)) + 264) / 15
    oreha_relic_indprice = ((((oreha_relic_price / 10) * 52) + ((rare_relic_price / 10)
                            * 51) + ((ancient_relic_price / 100) * 107)) + 264) / 15

    # Let's the user know if it is cheaper to craft or buy the oreha fusion materials based on the input value of the auction house price.
    if oreha_fusion_material_price > oreha_fish_indprice or oreha_fusion_material_price > oreha_meat_indprice or oreha_fusion_material_price > oreha_relic_indprice:
        summary = "IT IS CURRENTLY CHEAPER TO CRAFT"
    elif oreha_fusion_material_price < oreha_fish_indprice or oreha_fusion_material_price < oreha_meat_indprice or oreha_fusion_material_price < oreha_relic_indprice:
        summary = "IT IS CURRENTLY CHEAPER TO BUY"
    else:
        summary = "IT IS THE SAME PRICE TO CRAFT OR BUY"

    oreha_render_template = render_template("oreha.html", oreha_solar_carp_price=oreha_solar_carp_price, natural_pearl_price=natural_pearl_price, fish_price=fish_price,
                                            oreha_thick_meat_price=oreha_thick_meat_price, tough_leather_price=tough_leather_price, thick_raw_meat_price=thick_raw_meat_price,
                                            oreha_relic_price=oreha_relic_price, rare_relic_price=rare_relic_price, ancient_relic_price=ancient_relic_price,
                                            oreha_fish_indprice=oreha_fish_indprice, oreha_meat_indprice=oreha_meat_indprice, oreha_relic_indprice=oreha_relic_indprice,
                                            oreha_fusion_material_price=oreha_fusion_material_price, summary=summary)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure that every input field related to the oreha fusion material prices is not empty.
        if not request.form.get("oreha_solar_carp_price") or not request.form.get("natural_pearl_price") or not request.form.get("fish_price") or not request.form.get("oreha_thick_meat_price")\
                or not request.form.get("tough_leather_price") or not request.form.get("thick_raw_meat_price") or not request.form.get("oreha_relic_price") or not request.form.get("rare_relic_price")\
                or not request.form.get("ancient_relic_price") or not request.form.get("oreha_fusion_material_price"):
            flash(f"Please Fill Out Every Value")
            return oreha_render_template

        # Ensure that the user inputs only positive values for the oreha fusion material prices.
        try:
            if int(request.form.get("oreha_solar_carp_price")) < 0 or int(request.form.get("oreha_solar_carp_price")) % 1 != 0 or\
                    int(request.form.get("natural_pearl_price")) < 0 or int(request.form.get("natural_pearl_price")) % 1 != 0 or\
                    int(request.form.get("fish_price")) < 0 or int(request.form.get("fish_price")) % 1 != 0 or\
                    int(request.form.get("oreha_thick_meat_price")) < 0 or int(request.form.get("oreha_thick_meat_price")) % 1 != 0 or\
                    int(request.form.get("tough_leather_price")) < 0 or int(request.form.get("tough_leather_price")) % 1 != 0 or\
                    int(request.form.get("thick_raw_meat_price")) < 0 or int(request.form.get("thick_raw_meat_price")) % 1 != 0 or\
                    int(request.form.get("oreha_relic_price")) < 0 or int(request.form.get("oreha_relic_price")) % 1 != 0 or\
                    int(request.form.get("rare_relic_price")) < 0 or int(request.form.get("rare_relic_price")) % 1 != 0 or\
                    int(request.form.get("ancient_relic_price")) < 0 or int(request.form.get("ancient_relic_price")) % 1 != 0 or\
                    int(request.form.get("oreha_fusion_material_price")) < 0 or int(request.form.get("oreha_fusion_material_price")) % 1 != 0:
                flash(f"Please Enter Positive Integers Only")
                return oreha_render_template
        except ValueError:
            flash(f"Please Enter Positive Integers Only")
            return oreha_render_template

        # If the form is filled out correctly, this will update all the values in the oreha materials database, then redirect the user back to the page
        # to show the updated values after all calculations have ran again.
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'oreha_solar_carp';", int(
            request.form.get("oreha_solar_carp_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'natural_pearl';",
                   int(request.form.get("natural_pearl_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'fish';",
                   int(request.form.get("fish_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'oreha_thick_meat';", int(
            request.form.get("oreha_thick_meat_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'tough_leather';",
                   int(request.form.get("tough_leather_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'thick_raw_meat';",
                   int(request.form.get("thick_raw_meat_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'oreha_relic';",
                   int(request.form.get("oreha_relic_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'rare_relic';",
                   int(request.form.get("rare_relic_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'ancient_relic';",
                   int(request.form.get("ancient_relic_price")))
        db.execute("UPDATE oreha_materials SET price = ? WHERE material = 'oreha_fusion_material';", int(
            request.form.get("oreha_fusion_material_price")))

        return redirect("/oreha")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return oreha_render_template


@app.route("/qualities", methods=["GET", "POST"])
@login_required
def qualities():
    # This queries the qualities database and returns everything so it can be manipulated later on.
    qualities = db.execute("SELECT * FROM qualities")

    # This returns a list of all the current user's characters to be used later in an input form as well as displayed in a table on the page.
    characters_raw_list = db.execute("SELECT name FROM characters")
    characters_list = []
    for _ in characters_raw_list:
        characters_list.append(_["name"])

    # The list of all available equipment slots in the game.
    slots = ["Helm", "Pauldrons", "Chestpiece", "Pants", "Gloves", "Weapon"]

    # This returns the quality of all the equipment in the database. Sorted by character name so it can be matched by charactear as they are alphabetical.
    # I hope to learn a more dynamic way to do this in the future.
    helm_qualities_raw_list = db.execute(
        "SELECT quality FROM qualities WHERE slot='Helm' ORDER BY character_name ASC")
    helm_qualities_list = []
    for _ in helm_qualities_raw_list:
        helm_qualities_list.append(_["quality"])

    pauldrons_qualities_raw_list = db.execute(
        "SELECT quality FROM qualities WHERE slot='Pauldrons' ORDER BY character_name ASC")
    pauldrons_qualities_list = []
    for _ in pauldrons_qualities_raw_list:
        pauldrons_qualities_list.append(_["quality"])

    chestpiece_qualities_raw_list = db.execute(
        "SELECT quality FROM qualities WHERE slot='Chestpiece' ORDER BY character_name ASC")
    chestpiece_qualities_list = []
    for _ in chestpiece_qualities_raw_list:
        chestpiece_qualities_list.append(_["quality"])

    pants_qualities_raw_list = db.execute(
        "SELECT quality FROM qualities WHERE slot='Pants' ORDER BY character_name ASC")
    pants_qualities_list = []
    for _ in pants_qualities_raw_list:
        pants_qualities_list.append(_["quality"])

    gloves_qualities_raw_list = db.execute(
        "SELECT quality FROM qualities WHERE slot='Gloves' ORDER BY character_name ASC")
    gloves_qualities_list = []
    for _ in gloves_qualities_raw_list:
        gloves_qualities_list.append(_["quality"])

    weapon_qualities_raw_list = db.execute(
        "SELECT quality FROM qualities WHERE slot='Weapon' ORDER BY character_name ASC")
    weapon_qualities_list = []
    for _ in weapon_qualities_raw_list:
        weapon_qualities_list.append(_["quality"])

    # This returns the lowest armor quality and weapon quality out of all the ones retrieved, to be highlithed in a table on the page.
    lowest_weapon_quality = min(weapon_qualities_list)
    lowest_armor_quality = min(helm_qualities_list + pauldrons_qualities_list +
                               chestpiece_qualities_list + pants_qualities_list + gloves_qualities_list)

    qualities_render_return = render_template("qualities.html", qualities=qualities, characters_list=characters_list, slots=slots, helm_qualities_list=helm_qualities_list, pauldrons_qualities_list=pauldrons_qualities_list,
                                              chestpiece_qualities_list=chestpiece_qualities_list, pants_qualities_list=pants_qualities_list, gloves_qualities_list=gloves_qualities_list, weapon_qualities_list=weapon_qualities_list,
                                              lowest_weapon_quality=lowest_weapon_quality, lowest_armor_quality=lowest_armor_quality)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("character"):
            flash(f"Please Select A Character")
            return redirect("/qualities")
        # Ensure slot was submitted
        elif not request.form.get("slot"):
            flash(f"Please Select A Slot")
            return redirect("/qualities")
        # Ensure quality was submitted
        elif not request.form.get("quality"):
            flash(f"Please Fill Enter A Quality")
            return redirect("/qualities")
        # Ensure that quality is a positive integer between 1 and 100.
        try:
            if int(request.form.get("quality")) < 0 or int(request.form.get("quality")) % 1 != 0 or int(request.form.get("quality")) > 100 or int(request.form.get("quality")) < 1:
                flash(f"Please Enter A Positive Integer Between 1 And 100")
                return redirect("/qualities")
        except ValueError:
            flash(f"Please Enter A Positive Integer Between 1 And 100")
            return redirect("/qualities")

        # Since each character can only have one quality value for each slot, this checks to see if a slot exists already in the database for the character.
        # If a slot exists, it updates the quality value, otherwise it inserts the quality of the slow into the database.
        rows = db.execute(
            "SELECT * FROM qualities WHERE character_name = ? AND slot = ?", request.form.get("character"), request.form.get("slot"))

        if len(rows) == 1:
            db.execute("UPDATE qualities SET quality = ? WHERE character_name = ? AND slot = ?", int(
                request.form.get("quality")), request.form.get("character"), request.form.get("slot"))
        else:
            db.execute("INSERT INTO qualities (quality, character_name, slot) VALUES (?, ?, ?)", int(
                request.form.get("quality")), request.form.get("character"), request.form.get("slot"))

        return redirect("/qualities")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return qualities_render_return


@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not username:
            flash(f"Registration Failed: Please Enter Username")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash(f"Registration Failed: Please Enter Password")
            return render_template("register.html")

        # Ensure confirmation password was submitted
        elif not confirmation:
            flash(f"Registration Failed: Please Confirm Password")
            return render_template("register.html")

        # Ensure password and confirmation password match
        elif password != confirmation:
            flash(f"Password And Confirmation Password Do Not Match")
            return render_template("register.html")

        # Ensure username does not already exist
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       username, generate_password_hash(password))
        except ValueError:
            flash(f"Registration Failed: Username Already Exists")
            return render_template("register.html")

        # Redirect to homepage if registration pases all checks
        flash(f"Registration Successful")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
