from mongoengine import Document,StringField,EmailField,IntField,DateField,ReferenceField,NULLIFY,BooleanField
from backend.classes.address import Address
from backend.classes.category import Category
from backend.interface.sign_up import send_email

TYPE = ("Manager" , "Buyer" , "Seller")
GENDER = ("Male" , "Female")

class User(Document):
    uid = StringField()
    password = StringField(minlength = 8,required = True)
    name = StringField(required = True,minlength = 1)
    email = EmailField(required = True)
    address = ReferenceField(Address,required=True,reverse_delete_rule=NULLIFY)
    telephone = IntField(required=True, min_value=1000000000, max_value=9999999999)

    is_authenticated = BooleanField(default = False)
    is_anonymous = BooleanField(default = False)
    is_active = BooleanField(default = True)

    def get_id(self):
        return self.uid

    meta = {'allow_inheritance' : True}

    def change_data(self,**kwargs):
        try:
            if "name" in kwargs :
                self.name = kwargs["name"]
            if "email" in kwargs:
                self.email = kwargs["email"]
            if "address" in kwargs:
                self.address = kwargs["address"]
            if "telephone" in kwargs:
                self.telephone = kwargs["telephone"]
            self.save()
            return (True, "Profile information updated successfully")

        except Exception as ex:
            return False, str(ex)

    def change_password(self,oldpass, newpass):
        try:
            if oldpass != self.password :
                raise Exception("Wrong password!")
            self.password = newpass
            self.save()
            return True, "Password changed"

        except Exception as ex:
            return False,str(ex)


class Manager(User):
    gender = StringField(required=True, choices=GENDER)
    dob = DateField(required=True)

    @staticmethod
    def create_manager(**kwargs):
        try:
            new_manager = Manager(
                password = kwargs["password"],
                name = kwargs["name"],
                email = kwargs["email"],
                address = kwargs["address"],
                telephone = kwargs["telephone"],
                gender = kwargs["gender"],
                dob = kwargs["dob"]
            )
            new_manager.save()
            new_manager.uid = str(new_manager.id)
            new_manager.save()
            mail_txt = f"""Hi {new_manager.name}
            
            Greetings from Team OSP. Your login credentials are stated below.
                            
            User-ID: {new_manager.uid}
            Password: {new_manager.password}
                
            Regards,
            Team OSP
            """
            send_email("Your \"Manager\" account credentials",mail_txt,new_manager.email)
            return True,new_manager.uid

        except Exception as ex:
            return False, str(ex)

    def type(self):
        return "Manager"

    # @staticmethod
    # def signup_key():                       # mimicking static variables
    #     return str("for_managers_only")


    def change_category(self, item_id, category_id):
        from backend.classes.item import Item
        try:
            item_ = Item.objects(uid=item_id).first()
            if not item_:
                raise Exception("No such item found!")

            category_ = Category.objects(uid=category_id).first()
            if not category_:
                raise Exception("No such category exists!")

            item_.category = category_
            item_.save()

        except Exception as ex:
            return False,str(ex)


    # for adding and removing categories, the static add and remove categories of the class Category can be used directly. No special methods are required in class Manager
    # similarly for deleting items, the static method delete item of class Item can be used directly


    def manage_seller(self,seller_id):
        try:
            seller = Seller.objects(uid=seller_id).first()
            if seller:
                seller.delete()
                return True, "Seller deleted"
            else :
                raise Exception("No such seller found!")

        except Exception as ex:
            return False, str(ex)

    def manage_buyer(self, buyer_id):
        try:
            buyer = Buyer.objects(uid=buyer_id).first()
            if buyer:
                buyer.delete()
                return True, "Buyer deleted"
            else:
                raise Exception("No such buyer found!")

        except Exception as ex:
            return  False, str(ex)

    @staticmethod
    def audit(): #check
        try:
            from backend.classes.order import Transaction
            return True, Transaction.objects() #check
        except Exception as ex:
            return False, str(ex)

    def negotiations(self,order_id): #check
        try:
            from backend.classes.order import Order
            return True, Order.objects(uid=order_id).first()
        except Exception as ex:
            return False, str(ex)

class Seller(User):
    # for adding and deleting products, static methods of Class Item can be used

    @staticmethod
    def create_seller(**kwargs):
        try:
            new_seller = Seller(
                password = kwargs["password"],
                name = kwargs["name"],
                email = kwargs["email"],
                address = kwargs["address"],
                telephone = kwargs["telephone"]
            )

            new_seller.save()
            new_seller.uid = str(new_seller.id)
            new_seller.save()
            mail_txt = f"""Hi {new_seller.name}
            
            Greetings from Team OSP. Your login credentials are stated below.
    
            User-ID: {new_seller.uid}
            Password: {new_seller.password}
    
            Regards,
            Team OSP
            """
            send_email("Your \"Seller\" account credentials", mail_txt, new_seller.email)
            return True, new_seller.uid

        except Exception as ex:
            return False, str(ex)


    def type(self):
        return "Seller"

    def view_pending_orders(self):
         from backend.classes.order import Order
         return Order.objects(seller=self)

    def view_sales(self):
         from backend.classes.order import Transaction
         return Transaction.objects(seller = self)

    def negotiate(self,order_id,offer):
        from backend.classes.order import Order
        try:
            order = Order.objects(uid = order_id).first()
            order.negotiate(offer)
            return True,"Offer Placed"

        except Exception as ex:
            return False, str(ex)
                                                       # order is an object of class Order
    def update_order_status(self,order_id,status):     # status is an enumeration of REQUEST_STATUS
        from backend.classes.order import Order,Transaction
        try:
            order = Order.objects(uid = order_id).first()
            if not order:
                raise Exception("No such order found!")

            if status == "ACCEPTED":
                mail_txt = f'''Hi {order.buyer.name}
                
                Greetings from Team OSP. 
                
                Your purchase request for the Item: {order.item.name}, Item_ID: {order.item.uid}
                has been approved by the Seller: {order.seller.name}, Seller_ID: {order.seller.uid} and the offer price
                is {order.offer_price}. Kindly make payment from the portal to receive the delivery. 
    
                Regards,
                Team OSP
                '''
                send_email("Approval of your purchase request", mail_txt,order.buyer.email)

                order.request_status = "ACCEPTED"
                order.save()
                return True, "Request ACCEPTED"

            elif status == "REJECTED":

                mail_txt = f'''Hi {order.buyer.name}.
                Greetings from team OSP. 
                Your purchase request for Item: {order.item.name} , ItemId: {order.item.uid} has been rejected by 
                Seller: {order.seller.name}, SellerId: {order.seller.uid}.

                Regards,
                Team OSP
                '''
                send_email("Rejection of Purchase Request",mail_txt,order.buyer.email)

                order.item.on_sale = True
                order.item.save()
                order.delete()
                return True, "Request rejected"

        except Exception as ex:
            return False, str(ex)


class Buyer(User):

    @staticmethod
    def create_buyer(**kwargs):
        try:
            print("Hello first")
            new_buyer = Buyer(
                password = kwargs["password"],
                name = kwargs["name"],
                email = kwargs["email"],
                address = kwargs["address"],
                telephone = kwargs["telephone"]
            )

            new_buyer.save()
            new_buyer.uid = str(new_buyer.id)
            new_buyer.save()

            mail_txt = f"""Hi {new_buyer.name}
            Greetings from Team OSP. Your login credentials are stated below.
    
            User-ID: {new_buyer.uid}
            Password: {new_buyer.password}
    
            Regards,
            Team OSP
            """
            send_email("Your \"Buyer\" account credentials", mail_txt, new_buyer.email)
            return True, new_buyer.uid

        except Exception as ex:
            return False,str(ex)


    def type(self):
        return "Buyer"

    def raise_purchase_request(self,item_id,offer):
        from backend.classes.order import Order
        from backend.classes.item import Item
        try:
            item = Item.objects(uid = item_id).first()
            if not item :
                raise Exception("No such item found!")

            seller = Seller.objects(uid = item.seller.uid).first()
            if not seller :
                raise Exception("No such seller found!")

            order_id = Order.create_order(offer_price = offer , item = item.uid , seller = seller.uid , buyer = self.uid)
            item.on_sale = False
            item.save()

            mail_txt = f'''Hi {item.seller.name}
            
            Greetings from Team OSP. A new purchase request has been raised by the Buyer: {self.name}, Buyer_ID: {self.uid}
            for the Item: {item.name}, Item_ID: {item.uid} and the offer price is {offer}.
               
            The buyer's details are mentioned below:
            Name: {self.name}
            Mail ID: {self.email}
            Telephone No.: {self.telephone}
            
            Regards,
            Team OSP
            '''

            send_email("New Purchase request for your item",mail_txt,seller.email)

            mail_txt2 = f'''Hi {self.name}
            
            Greetings from Team OSP. Your purchase request for the Item: {item.name}, Item_ID: {item.uid} has been
            raised with the offer price is {offer}.
            Seller's details are mentioned below:   
            Name: {seller.name}
            Mail id: {seller.email}
            Telephone No.: {seller.telephone}
            
            Regards,
            Team OSP
            '''
            send_email("Your purchase request",mail_txt2,self.email)
            return True, order_id

        except Exception as ex:
            return False, str(ex)

    def negotiate(self,order_id,offer):
        from backend.classes.order import Order
        try:
            order = Order.objects(uid = order_id).first()
            if not order :
                raise Exception("No such order exists!")

            order.negotiate(offer)
            return True, "Negotiation request placed"

        except Exception as ex:
            return False, str(ex)

    def payment(self,order_id):
        from backend.classes.order import Order,Transaction
        try:
            order = Order.objects(uid = order_id).first()
            if not order :
                raise Exception("No such order exists!")

            if order.request_status == "ACCEPTED":
                transaction_id = Transaction.create_transaction(order_id)
                order.item.delete()                 # check cascade deletion
                order.delete()
                return True, transaction_id

            else:
                return False, "Request has not yet been approved"

        except Exception as ex:
            return True, str(ex)


    def view_pending_orders(self):
         from backend.classes.order import Order
         return Order.objects(buyer=self)

    def view_purchases(self):
         from backend.classes.order import Transaction
         return Transaction.objects(buyer = self)
