from flask import Flask, render_template, request, redirect
from flask_pymongo import MongoClient
from bson.objectid import ObjectId
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2


app = Flask(__name__)
# Update with your MongoDB connection URI
client = MongoClient(
    'mongodb+srv://dhalavai:dhalavai2003@cluster0.yoiv9rm.mongodb.net/?retryWrites=true&w=majority')
db = client['events_db']
events_collection = db['events']
approved_collection = db['approved']
# for the email


def send_email(to_address):
    # Email constants
    sender_email = 'dhalavain@gmail.com'
    sender_password = 'rahbnxguldjmgwpl'
    subject = 'Regarding OD Request'
    body = 'Your OD Request Failed Please make it offline'

    try:
        # Create email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to_address
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, to_address, message.as_string())
        print('Email sent successfully!')
        server.quit()

    except Exception as e:
        print('Error sending email:', str(e))


def send_email1(to_address, output_file_name):
    # Email constants
    sender_email = 'dhalavain@gmail.com'
    sender_password = 'rahbnxguldjmgwpl'
    subject = 'Regarding OD Request'
    body = 'Your OD Request is Processed successfully Please make sure to download the image'

    try:
        # Create email message

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to_address
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        with open("output_image.jpg", 'rb') as f:
            image_data = f.read()
            image_mime = MIMEImage(image_data)
            message.attach(image_mime)
        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, to_address, message.as_string())
        print('Email sent successfully!')
        server.quit()

    except Exception as e:
        print('Error sending email:', str(e))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        to_address = request.form.get('email')
        college_name = request.form['college_name']
        date = request.form['date']
        event_name = request.form['event_name']
        poster = request.files['poster']
        poster.save('static/' + poster.filename)
        poster_url = 'static/' + poster.filename

        event_data = {
            'name': name,
            'roll_number': roll_number,
            'to_address': to_address,
            'college_name': college_name,
            'date': date,
            'event_name': event_name,
            'poster_url': poster_url,
            'is_approved': 'null'  # Add a new field to track approval status
        }

        # Insert event data into MongoDB
        events_collection.insert_one(event_data)
        return render_template('thanks.html')

    return render_template('form.html')


admin_username = "admin"
admin_password = "password"


@app.route('/login', methods=['GET', 'POST'])
def login():
    events = events_collection.find()
    if request.method == 'POST':
        username = request.form['admin_username']
        password = request.form['admin_password']

        if username == admin_username and password == admin_password:
            # Redirect to admin.html if credentials are correct
            return render_template('admin.html', events=events)
        else:
            error_message = "Wrong credentials. Please try again."
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')


@app.route('/adminlogin')
def adminlogin():
    return render_template('login.html')  # Redirect to login.html


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        event_id = request.form['event_id']
        is_approved = request.form['is_approved']

        # Update approval status in MongoDB
        events_collection.update_one(
            {'_id': event_id}, {'$set': {'is_approved': is_approved}})

        # If event is approved, move it to approved collection and delete from events collection
        if is_approved == 'true':
            event = events_collection.find_one({'_id': event_id})
            approved_collection.insert_one(event)
            events_collection.delete_one({'_id': event_id})

    events = events_collection.find()
    return render_template('admin.html', events=events)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/admin/update_approval', methods=['POST'])
def update_approval():
    event_id = request.form['event_id']
    is_approved = request.form['is_approved']

    # Get the event from the events collection
    event = events_collection.find_one({'_id': ObjectId(event_id)})

    # Update the approval status
    event['is_approved'] = is_approved

    # Insert the updated event into the approved collection
    approved_collection.insert_one(dict(event))

    # Delete the event from the events collection
    events_collection.delete_one({'_id': ObjectId(event_id)})
    if is_approved == 'true':
        name = event['name']
        event_name = event['event_name']
        roll_number = event['roll_number']
        date = event['date']
        college_name = event['college_name']
        to_address = event['to_address']
        # Load the image
        # Replace 'image.jpg' with the path to your image
        image = cv2.imread('image.jpg')

# Get the dimensions of the image
        height, width, _ = image.shape

# Define the texts and their corresponding positions
        namep = name
        rollnop = str(roll_number)
        eventnamep = event_name
        datep = str(date)
        collegenamep = college_name
        texts = [namep, rollnop, eventnamep, datep, collegenamep, namep]
        positions = [(200, 280), (200, 330), (527, 1200),
                     (1259, 1200), (254, 1281), (200, 1610)]

# Define the font properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2

# Loop through each text and position
        for i in range(len(texts)):
            text = texts[i]
            x, y = positions[i]

    # Calculate the position of the text box
            text_size = cv2.getTextSize(
                text, font, font_scale, font_thickness)[0]
            text_width = text_size[0]
            text_height = text_size[1]
            x_start = x
            y_start = y
            x_end = x + text_width
            y_end = y + text_height

    # Check if the text box is within the image boundaries
            if x_start >= 0 and y_start >= 0 and x_end <= width and y_end <= height:
                # Draw a filled rectangle with white color as the background for the text
                cv2.rectangle(image, (x_start, y_start),
                              (x_end, y_end), (255, 255, 255), -1)

        # Add the text to the image with black color
                cv2.putText(image, text, (x, y + text_height), font,
                            font_scale, (0, 0, 0), font_thickness)

        # Save the image with the added text to output with a unique file name
        output_file_name = f"output_image.jpg"
        cv2.imwrite(output_file_name, image)
        send_email1(to_address, output_file_name)

        print(f"Image with text {text} saved as {output_file_name}")
    if is_approved == 'false':
        # Replace with the actual email address
        to_address = event['to_address']
        send_email(to_address)
    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)
