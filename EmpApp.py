from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__,template_folder="templates",static_folder= 'templates/static')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

    
@app.route("/del")
def Delete():
    return render_template("deleteEmployee.html")

@app.route("/edit")
def Edit():
    return render_template("EditEmp.html")    

@app.route("/show")
def ViewProfile():
    return render_template("GetEmpOutput.html")    


@app.route("/add")
def Add():
    return render_template('addEmployee.html')  

@app.route("/editpayroll")
def editpayroll():
    return render_template('EditPayroll.html')    

@app.route("/payroll")
def Payroll():
    return render_template('EmpPayroll.html')    

@app.route("/delpayroll")
def delpayroll():
    return render_template('DelPayroll.html')      


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/getdata",methods=['POST'])
def getData():
    emp_id = request.form['emp_id']

    rtr_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchome()
    cursor.close()
    return render_template('GetEmpOutput.html', user = user)

@app.route("/delemp", methods=['POST'])
def getDataDeleteEmployee():
    emp_id = request.form['emp_id']

    rtr_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('DelEmpOutput.html', id = emp_id)

@app.route("/getdataemp", methods=['POST'])
def getDataEmp():
    emp_id = request.form['emp_id']

    rtr_sql = "SELECT * FROM employee WHERE emp_id =%s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()

    return render_template('EditProfile.html', user = user)

@app.route("/editemp",methods=['POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']
    first_name = request.form["first_name"]
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    department = request.form['department']
    hire_date = request.form['hire_date']

    rtr_sql = "UPDATE employee SET first_name=%s,last_name=%s,pri_skill=%s,location=%s,department=%s,hire_date=%s WHERE emp_id =%s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(first_name,last_name,pri_skill,location,department,hire_date,emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()

    return render_template('EditEmpOutput.html', id = emp_id)

@app.route("/editpayroll", methods=['POST'])
def UpdatePayroll():
    emp_id = request.form['emp_id']
    salary = request.form['salary']
    epf = request.form['epf']
    socso = request.form['socso']
    net_salary = request.form['net_salary']

    rtr_sql = "UPDATE payroll SET salary=%s,epf=%s,socso=%s,net_salary=%s WHERE emp_id =%s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(salary,epf,socso,net_salary,emp_id))
    db_conn.commit()
    payroll = cursor.fetchone()
    cursor.close()

    return render_template('EditPayrollOutput.html', id = emp_id)


@app.route("/addpayroll", methods=['POST'])
def AddPayroll():
    emp_id = request.form['emp_id']
    salary = request.form['salary']
    epf = request.form['epf']
    socso = request.form['socso']
    net_salary = request.form['net_salary']

    insert_sql = "INSERT INTO payroll VALUES (%s,%s,%s,%s,%s)"
    cursor = db_conn.cursor()
    cursor.execute(insert_sql,(emp_id,salary,epf,socso,net_salary))
    db_conn.commit()
    payroll = cursor.fetchone()
    cursor.close()

    return render_template("AddPayrollOutput.html", id = emp_id)

@app.route("/delpayroll", methods = ['POST'])
def DelPayroll():
    emp_id = request.form['emp_id']

    rtr_sql = "DELETE FROM payroll WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('DelPayrollOutput.html', id = emp_id)

@app.route("/getpayroll", methods=['POST'])
def getPayroll():

    emp_id = request.form['emp_id']

    rtr_sql = "SELECT * FROM payroll WHERE emp_id =%s"
    cursor = db_conn.cursor()
    cursor.execute(rtr_sql,(emp_id))
    db_conn.commit()
    payroll = cursor.fetchone()
    cursor.close()

    return render_template('EditPayrollDetail.html', payroll = payroll)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    department = request.form['department']
    hire_date = request.form['hire_date']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s,%s,%s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, department, hire_date))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
