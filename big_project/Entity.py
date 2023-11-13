class CurrentUser:  # 当前用户类
    id = None
    name = None
    phone = None
    email = None
    username = None
    password = None

    def set_user(self, customer):
        self.id = customer[0]
        self.username = customer[1]
        self.password = customer[2]
        self.name = customer[3]
        self.phone = customer[4]
        self.email = customer[5]

    def get_user_info(self):
        return {
            'username': self.username,
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        }

class CurrentEmployee:  # 当前员工类
    id = None
    name = None
    phone = None
    email = None
    hotel_id = None
    salary = None
    department_id = None
    start_date = None
    end_date = None

    def set_employee(self, employee):
        self.id = employee[0]
        self.hotel_id = employee[1]
        self.department_id = employee[2]
        self.name = employee[3]
        self.phone = employee[4]
        self.email = employee[5]
        self.salary = employee[6]
        self.start_date = employee[7]
        self.end_date = employee[8]

class Hotel:  # 酒店类
    def __init__(self, hotel):
        self.id = hotel[0]
        self.name = hotel[1]
        self.phone = hotel[2]
        self.address = hotel[3]

    def get_hotel_info(self):
        return {
            'H_name': self.name,
            'H_phone': self.phone,
            'H_address': self.address
        }

class Room:  # 房间类
    def __init__(self, room):
        self.id = room[0]
        self.hotel_id = room[1]
        self.type = room[2]
        self.price = room[3]
        self.status = room[4]

    def get_room_info(self):
        return {
            'R_id': self.id,
            'R_H_id': self.hotel_id,
            'R_type': self.type,
            'R_price': self.price,
            'R_status': self.status
        }
