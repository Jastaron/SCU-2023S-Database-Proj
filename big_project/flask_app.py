import datetime
from app_config import *
from Entity import *

cu = CurrentUser()
ce = CurrentEmployee()

# 酒店首页
@app.route('/Home', methods=['GET', 'POST'])
def index_logined():
    return render_template('hotel_index_logined.html')

# 登录界面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 查询客户表中是否有该用户
        username = request.form['username']
        password = request.form['password']

        # 判断是否为工作人员
        if username == password and username[0] == 'e':
            e_id = username.split('e')[1]
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM Employee WHERE Employee_id = {e_id}")
            rv = cur.fetchone()
            if not rv:
                return render_template('sign-in_nouser.html')

            # 设定当前工作人员信息
            ce.set_employee(rv)

            # 判断是否为管理人员
            check_manager_sql = f"SELECT Manage_authority FROM Department WHERE Department_id = {rv[2]}"
            cur.execute(check_manager_sql)
            rv = cur.fetchone()[0]
            cur.close()
            if rv == 1:
                return redirect(url_for('counter_home'))
            else:
                return "普通员工"

        conn = mysql.connection
        cur = conn.cursor()
        check_customer_sql = f'SELECT * FROM Customer WHERE C_username = {repr(username)}'
        cur.execute(check_customer_sql)
        customer = cur.fetchone()
        cur.close()
        if customer:
            if bcrypt.check_password_hash(customer[2], password):
                cu.set_user(customer)
                return redirect(url_for('index_logined'))
            else:
                return render_template('sign-in_wrong_pswd.html')
        else:
            return render_template('sign-in_nouser.html')
    return render_template('sign-in.html')

# 注册界面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 检查密码是否匹配
        if password != confirm_password:
            return render_template('register_confirm_pswd_wrong.html')

        # 对密码进行散列存储
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # mysql连接
        conn = mysql.connection
        cur = conn.cursor()

        # 插入用户信息到数据库的 Customer 表中
        insert_customer_sql = \
            "INSERT INTO customer (C_Name, C_Phone, C_email, C_username, C_password) " \
            f"VALUES ({repr(name)}, {phone}, {repr(email)}, {repr(username)}, {repr(hashed_password)});"

        check_customer_username_sql = \
            f"SELECT * FROM customer WHERE C_username = {repr(username)};"

        cur.execute(check_customer_username_sql)
        rv = cur.fetchone()
        if rv:
            return render_template('register_username.html')
        try:
            cur.execute(insert_customer_sql)
            conn.commit()
            cur.close()
            flash('注册成功，请登录', 'success')
            print("注册成功")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'注册失败：{str(e)}', 'error')
            print("注册失败")
            return redirect(url_for('register'))
    return render_template('register.html')

# 江安西园酒店页面
@app.route('/west-garden-hotel', methods=['GET', 'POST'])
def west_garden_hotel():
    conn = mysql.connection
    cur = conn.cursor()
    get_hotel_info_sql = f'SELECT * FROM Hotel WHERE H_Name = "江安西园酒店"'
    cur.execute(get_hotel_info_sql)
    rv = cur.fetchone()
    wg_hotel = Hotel(rv)
    cur.close()
    return render_template('west-garden-hotel.html', data=wg_hotel.get_hotel_info())

# 江安西园房间页面
@app.route('/west-garden-rooms', methods=['GET', 'POST'])
def west_garden_rooms():
    return render_template('west-garden-rooms.html')

# 江安西园大床房界面
@app.route('/west-garden-bigbed', methods=['GET', 'POST'])
def west_garden_bigbed():
    if request.method == 'POST':
        tenant_name = request.form['name']
        tenant_phone = request.form['phone']
        tenant_PRC_id = request.form['PRC_id']
        tenant_start_time = request.form['start_time']
        tenant_leaving_time = request.form['leaving_time']
        today = str(datetime.date.today())
        conn = mysql.connection
        cur = conn.cursor()
        insert_order_sql = \
            "INSERT INTO `order` (Hotel_id, Customer_id, tenant_name, tenant_phone, " \
            "tenant_PRC_id, `Status`, Order_date, Check_in_date, Leaving_date, Desire_type)" \
            f"VALUES (1, {cu.id}, {repr(tenant_name)}, {tenant_phone}, {repr(tenant_PRC_id)}, " \
            f"'未入住', {repr(today)}, {repr(tenant_start_time)}, {repr(tenant_leaving_time)}, '大床房');"
        cur.execute(insert_order_sql)
        conn.commit()
        cur.close()
        return redirect(url_for('index_logined'))
    return render_template('west-garden-bigbed.html')

# 用户个人界面
@app.route('/user-page')
def user_page():
    data = cu.get_user_info()
    return render_template('user-page.html', data=data)

# 用户订单界面
@app.route('/user-orders', methods=['GET', 'POST'])
def user_orders():
    conn = mysql.connection
    cur = conn.cursor()
    get_orders_sql = f"SELECT * FROM `order` NATURAL JOIN `hotel` WHERE Customer_id = {cu.id};"
    cur.execute(get_orders_sql)
    rv = cur.fetchall()
    items = []
    for i in rv:
        items.append({
            'Order_id': i[1],
            'Hotel_name': i[13],
            'tenant_name': i[4],
            'Desire_Type': i[11],
            'Check_in_date': i[9],
            'Leaving_date': i[10],
            'Current_status': i[7]
        })
    cur.close()
    return render_template('user-orders.html', items=items)

# 用户取消订单
@app.route('/user-order-cancel', methods=['GET'])
def user_order_cancel():
    conn = mysql.connection
    cur = conn.cursor()
    o_id = request.args.get('id')
    delete_orders_sql = f"UPDATE `order` SET `Status` = '已取消' WHERE order_id = {o_id};"
    cur.execute(delete_orders_sql)
    conn.commit()
    cur.close()
    return redirect(url_for('user_orders'))

# 用户更改个人信息
@app.route('/user-info-change', methods=['GET', 'POST'])
def user_info_change():
    if request.method == 'POST':
        c_name = request.form['name']
        c_phone = request.form['phone']
        c_email = request.form['email']
        c_username = request.form['username']
        c_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        conn = mysql.connection
        cur = conn.cursor()
        try:
            user_info_change_sql = \
                f"UPDATE customer SET C_name = {c_name}, C_phone = {c_phone}, " \
                f"C_email = {c_email}, C_username = {c_username}, C_password = {c_password} " \
                f"WHERE customer_id = {cu.id};"
            cur.execute(user_info_change_sql)
            conn.commit()
            return redirect(url_for('user_page'))
        except:
            pass
    return render_template('/user-info-change.html', cu=cu.get_user_info())


# 员工服务主页
@app.route('/counter-home', methods=['GET', 'POST'])
def counter_home():
    hotel_id = ce.hotel_id
    conn = mysql.connection
    cur = conn.cursor()
    if request.method == 'POST':
        r_id = request.form['room_id']
        lb = request.form['lower_bound']
        ub = request.form['upper_bound']
        rt = request.form['room_type']
        rs = request.form['room_status']
        # print(f"lb:{lb}\nub:{ub}\nrt:{rt}")

        get_rooms_sql = f"SELECT * FROM Room WHERE Hotel_id = {hotel_id}"
        if r_id != "":
            get_rooms_sql += f" AND Room_id = {r_id}"
        else:
            if lb != "":
                get_rooms_sql += f" AND Price >= {lb}"
            if ub != "":
                get_rooms_sql += f" AND Price <= {ub}"
            if rt != "":
                get_rooms_sql += f" AND Type = {repr(rt)}"
            if rs != "":
                get_rooms_sql += f" AND Status = {repr(rs)}"
            get_rooms_sql += ";"
    else:
        get_rooms_sql = f"SELECT * FROM Room WHERE Hotel_id = {hotel_id} LIMIT 20;"
    cur.execute(get_rooms_sql)
    rv = cur.fetchall()
    items = []
    for r in rv:
        room = Room(r)
        items.append(room.get_room_info())
    return render_template('/counter-home.html', items=items)

# 办理入住业务
@app.route('/room-checkin', methods=['GET', 'POST'])
def room_checkin():
    conn = mysql.connection
    cur = conn.cursor()
    if request.method == 'POST':
        r_id = request.form['r_id']
        o_id = request.form['o_id']
        cur.execute("START TRANSACTION;")
        try:
            cur.execute(f"CALL check_in({r_id},{ce.hotel_id},{o_id});")
            cur.execute("COMMIT;")
        except:
            cur.execute("ROLLBACK;")
        conn.commit()
        cur.close()
        return redirect(url_for('counter_home'))
    else:
        r_id = request.args.get('id')
        not_cIn_sql = f"SELECT * FROM `Order` WHERE Hotel_id = {ce.hotel_id} AND `Status` = '未入住';"
        cur.execute(not_cIn_sql)
        rv = cur.fetchall()
        items = []
        for r in rv:
            items.append({
                'Order_id': r[0],
                'tenant_name': r[4],
                'tenant_phone': r[5],
                'tenant_PRC_id': r[6],
                'Check_in_date': r[9],
                'Leaving_date': r[10],
                'Desire_Type': r[11]
            })
        cur.close()
        return render_template('/room-check-in.html', room_id=r_id, items=items)

# 办理退房业务
@app.route('/room-checkout', methods=['GET', 'POST'])
def room_checkout():
    r_id = request.args.get('id')
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("START TRANSACTION;")
    try:
        cur.execute(f"SELECT Price FROM room WHERE room_id = {r_id} AND HOTEL_id = {ce.hotel_id};")
        price = cur.fetchone()[0]
        cur.execute(f"SELECT order_id, check_in_date FROM `order` WHERE room_id = {r_id} AND `Status` = '入住中';")
        rv = cur.fetchone()
        order_id = rv[0]
        today = datetime.date.today()
        cin_date = rv[1]
        days = (today-cin_date).days
        deal_price = price * days
        update_order_sql = f"UPDATE `order` SET Deal_Price = {deal_price}, `Status` = '已完成' WHERE order_id = {order_id};"
        cur.execute(update_order_sql)
        update_room_sql = f"UPDATE room SET `Status` = '空闲' WHERE room_id = {r_id} AND hotel_id = {ce.hotel_id};"
        cur.execute(update_room_sql)
        cur.execute("COMMIT;")
    except:
        cur.execute("ROLLBACK;")
    finally:
        conn.commit()
        cur.close()
        return redirect(url_for('counter_home'))

# 订单界面
@app.route('/counter-orders', methods=['GET', 'POST'])
def counter_orders():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM `order` WHERE Hotel_id = {ce.hotel_id}")
    rv = cur.fetchall()
    items = []
    for r in rv:
        items.append({
            'Order_id': r[0],
            'Room_id': r[2],
            'tenant_name': r[4],
            'tenant_phone': r[5],
            'tenant_PRC_id': r[6],
            'Order_date': r[8],
            'Check_in_date': r[9],
            'Leaving_date': r[10],
            'desireType': r[11],
            'order_status': r[7]
        })
    return render_template('counter-orders.html', items=items)

# 修改房间信息界面
@app.route('/room-change', methods=['GET', 'POST'])
def room_change():
    r_id = request.args.get('id')
    conn = mysql.connection
    cur = conn.cursor()
    if request.method == 'POST':
        r_type = request.form['r_type']
        r_price = request.form['r_price']
        r_status = request.form['r_status']
        try:
            cur.execute(f"UPDATE room SET type = {r_type}, price = {r_price}, `Status` = {r_status} WHERE room_id = {r_id} AND hotel_id = {ce.hotel_id};")
            conn.commit()
        except:
            print(r_id, r_type, r_price, r_status)
        cur.close()
        return redirect(url_for('counter_home'))
    cur.execute(f"SELECT * FROM room WHERE room_id = {r_id} AND hotel_id = {ce.hotel_id};")
    rv = cur.fetchone()
    room = Room(rv)
    cur.close()
    return render_template('room-change.html', room=room.get_room_info())

# 删除订单
@app.route('/delete-order', methods=['GET'])
def delete_order():
    o_id = request.args.get('id')
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute('START TRANSACTION;')
    try:
        cur.execute(f"DELETE FROM `order` WHERE order_id = {o_id}")
        cur.execute("COMMIT;")
    except:
        cur.execute("ROLLBACK;")
    finally:
        conn.commit()
        cur.close()
        return redirect(url_for('counter_orders'))

if __name__ == '__main__':
    app.run()