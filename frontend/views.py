import datetime
from functools import wraps

from decouple import config
from flask import render_template, request, redirect, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from frontend import app
from backend.classes.address import Address
from backend.classes.user import User, Buyer, Seller, Manager
from backend.classes.category import Category
from backend.interface.sign_in import signin
from backend.classes.order import Order,Transaction
from backend.classes.item import Item

## initialising flask-login
app.secret_key = config("SECRETKEY")   # made it secret
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"

@login_manager.user_loader
def load_user(userid):
    return User.objects(uid = userid).first()

# special decorators

def is_manager(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_anonymous or current_user.type() != "Manager":
            flash("Please login as a Manager to access this page!" , "error")
            return redirect("/sign_in")
        return f(*args, **kwargs)
    return decorated


def is_seller(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if (current_user.is_anonymous) or current_user.type() != "Seller":
            flash("Please login as a Seller to access this page!" , "error")
            return redirect("/sign_in")
        return f(*args, **kwargs)
    return decorated


def is_buyer(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if (current_user.is_anonymous) or current_user.type() != "Buyer":
            flash("Please login as a Buyer to access this page!" , "error")
            return redirect("/sign_in")
        return f(*args, **kwargs)
    return decorated

############### common  routes  ###############

@app.route("/home")
@app.route("/")
def home():

    if current_user.is_anonymous:
        return redirect("/sign_in")

    elif current_user.type() == "Manager":
        return redirect("/manager")

    elif current_user.type() == "Seller":
        return redirect("/seller")

    elif current_user.type() == "Buyer":
        return redirect("/buyer")

    return redirect("/sign_in")


@app.route("/sign_up", methods=["GET" , "POST"])
def sign_up():
    req = request.form

    try:
        if request.method == "POST":
            success = False

            obj = Address(residence_number=req["residenceno"], street = req["street"], locality = req["locality"], pincode = req["pincode"], state = req["state"], city = req["city"])
            obj.save()

            if req["type"] == "buyer":
                success, obj = Buyer.create_buyer(password = req["password"] , name = req["name"] , email = req["email"] , address = obj, telephone = req["telephone"])

            elif req["type"] == "seller":
                success, obj = Seller.create_seller(password = req["password"] , name = req["name"] , email = req["email"] , address = obj, telephone = req["telephone"])

            if success == True:
                flash("Successful sign-up", "info")
                return redirect("/sign_in")
            else:
                flash("Unsuccessful sign up", "error")
                return redirect("/sign_up")

    except Exception as ex:
        flash("Invalid entries! Sign-up failed", "error")
        return redirect("/sign_up")

    return render_template("sign_up.html")

@app.route("/manager_sign_up", methods=["GET", "POST"])
def manager_sign_up():
    req = request.form
    try:
        if request.method == "POST":
            if req["key"] == config("MANAGERKEY"):
                obj = Address(residence_number=req["residenceno"], street = req["street"], locality = req["locality"], pincode = req["pincode"], state = req["state"],
                              city=req["city"])
                obj.save()
                dob = datetime.datetime.strptime(req['birthday'], "%Y-%m-%d")
                success, new_manager = Manager.create_manager(password = req["password"] , name = req["name"] , email = req["email"] , address = obj, telephone = req["telephone"],
                                                              dob=dob,gender=req["gender"])
                if success == True:
                    flash("Successful sign-up", "info")
                    return redirect("/sign_in")
                else:
                    flash("Successful sign-up", "info")
                    return redirect("/manager_sign_up")
            else:
                flash("Wrong sign-up key!" , "error")
                return redirect("/manager_sign_up")
    except Exception as ex:
        flash(str(ex), "error")
        return redirect("/manager_sign_up")
    return render_template("manager_sign_up.html")

@login_manager.unauthorized_handler
def unauthorized_callback():
       return redirect("sign_in")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    req = request.form
    try:
        if request.method == 'POST':
            userid = req['userid']
            password = req['password']
            user1 = signin(userid, password, "M")
            user2 = signin(userid, password, "B")
            user3 = signin(userid, password, "S")
            if user1:
                user1.is_authenticated = True
                user1.save()
                login_user(user1)
                return redirect("/manager")

            elif user2:
                user2.is_authenticated = True
                user2.save()
                login_user(user2)
                return redirect("/buyer")

            elif user3:
                user3.is_authenticated = True
                user3.save()
                login_user(user3)
                return redirect("/seller")

            if ( (not user1) and (not user2) and (not user3) ):
                raise Exception("Invalid login credentials")
    except Exception as ex:
        flash("Invalid login credentials", "error")
        return redirect("/sign_in")
    return render_template("sign_in.html")


@app.route("/sign_out")
@login_required
def sign_out():
    curr_user = current_user
    curr_user.is_authenticated = False
    curr_user.save()
    logout_user()
    return redirect("/sign_in")

########################  manager  routes   ######################

@app.route("/manager" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def manager():

    req = request.form
    if request.method == "POST":

        category = req["category"]
        name = req["name"]

        success , obj = Item.search(category,name)

        if success == False:
            flash(obj , "error")
            return render_template("manager/manager.html", items=Item.objects(), categories=Category.objects())

        return render_template("manager/manager.html", items=obj, categories=Category.objects())

    return render_template("manager/manager.html" , items = Item.objects(), categories = Category.objects())

@app.route("/manager/profile" , methods = ["GET" , "POST"])
@is_manager
@login_required
def manager_profile():
    req = request.form
    if request.method == "POST":
        if not (req["old_password"] == current_user.password):
            flash("Wrong password entered", "error")
            return redirect("/manager/profile")

        else:
            flash("Password successfully changed" , "info")
            current_user.password = req["new_password"]
            current_user.save()
            return redirect("/manager/profile")

    return render_template("manager/profile.html", manager=current_user)

@app.route("/manager/manage_buyers" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def manage_buyers():
    req = request.form
    if request.method == "POST":
        buyer_to_delete = Buyer.objects(uid = req["uid"]).first()
        buyer_to_delete.delete()

    return render_template("manager/manage_buyers.html",buyers=Buyer.objects())

@app.route("/manager/manage_sellers" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def manage_sellers():
    req = request.form
    if request.method == "POST":
        seller_to_delete = Seller.objects(uid=req["uid"]).first()
        seller_to_delete.delete()

    return render_template("manager/manage_sellers.html", sellers=Seller.objects())

@app.route("/manager/remove" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def manager_remove():
    req = request.form
    if request.method == "POST":
        item_to_delete = Item.objects(uid = req["uid"]).first()
        item_to_delete.delete()

    return redirect("/manager")

@app.route("/manager/change_category" , methods = ["GET" , "POST"])
@is_manager
@login_required
def manager_change_category():
    req = request.form
    if request.method == "POST":
        current_user.change_category(req["item"] , req["category"])

    return redirect("/manager")

@app.route("/manager/audit" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def audit():
    return render_template("manager/audit.html",payments=Transaction.objects())

@app.route("/manager/help_negotiations" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def help_negotiations():
    return render_template("manager/help_negotiations.html" , )

@app.route("/manager/add_category" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def add_category():
    req = request.form

    if request.method == "POST":
        success, new_category = Category.add_category(req["name"])

        if success == False:
            flash("Cannot make this category" , "error")
            return redirect("/manager/add_category")

    return render_template("manager/add_category.html")

@app.route("/manager/delete_category" , methods = ["GET" ,"POST"])
@is_manager
@login_required
def delete_category():

    req = request.form
    if request.method == "POST":
        success,message = Category.delete_category(req["uid"])

        if success == False:
            flash(message,"error")

    return render_template("manager/delete_category.html" , categories = Category.objects())

########################  seller  routes   ######################

@app.route("/seller" , methods = ["GET" ,"POST"])
@is_seller
@login_required
def seller():
    req = request.form
    if request.method == "POST":

        category = req["category"]
        name = req["name"]

        success , obj = Item.search(category,name)

        if success == False:
            flash(obj , "error")
            return render_template("seller/seller.html", items=Item.objects(), categories=Category.objects())

        return render_template("seller/seller.html", items=obj, categories=Category.objects())

    return render_template("seller/seller.html" , items = Item.objects(), categories = Category.objects())

@app.route("/seller/profile" , methods = ["GET" , "POST"])
@is_seller
@login_required
def seller_profile():
    req = request.form
    if request.method == "POST":
        if not (req["old_password"] == current_user.password):
            flash("Wrong password entered", "error")
            return redirect("/seller/profile")

        else:
            flash("Password successfully changed", "info")
            current_user.password = req["new_password"]
            current_user.save()
            return redirect("/seller/profile")

    return render_template("seller/profile.html", seller=current_user)

@app.route("/seller/buy_requests" , methods = ["GET" ,"POST"])
@is_seller
@login_required
def buy_requests():

    req = request.form
    if request.method == "POST":
        update_order = Order.objects(uid = req["uid"]).first()
        success,msg = update_order.negotiate(int(req["offer"]))
        if success == False:
            flash(msg,"error")
            return render_template("seller/buy_requests.html", orders=Order.objects(seller=current_user))

    return render_template("seller/buy_requests.html" , orders = Order.objects(seller = current_user))

@app.route("/seller/accept" , methods = ["GET" , "POST"])
@is_seller
@login_required
def accept_offer():

    req = request.form
    if request.method == "POST":
        current_user.update_order_status(req["uid"] , "ACCEPTED")

    return redirect("/seller/buy_requests")

@app.route("/seller/reject", methods=["GET", "POST"])
@is_seller
@login_required
def reject_offer():
    req = request.form
    if request.method == "POST":
        current_user.update_order_status(req["uid"] , "REJECTED")

    return redirect("/seller/buy_requests")

@app.route("/seller/payments" , methods = ["GET"])
@is_seller
@login_required
def pending_payments():
    return render_template("/seller/payments.html" , orders = Order.objects(seller = current_user))

@app.route("/seller/items" , methods = ["GET" ,"POST"])
@is_seller
@login_required
def items():
    req = request.form

    if request.method == "POST":
        success,obj = Item.objects(uid=req["uid"]).first().remove_item()
        if not success:
            flash(obj,"error")

    return render_template("seller/items.html",products=Item.objects(seller=Seller.objects(uid=current_user.uid).first()))

@app.route("/seller/upload_item" , methods = ["GET" ,"POST"])
@is_seller
@login_required
def upload_item():

    req = request.form

    if request.method == "POST":

        #image = request.files["image"]
        name = req["name"]
        category = req["uid"]
        price = req["price"]
        age = 0
        if "age" in req.keys() and req["age"] != "":
            age = int(req["age"])

        manufacturer = req["manufacturer"]
        descr = req["description"]

        if "is_heavy" in req.keys():
            is_heavy = req["is_heavy"]
        else:
            is_heavy = "off"
        var = False
        if is_heavy == "on":
            var = True


        success, new_item = Item.add_item(name=name, seller=current_user.uid, category=category,
                                          price=price, age=int(age),
                                          descr=descr, manufacturer_name=manufacturer,
                                          is_heavy=var)
        print(success)
        if success == False:
            flash(new_item ,"error")

    return render_template("/seller/upload_item.html" , categories = Category.objects())


@app.route("/seller/sales" , methods = ["GET" ,"POST"])
@is_seller
@login_required
def sales():
    return render_template("seller/sales.html" , payments = Transaction.objects(seller_id = current_user.uid))


########################  buyer  routes   ######################

@app.route("/buyer" , methods = ["GET" ,"POST"])
@is_buyer
@login_required
def buyer():
    req = request.form
    if request.method == "POST":

        category = req["category"]
        name = req["name"]

        success , obj = Item.search(category,name)

        if success == False:
            flash(obj , "error")
            return render_template("buyer/buyer.html", items=Item.objects(), categories=Category.objects())

        return render_template("buyer/buyer.html", items=obj, categories=Category.objects())

    return render_template("buyer/buyer.html" , items = Item.objects(), categories = Category.objects())

@app.route("/buyer/profile" , methods = ["GET" , "POST"])
@is_buyer
@login_required
def buyer_profile():
    req = request.form
    if request.method == "POST":
        if not (req["old_password"] == current_user.password):
            flash("Wrong password entered" , "error")

        else:
            flash("Password successfully changed", "info")
            current_user.password = req["new_password"]
            current_user.save()

    return render_template("buyer/profile.html" , buyer = current_user)

@app.route("/buyer/purchase_requests" , methods = ["GET" ,"POST"])
@is_buyer
@login_required
def purchase_requests():
    req = request.form
    if request.method == "POST":
        update_order = Order.objects(uid = req["uid"]).first()
        success,msg = update_order.negotiate(int(req["offer"]))

        if success == False:
            flash(msg,"error")

    return render_template("buyer/purchase_requests.html", orders = Order.objects(buyer=current_user))

@app.route("/buyer/purchases" , methods = ["GET" ,"POST"])
@is_buyer
@login_required
def purchases():
    return render_template("buyer/purchases.html",payments=Transaction.objects(buyer_id=current_user.uid))

@app.route("/buyer/raise_purchase" , methods = ["GET" ,"POST"])
@is_buyer
@login_required
def buyer_raise_purchase():
    req = request.form
    print(1)
    if request.method == "POST":
        print("HI")
        success,order_id =  current_user.raise_purchase_request(req["uid"] , req["offer"])
        print(order_id)
        if success == False:
            flash(order_id , "error")

    return redirect("/buyer")

@app.route("/buyer/payments" , methods = ["GET" ,"POST"])
@is_buyer
@login_required
def buyer_payments():
    req = request.form
    if request.method == "POST":
        success, obj = current_user.payment(req["uid"])
        print(success)
        if success == False:
            flash(obj , "error")

    return render_template("buyer/payments.html",orders=Order.objects(buyer=current_user))


