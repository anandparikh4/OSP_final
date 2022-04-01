def signin(user_id, user_password, type): #type can be M,B or S
    from backend.classes.user import Buyer, Seller, Manager
    ans = None
    if type == "M":
        ans = Manager.objects(uid=user_id,password=user_password).first()

    elif type == "B":
        ans = Buyer.objects(uid=user_id,password=user_password).first()

    elif type == "S":
        ans = Seller.objects(uid=user_id,password=user_password).first()

    return ans #what to return please check
