from pyexpat import features
from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nk***777",
    database="agripredict"
)

cursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secure-key'

# Load Model
model = joblib.load('crop_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')


@app.route('/')
def home():
    return render_template('home.html', crop=None, confidence=None)


@app.route('/about')
def about():

    email = None

    message = request.args.get('message')

    if 'user' in session:

        cursor.execute(
            "SELECT email FROM users WHERE username=%s",
            (session['user'],)
        )

        user = cursor.fetchone()

        if user:
            email = user[0]

    return render_template(
        'about.html',
        email=email,
        message=message
    )


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))

    message = request.args.get('message')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            message = 'Invalid username or password.'
    return render_template('login.html', message=message)


@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
@app.route('/new-registration', methods=['GET', 'POST'])
@app.route('/new-registration/', methods=['GET', 'POST'])
def register():

    if 'user' in session:
        return redirect(url_for('home'))

    message = None

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:

            message = 'Please enter all fields.'

        elif password != confirm_password:

            message = 'Passwords do not match. Please try again.'

        else:

            cursor.execute(
                "SELECT * FROM users WHERE username=%s",
                (username,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                message = "Username already exists."

            else:

                cursor.execute(
                    "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
                    (username, email, password)
                )

                mydb.commit()

                return redirect(
                    url_for(
                        'login',
                        message='Registration successful. Please login.'
                    )
                )

    return render_template(
        'register.html',
        message=message
    )



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('predict.html', crop=None, confidence=None)

    try:
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # Validation
        if (
            N < 0 or
            P < 0 or
            K < 0 or
            temperature < 0 or
            humidity < 0 or
            ph < 0 or
            rainfall < 0
        ):

            return render_template(
                'predict.html',
                crop='Invalid Input',
                confidence=0
            )

        # Feature Engineering
        # The saved model was trained on the original 7 input features.
        features = [[
            N,
            P,
            K,
            temperature,
            humidity,
            ph,
            rainfall
        ]]

        prediction = model.predict(features)[0]

        crop_name = label_encoder.inverse_transform(
            [prediction]
            )[0]

        probability = max(
            model.predict_proba(features)[0]
            ) * 100

        # Save Prediction History
        cursor.execute(
             """
             INSERT INTO prediction_history
             (
                username,
                nitrogen,
                phosphorus,
                potassium,
                temperature,
                humidity,
                ph,
                rainfall,
                predicted_crop,
                confidence
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                session['user'],
                N,
                P,
                K,
                temperature,
                humidity,
                ph,
                rainfall,
                crop_name.upper(),
                round(probability, 2)
            )
        )
        mydb.commit()

        return render_template(
            'predict.html',
            crop=crop_name.upper(),
            confidence=round(probability, 2)
            )

    except Exception as e:

        return render_template(
            'predict.html',
            crop=f'Error: {e}',
            confidence=0
        )

@app.route('/subscribe', methods=['POST'])
def subscribe():

    email = request.form['email']

    cursor.execute(
        "SELECT * FROM subscribers WHERE email=%s",
        (email,)
    )

    existing = cursor.fetchone()

    if existing:
        message = "This email is already subscribed."

    else:
        cursor.execute(
            "INSERT INTO subscribers(email) VALUES(%s)",
            (email,)
        )

        mydb.commit()

        message = "Subscribed Successfully!"

    return redirect(url_for('about', message=message))

if __name__ == '__main__':
    app.run(debug=True)