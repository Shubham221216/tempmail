from flask import Flask, render_template, redirect, url_for, session, jsonify
from mailtm import Email
import threading
import os
app = Flask(__name__)
app.secret_key = 'tempmail1234'  # Replace with a secure secret key

email_instance = None
inbox_emails = []  # Store emails here

def start_email_listener(email_obj):
    def listener(message):
        print("\nNew Email Received!")
        print("Subject:", message['subject'])
        print("Content:", message['text'] if message['text'] else message['html'])

        # Save incoming emails, prefer HTML content if available
        content = message['html'] if message['html'] else message['text']
        inbox_emails.append({
            'subject': message['subject'],
            'content': content
        })
    email_obj.start(listener)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    global email_instance, inbox_emails
    email_instance = Email()
    email_instance.register()
    session['email_address'] = email_instance.address
    inbox_emails = []  # Reset inbox on new email creation

    # Start listener in a separate thread
    thread = threading.Thread(target=start_email_listener, args=(email_instance,))
    thread.daemon = True
    thread.start()

    return redirect(url_for('inbox'))

@app.route('/inbox')
def inbox():
    email_address = session.get('email_address')
    if not email_address:
        return redirect(url_for('index'))
    return render_template('inbox.html', email=email_address)

@app.route('/get_emails')
def get_emails():
    return jsonify(inbox_emails)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

