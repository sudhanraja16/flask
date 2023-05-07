import base64
import os

import psycopg2
from flask import Flask, render_template, request,redirect
from keras_preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.applications.vgg16 import preprocess_input
import os
from tensorflow.keras.preprocessing import image

from flask import Flask,render_template,request
from tensorflow.keras.models import load_model
from unicodedata import category

conn = psycopg2.connect(
    host="localhost",
    database="plantuser",
    user="postgres",
    password="1234",
    port="5432"
)
cursor = conn.cursor()

app = Flask(__name__)

model = load_model('ricpot.h5')

target_img = os.path.join(os.getcwd(), 'static/images')

model1 = load_model('cortom.h5')
target_img1 = os.path.join(os.getcwd(), 'static/images')

model2 = load_model('jackstraw.h5')
target_img2 = os.path.join(os.getcwd(), 'static/images')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/succoured')
def succoured():
    return render_template('succoured.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        mobilenumber = request.form["mobilenumber"]
        category = request.form["category"]
        password = request.form["password"]
        if not fullname or not username or not email or not mobilenumber or not category or not password:
            return render_template('reg.html', error="please enter all required fields")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO registration (fullname, username, email, mobilenumber, category, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (fullname, username, email, mobilenumber, category, password)
            )
            conn.commit()
        return render_template('succoured.html')
    else:
        return render_template('reg.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        category = request.form['category']
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM registration WHERE username = %s AND password = %s AND category = %s",
                (username, password, category)
            )
            user = cur.fetchone()
        if user:
            if category == 'Farmer':
                return redirect('/farmerhome')
            elif category == 'Expert':
                return redirect('/index')
        else:
            return render_template('login.html', error="Incorrect username or password or category")
    else:
        return render_template('login.html')


@app.route('/farmerhome', methods=['GET', 'POST'])
def farmerhome():
    category = request.args.get('category')  # obtain category from request

    if category == 'Rice and Potato':
        return redirect('/classify')
    elif category == 'Corn and Tomato':
        return redirect('/classify1')
    elif category == 'Jackfruit and Strawberry':
        return redirect('/classify2')
    else:
        return render_template('farmerhome.html', error="Incorrect category")


@app.route('/experthome')
def experthome():
    return render_template('experthome.html')

@app.route('/classify')
def classify():
    return render_template('classify.html')

@app.route('/classify1')
def classify1():
    return render_template('classify1.html')

@app.route('/classify2')
def classify2():
    return render_template('classify2.html')




ALLOWED_EXT = {'jpg','JPG', 'jpeg', 'png'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXT


# Function to load and prepare the image in right shape
def read_image(filename):
    x = load_img(filename, target_size=(250, 250))

    return x


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):  # Checking file format
            filename = file.filename
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            img = read_image(file_path)  # pre-processing method
            # Convert the image to a numpy array
            img_array = img_to_array(img)

            # Expand the dimensions of the array to fit the model's input shape
            img_array = img_array.reshape((1,) + img_array.shape)


            # Make a prediction on the image
            prediction = model.predict(img_array)

            predicted_label = np.argmax(prediction)

            class_names = {1:"Potato___Early_blight",
                           0:"Potato___healthy",
                           2:"Potato___Late_blight",
                           3:"Rice__BrownSpot",
                           4:"Rice__Healthy",
                           5:"Rice__Hispa",
                           6:"Rice__LeafBlast"}
            predicted_class = class_names[predicted_label]
            des = {
                "Potato___Early_blight": "1.Disease free seed tubers should be used for planting.<br>2.Removal and destruction of infected plant debris should be done because the spores lying in the soil are the primary source of infection.\n3.Very early spraying with Zineb or captan 0.2% and repeating it for every 15 – 20 days gives effective control.\n4.The variety Kufri Sindhuri possesses a fair degree of resistance.",
                "Potato___healthy": "Healthy Potato",
                "Potato___Late_blight": "1.Protective spraying with mancozeb or zineb 0.2 % should be done to prevent infection of tubers.\n2.Tuber contamination is minimized if injuries are avoided at harvest time and storing of visibly infected tubers before storage.\n3.The resistant varities recommended for cultivation are Kufri Naveen, Kufri Jeevan, Kufri Alenkar, Kufri Khasi Garo and Kufri Moti.\n4.Destruction of the foliage few days before harvest is beneficial and this is accomplished by spraying with suitable herbicide.",
                "Rice__BrownSpot": "1.Seed soak / seed treatment with Captan or Thiram at 2.0g /kg of seed.\n2.Spray Mancozeb (2.0g/lit) or Edifenphos (1ml/lit) - 2 to 3 times at 10 - 15 day intervals.\n3.Spray preferably during early hours or afternoon at flowering and post-flowering stages.\n4.Seed treatment with Agrosan or Ceresan 2.5 g/kg seed to ward off seedling blight stage;\n5.Spraying copper fungicides to control secondary spread;\n6.Grisepfulvin, nystatin, aureofungin, and similar antibiotics have been found effective in preventing primary seedling infection.\n7.Seed treatment with captan, thiram, chitosan, carbendazim, or mancozeb has been found to reduce seedling infection.\n8.Seed treatment with tricyclazole followed by spraying of mancozeb + tricyclazole at tillering and late booting stages gave good control of the disease.\n9.Application of edifenphos, chitosan, iprodione, or carbendazim in the field is also advisable.",
                "Rice__Healthy": "Healthy Rice",
                "Rice__Hispa": "1.Avoid over fertilizing the field.\n2.Close plant spacing results in greater leaf densities that can tolerate higher hispa numbers.\n3.Leaf tip containing blotch mines should be destroyed.\n4.Manual collection and killing of beetles – hand nets.\n5.To prevent egg laying of the pests, the shoot tips can be cut.\n6.Clipping and burying shoots in the mud can reduce grub populations by 75 - 92%.\n7.Reduviid bug eats upon the adults.\n8.Spraying of methyl parathion 0.05% or Quinalphos 0.05%.",
                "Rice__LeafBlast": "1.Do not apply lower/higher doses of fungicides.\n2.Spray before 11.00 AM/after 3.00 PM.\n3.Avoid noon hours for spraying.\n4.Seed treatment at 2.0 g/kg seed with Captan or Carbendazim or Thiram or Tricyclazole.\n5.Systemic fungicides such as pyroquilon and tricyclazole are possiblechemicals for controlling the disease.\n7.Spraying of Tricyclazole at 1g/lit of water or Edifenphos at 1 ml/lit of water or Carbendazim at 1.0 gm/lit.\n8.3 to 4 sprays each at nursery, tillering stage and panicle emergence stage may be required for complete control.\n9.Nursery stage: Light infection - Spray Carbendazim or Edifenphos @ 1.0 gm/lit.\n10.Pre-Tillering to Mid-Tillering: Light at 2 to 5 % disease severities - Apply Edifenphos or Carbendazim @ 1.0 gm/lit. Delay top dressing of N fertilizers when infection is seen.\n11.Panicle initiation to booting: At 2 to 5% leaf area damage- spray Edifenphos or Carbendazim or Tricyclazole @ 1.0 gm/lit.\n1.Flowering and after: At 5 % leaf area damage or 1 to 2 % neck infection spray Edifenphos or Carbendazim or Tricyclazole @1g/lit of water."
                    }
            solution = des[predicted_class]


            return render_template('predict.html',predicted_class= predicted_class,solution=solution, user_image=file_path)
        else:
            return "Unable to read the file. Please check file extension"





@app.route('/predict1', methods=['GET', 'POST'])
def predict1():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):  # Checking file format
            filename = file.filename
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            img = read_image(file_path)  # pre-processing method
            # Convert the image to a numpy array
            img_array = img_to_array(img)

            # Expand the dimensions of the array to fit the model's input shape
            img_array = img_array.reshape((1,) + img_array.shape)


            # Make a prediction on the image
            prediction = model1.predict(img_array)

            predicted_label = np.argmax(prediction)

            class_names = {
                0:'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                1:'Corn_(maize)___Common_rust_',
                2:'Corn_(maize)___Northern_Leaf_Blight',
                3:'Corn_(maize)___healthy',
                4:'Tomato___Late_blight',
                5:'Tomato___Septoria_leaf_spot',
                6:'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                7:'Tomato___Tomato_mosaic_virus',
                8:'Tomato___healthy'
                            }
            predicted_class = class_names[predicted_label]

            des = {
                "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "1.Rogue out affected plants. 2.Use resistant TNAU maize hybrid COH-6. 3.Soil application of P. fluorescens (or) T. viride @ 2.5 kg / ha + 50 kg of well decomposed FYM (mix 10 days before application) or sand at 30 days after sowing. 4.Spray Metalaxyl @ 1000g(or) Mancozeb 2g/lit at 20 days after sowing.",
                "Corn_(maize)___Common_rust": "1.Destroy altrenate plant host. 2.Soil application of P. fluorescens (or) T. viride @ 2.5 kg / ha + 50 kg of well decomposed FYM (mix 10 days before application) or sand at 30 days after sowing. 3.Spray Mancozeb 1.25 kg/ha",
                "Corn_(maize)___Northern_Leaf_Blight": "1.Rogue out affected plants. 2.Resistant cultivers – Deccan, VL 42, Prabhat, KH-5901, PRO-324, PRO-339, ICI-701, F- 7013, F-7012, PEMH 1, PEMH 2, PEMH 3, Paras, Sartaj, Deccan 109, COH-6. 3.Soil application of P. fluorescens (or) T. viride @ 2.5 kg / ha + 50 kg of well decomposed FYM (mix 10 days before application) or sand at 30 days after sowing 4.Spray Matalaxyl 1000 g / Mancozeb 2 g/liter at 10 days interval after first appearance of the disease.",
                "Corn_(maize)___healthy": "Healty Corn PLant",
                "Tomato___Late_blight": "Apply any one of the follwoing fungicide: 1.Azoxystrobin 23% SC - 500ml / ha . 2.Cyazofamid 34.5% SC - 200ml / ha. 3.Mancozeb 35% SC - 2.5l / ha. 4.Zineb 75% WP - 1Kg / ha. 5.Azoxystrobin 18.2% + Difenoconazole 11.4% w/w SC - 500ml / ha.",
                "Tomato___Septoria_leaf_spot": "Fluxapyroxad 250 g/l + Pyraclostrobin 250 g/l SC - 200-250 ml/ha.",
                "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Apply any one of the follwoing insecticide: 1.Dimethoate 30 EC @ 1 ml /l. 2.Malathion 50 EC @ 1.5 ml / l. 3. Methyl demeton 25 EC @ 1.0 ml/l. 4.Thiamethoxam 25 WG @ 4 ml/10 l. 5.Cyantraniliprole 10.26 OD @ 1.8 ml/l. 6.Imidacloprid 17.8 SL @ 3 ml/10l. 7.Spiromesifen 22.9 SC @ 1.25 ml/l to control white fly vector.",
                "Tomato___Tomato_mosaic_virus": '1.Trichoderma asperellum @ 4g/kg seeds. 2.Seedling dip in Bacillus subtilis @ 5g/l and soil application of Bacillus subtilis @ 2.5 kg with 125 kg of FYM / ha at 30 days of transplanting.',
                "Tomato___healthy" : "Healthy Tomato"
            }
            solution = des[predicted_class]

            return render_template('predict1.html',predicted_class= predicted_class,solution=solution, user_image=file_path)
        else:
            return "Unable to read the file. Please check file extension"



@app.route('/predict2', methods=['GET', 'POST'])
def predict2():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):  # Checking file format
            filename = file.filename
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            img = read_image(file_path)  # pre-processing method
            # Convert the image to a numpy array
            img_array = img_to_array(img)

            # Expand the dimensions of the array to fit the model's input shape
            img_array = img_array.reshape((1,) + img_array.shape)


            # Make a prediction on the image
            prediction = model2.predict(img_array)

            predicted_label = np.argmax(prediction)

            class_names = {0: "Jackfruit___Bacterial_spot",
                           1: "Jackfruit___healthy",
                           2: "Strawberry Healthy",
                           3: "Strawberry Leaf scorch"
                           }
            predicted_class = class_names[predicted_label]


            des = {
                "Jackfruit___Bacterial_spot" :"The disease is effectively controlled by spraying Carbendazim (0.1%) or Thiophanate methyl (0.2%) or Difolatan (0.2%).",
                "Jackfruit___healthy" : "Healthy Jack Fruit",
                "Strawberry Healthy": "Healthy Strawberry",
                "Strawberry Leaf scorch" : "1.Begin with clean plant material. 2.Use proper sanitation. 3.Remove infected leaves and debris. 4.Increase air circulation to encourage leaf drying. 5.Consider resistant cultivars. 6.Use fungicides if disease becomes severe."
                 }


            solution = des[predicted_class]


            return render_template('predict2.html',predicted_class= predicted_class,solution=solution, user_image=file_path)
        else:
            return "Unable to read the file. Please check file extension"




from flask import Flask, render_template, request, redirect, url_for


# Create a table to store images
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id SERIAL PRIMARY KEY,
        filename TEXT NOT NULL,
        data BYTEA NOT NULL,
        uploaded_at TIMESTAMP DEFAULT NOW()
    )
''')
conn.commit()

# Create a table to store comments
cur.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50),
        comment TEXT,
        image_id INTEGER REFERENCES images(id)
    );
""")
conn.commit()

# Route for the homepage
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Handle image uploads
    if request.method == 'POST' and 'file' in request.files:
        # Get the uploaded file data and filename
        file = request.files['file']
        filename = file.filename

        # Read the file data and insert it into the database
        data = file.read()
        cur = conn.cursor()
        cur.execute('INSERT INTO images (filename, data) VALUES (%s, %s)', (filename, psycopg2.Binary(data)))
        conn.commit()

        # Redirect to the homepage
        return redirect(url_for('index'))

    # Handle comments
    if request.method == 'POST' and 'name' in request.form and 'comment' in request.form and 'image_id' in request.form:
        # Insert new comment into the database
        name = request.form['name']
        comment = request.form['comment']
        image_id = request.form['image_id']
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO comments (name, comment, image_id) 
            VALUES (%s, %s, %s)
        """, (name, comment, image_id))
        conn.commit()

    # Fetch all images from the database
    cur = conn.cursor()
    cur.execute('SELECT id, filename, data FROM images ORDER BY uploaded_at DESC')
    rows_images = cur.fetchall()

    # Fetch all comments from the database
    cur.execute("SELECT * FROM comments")
    rows_comments = cur.fetchall()

    # Encode the image data in base64 format for display in HTML
    images = []
    for row in rows_images:
        image = {
            'id': row[0],
            'filename': row[1],
            'data': base64.b64encode(row[2]).decode('utf-8')
        }

        # Fetch the comments for the image
        cur.execute("""
            SELECT name, comment
            FROM comments
            WHERE image_id = %s
        """, (row[0],))
        comments = cur.fetchall()
        image['comments'] = comments

        images.append(image)

    return render_template('index.html', images=images)



@app.route('/farmersite', methods= ['POST','GET'])
def farmersite():
    # Handle image uploads
    if request.method == 'POST' and 'file' in request.files:
        # Get the uploaded file data and filename
        file = request.files['file']
        filename = file.filename

        # Read the file data and insert it into the database
        data = file.read()
        cur = conn.cursor()
        cur.execute('INSERT INTO images (filename, data) VALUES (%s, %s)', (filename, psycopg2.Binary(data)))
        conn.commit()

        # Redirect to the homepage
        return redirect(url_for('farmersite'))

    # Handle comments
    if request.method == 'POST' and 'name' in request.form and 'comment' in request.form and 'image_id' in request.form:
        # Insert new comment into the database
        name = request.form['name']
        comment = request.form['comment']
        image_id = request.form['image_id']
        cur = conn.cursor()
        cur.execute("""
                INSERT INTO comments (name, comment, image_id) 
                VALUES (%s, %s, %s)
            """, (name, comment, image_id))
        conn.commit()

    # Fetch all images from the database
    cur = conn.cursor()
    cur.execute('SELECT id, filename, data FROM images ORDER BY uploaded_at DESC')
    rows_images = cur.fetchall()

    # Fetch all comments from the database
    cur.execute("SELECT * FROM comments")
    rows_comments = cur.fetchall()

    # Encode the image data in base64 format for display in HTML
    images = []
    for row in rows_images:
        image = {
            'id': row[0],
            'filename': row[1],
            'data': base64.b64encode(row[2]).decode('utf-8')
        }

        # Fetch the comments for the image
        cur.execute("""
                SELECT name, comment
                FROM comments
                WHERE image_id = %s
            """, (row[0],))
        comments = cur.fetchall()
        image['comments'] = comments

        images.append(image)

    return render_template('farmersite.html', images=images)





if __name__ == "__main__":
    app.run(debug=True)
