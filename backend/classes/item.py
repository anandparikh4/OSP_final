from mongoengine import Document,StringField,IntField,BooleanField,ReferenceField, CASCADE, FloatField
from backend.classes.category import Category
from backend.classes.user import Seller


class Item(Document):
    uid = StringField()
    name = StringField(required=True,min_length=1)
    seller = ReferenceField(Seller,required=True,reverse_delete_rule=CASCADE)
    category = ReferenceField(Category,required = True, reverse_delete_rule=CASCADE)
    #photo = ImageField(size=(300,300,True),required=True)
    price = FloatField(required=True,min_value=1)
    age = IntField(default=int(0))
    descr = StringField(default="")
    manufacturer_name = StringField(required=True,min_length=1)
    is_heavy = BooleanField(required=True)
    on_sale = BooleanField(default=True)

    @staticmethod
    def add_item(**kwargs):
        # try:
        item_seller = Seller.objects(uid=kwargs['seller']).first()
        if not item_seller:
            raise Exception("No such seller exists!")

        item_category = Category.objects(uid=kwargs['category']).first()
        if not item_category:
            raise Exception("No such category exists!")

        new_item = Item(name=kwargs['name'],seller=item_seller,category=item_category,price=kwargs['price'],age=kwargs['age'],
                        descr=kwargs['descr'],manufacturer_name=kwargs['manufacturer_name'],is_heavy=kwargs['is_heavy'])
        new_item.save()
        new_item.uid = str(new_item.id)
        new_item.save()
        return True, new_item.uid

        # except Exception as ex:
        #     return False, str(ex)

    def remove_item(self):
        try:
            self.delete()
            return True, "Deleted successfully"

        except Exception as ex:
            return False, str(ex)

    def change_details(self, **kwargs):
        try:
            if 'name' in kwargs:
                self.name = kwargs['name']

            if 'price' in kwargs:
                self.price = kwargs['price']

            if 'age' in kwargs:
                self.age = kwargs['age']

            if 'category' in kwargs:
                category_update = Category.objects(uid=kwargs['category']).first()
                if not category_update:
                    raise Exception("No such category exists!")
                self.category = Category.objects(uid=kwargs['category']).first()

            if 'descr' in kwargs:
                self.descr = kwargs['descr']

            if 'manufacturer_name' in kwargs:
                self.manufacturer_name = kwargs['manufacturer_name']

            if 'is_heavy' in kwargs:
                self.is_heavy = kwargs['is_heavy']

            self.save()
            return True, "Changed item details successfully"

        except Exception as ex:
            return False, str(ex)

    @staticmethod
    def search(category_search, name_search):
        if category_search == "all":
            print("All categories")
            return Item.objects(name__icontains=name_search)

        try:
            _category = Category.objects(uid = category_search).first()
            if not _category:
                raise Exception("No such category exists")

            return True,Item.objects(category=_category, name__icontains=name_search)

        except Exception as ex:
            return False, str(ex)


    # class Sold_Products(Document):
    #     uid = StringField()
    #     name = StringField(required=True)
    #     seller_name = StringField(required=True)
    #     buyer_name = StringField(required=True)
    #     sale_price = FloatField(required=True,min_value=1)
    #     photo = ImageField(size=(300,300,True),required=True)
    #     category = StringField(required=True)
    #
    # @staticmethod
    # def add_sold_product(**kwargs):
    #     sold_item = Sold_Products(name=kwargs['name'],seller_name=kwargs['seller_name'],buyer_name=kwargs['buyer_name'],sale_price=)
    #     name = kwargs['name']
    #     seller_name = kwargs['seller_name']
    #     buyer_name = kwargs['buyer_name']
    #     sale_price = kwargs['sale_price']
    #     photo = kwargs['photo']
    #     category = kwargs['category']