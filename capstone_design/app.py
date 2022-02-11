import psycopg2

connect = psycopg2.connect("dbname=capstone user=postgres password=********")
cur = connect.cursor()

global id
global password
global dept_name
global tot_cred
global per_result

id = 'default'
password = 'default'
dept_name = 'default'
tot_cred = 'default'


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/direct', methods=['POST'])
def direct():
    direction = request.form["send"]
    if direction == "로그인하기":
        return render_template("login.html")
    elif direction == "강의별인원보기":
        return render_template("count.html")
    elif direction == "나의선수강강의보기":
        return render_template("prereq.html")
    elif direction == "회원가입하기":
        return render_template("register.html")
    elif direction == "회원탈퇴하기":
        return render_template("withdrawl.html")
    elif direction == "전체학점수정하기":
        return render_template("credit_modi.html")


@app.route('/login', methods=['POST'])
def login():
    temp_id = request.form["id"]
    temp_password = request.form["password"]
    send = request.form["send"]

    if send == "로그인":
        cur.execute("SELECT stu_id, password, dept_name, tot_cred from student where stu_id = '" + temp_id + "';")
        result = cur.fetchall()
        if result:
            if result[0][1] == temp_password:
                global id
                global password
                global dept_name
                global tot_cred
                id = result[0][0]
                password = result[0][1]
                dept_name = result[0][2]
                tot_cred = result[0][3]
                flash("로그인에 성공하였습니다. 메인으로 이동합니다.")
                return render_template("main.html")
            else:
                flash("비밀번호가 틀렸습니다. 다시 로그인 페이지로 이동합니다.")
                return render_template("login.html")
        else:
            flash("아이디가 존재하지 않습니다. 회원가입 페이지로 이동합니다.")
            return render_template("register.html")
    elif send == "홈으로":
        return render_template("main.html")


@app.route('/count', methods=['GET'])
def count():
    statement = "with sec_takes(course_id, sec_id, count) as "
    statement += "(select course_id, sec_id, count(stu_id) "
    statement += "from section natural join takes "
    statement += "group by course_id, sec_id) "
    statement += "select course_id, sec_id, title, count "
    statement += "from course natural join sec_takes;"
    cur.execute(statement)
    result = cur.fetchall()
    return render_template("print_count.html", sections=result)


@app.route('/prereq', methods=['GET'])
def prereq():
    global id
    if id == 'default':
        flash("로그인이 안 되어있습니다. 로그인해주십시오.")
        return render_template("login.html")
    else:
        statement = "with stu_prereq(stu_id, prereq_id) as "
        statement += "(select stu_id, prereq_id "
        statement += "from student natural join takes natural join prereq "
        statement += "where stu_id = '"+id+"') "
        statement += "select stu_id, prereq_id, title, dept_name "
        statement += "from stu_prereq, course "
        statement += "where prereq_id = course_id;"
        cur.execute(statement)
        result = cur.fetchall()
        return render_template("print_prereq.html", courses=result)


@app.route('/register', methods=['POST'])
def register():
    temp_id = request.form["id"]
    temp_password = request.form["password"]
    temp_dept_name = request.form["department"]
    temp_tot_cred = request.form["total_credit"]
    send = request.form["send"]

    cur.execute("select dept_name from department;")
    result = cur.fetchall()
    department = [result[0][0], result[1][0], result[2][0]]
    if send == "회원가입":
        if temp_dept_name in department:
            statement = "insert into student values ('"+temp_id+"', '"+temp_password+"', '"+temp_dept_name+"', "+temp_tot_cred+");"
            cur.execute(statement)
            connect.commit()
            flash("회원가입에 성공하였습니다. 회원가입한 아이디 비밀번호로 로그인해주십시오.")
            return render_template("login.html")
        else:
            flash("올바른 학과이름이 아닙니다. 다시 회원가입해주십시오.")
            return render_template("register.html")
    elif send == "홈으로":
        return render_template("main.html")


@app.route('/withdrawl', methods=['POST'])
def withdrawl():
    send = request.form["send"]
    global id
    global password
    global dept_name
    global tot_cred
    if send == "회원탈퇴하기":
        if id == 'default':
            flash("로그인이 안 되어있습니다. 로그인해주십시오.")
            return render_template("login.html")
        else:
            cur.execute("delete from takes where stu_id = '"+id+"';")
            connect.commit()
            cur.execute("delete from student where stu_id = '"+id+"';")
            connect.commit()
            id = 'default'
            password = 'default'
            dept_name = 'default'
            tot_cred = 'default'
            flash("회원탈퇴에 성공하였습니다. 메인화면으로 돌아갑니다.")
            return render_template("main.html")
    elif send == "홈으로":
        return render_template("main.html")


@app.route('/sugang', methods=['GET'])
def sugang():
    global id
    global per_result
    if id == 'default':
        flash("로그인이 안 되어있습니다. 로그인해주십시오.")
        return render_template("login.html")
    else:
        statement = "select course_id, sec_id, title, dept_name from section natural join course"
        cur.execute(statement)
        per_result = cur.fetchall()
        return render_template("sugang.html", sections=per_result)


@app.route('/enroll', methods=['POST'])
def enroll():
    global per_result
    send = request.form["send"]
    global id
    global password
    global dept_name
    global tot_cred
    if id == 'default':
        flash("로그인이 안 되어있습니다. 로그인해주십시오.")
        return render_template("login.html")
    else:
        if send[-1] == '1':
            if dept_name != 'Computer Science':
                flash("학과가 다릅니다.")
                return render_template("sugang.html", sections=per_result)
            elif int(tot_cred) >= 130:
                flash("학점 초과입니다.")
                return render_template("sugang.html", sections=per_result)
            else:
                cur.execute("select course_id, sec_id from takes where stu_id = '"+id+"';")
                result = cur.fetchall()
                if ('10222', '2',) in result:
                    flash("이미 수강신청하였습니다.")
                    return render_template("sugang.html", sections=per_result)
                else:
                    cur.execute("insert into takes values ('"+id+"', '10222', '2');")
                    flash("수강신청에 성공하였습니다.")
                    connect.commit()
                    return render_template("sugang.html", sections=per_result)
        elif send[-1] == '2':
            if dept_name != 'Computer Science':
                flash("학과가 다릅니다.")
                return render_template("sugang.html", sections=per_result)
            elif int(tot_cred) >= 130:
                flash("학점 초과입니다.")
                return render_template("sugang.html", sections=per_result)
            else:
                cur.execute("select course_id, sec_id from takes where stu_id = '"+id+"';")
                result = cur.fetchall()
                if ('10333', '3',) in result:
                    flash("이미 수강신청하였습니다.")
                    return render_template("sugang.html", sections=per_result)
                else:
                    cur.execute("insert into takes values ('"+id+"', '10333', '3');")
                    flash("수강신청에 성공하였습니다.")
                    connect.commit()
                    return render_template("sugang.html", sections=per_result)
        elif send[-1] == '3':
            if dept_name != 'Mathematics':
                flash("학과가 다릅니다.")
                return render_template("sugang.html", sections=per_result)
            elif int(tot_cred) >= 130:
                flash("학점 초과입니다.")
                return render_template("sugang.html", sections=per_result)
            else:
                cur.execute("select course_id, sec_id from takes where stu_id = '"+id+"';")
                result = cur.fetchall()
                if ('20111', '1',) in result:
                    flash("이미 수강신청하였습니다.")
                    return render_template("sugang.html", sections=per_result)
                else:
                    cur.execute("insert into takes values ('"+id+"', '20111', '1');")
                    flash("수강신청에 성공하였습니다.")
                    connect.commit()
                    return render_template("sugang.html", sections=per_result)
        elif send[-1] == '4':
            if dept_name != 'Mathematics':
                flash("학과가 다릅니다.")
                return render_template("sugang.html", sections=per_result)
            elif int(tot_cred) >= 130:
                flash("학점 초과입니다.")
                return render_template("sugang.html", sections=per_result)
            else:
                cur.execute("select course_id, sec_id from takes where stu_id = '"+id+"';")
                result = cur.fetchall()
                if ('20222', '5',) in result:
                    flash("이미 수강신청하였습니다.")
                    return render_template("sugang.html", sections=per_result)
                else:
                    cur.execute("insert into takes values ('"+id+"', '20222', '5');")
                    flash("수강신청에 성공하였습니다.")
                    connect.commit()
                    return render_template("sugang.html", sections=per_result)
        elif send[-1] == '5':
            if dept_name != 'Biology':
                flash("학과가 다릅니다.")
                return render_template("sugang.html", sections=per_result)
            elif int(tot_cred) >= 130:
                flash("학점 초과입니다.")
                return render_template("sugang.html", sections=per_result)
            else:
                cur.execute("select course_id, sec_id from takes where stu_id = '"+id+"';")
                result = cur.fetchall()
                if ('30333', '4',) in result:
                    flash("이미 수강신청하였습니다.")
                    return render_template("sugang.html", sections=per_result)
                else:
                    cur.execute("insert into takes values ('"+id+"', '30333', '4');")
                    flash("수강신청에 성공하였습니다.")
                    connect.commit()
                    return render_template("sugang.html", sections=per_result)


@app.route('/credit_modi', methods=['POST'])
def credit_modi():
    global id
    global password
    global dept_name
    global tot_cred

    send = request.form["send"]
    temp_tot_cred = str(request.form["tot_credit"])
    if send == "홈으로":
        return render_template("main.html")
    elif send == "수정하기":
        if id == 'default':
            flash("로그인이 안 되어있습니다. 로그인해주십시오.")
            return render_template("login.html")
        else:
            tot_cred = temp_tot_cred
            cur.execute("update student set tot_cred = "+tot_cred+" where stu_id = '" + id + "';")
            connect.commit()
            flash("전체학점 수정에 성공하였습니다. 메인페이지로 돌아갑니다.")
            return render_template("main.html")


if __name__ == '__main__':
    app.debug = True
    app.config["SECRET_KEY"] = "ABCD"
    app.run()
