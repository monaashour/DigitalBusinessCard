import os
import base64
import json
import pathlib
from urllib.parse import unquote

import dotenv
import qrcode
import vobject
import pandas as pd
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from applepassgenerator.client import ApplePassGeneratorClient
from applepassgenerator.models import Generic, Barcode, BarcodeFormat
from django.contrib.auth.models import User
from pathlib import Path

from cards.models import Card    

dotenv.load_dotenv()

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)

CURRENT_WORKING_DIR = Path(__file__).resolve().parent
HOST_URL = os.getenv('HOST_URL')

def generate_vcard(user, directory):
    v = vobject.vCard()

    v.add('ORG').value = ['Orange Business']
    v.add('n').value = vobject.vcard.Name(family=user.last_name, given=user.first_name)
    v.add('fn').value = f'{user.first_name} {user.last_name.upper()}'

    email = v.add('email')
    email.type_param = 'WORK'
    email.value = user.email

    if user.card.phone:
        phone = v.add('tel')
        phone.type_param = 'WORK'
        phone.value = user.card.phone

    obcom = v.add('url')
    obcom.type_param = 'WORK'
    obcom.value = 'https://www.orange-business.com'

    if user.card.linkedin:
        lnkin = v.add('url')
        lnkin.type_param = 'LINKEDIN'
        lnkin.value = user.card.linkedin

    if user.card.photo_b64:
        img = v.add('PHOTO')
        img.type_param = 'jpg'
        img.params['ENCODING'] = ['BASE64']
        img.value = user.card.photo_b64

    with open(os.path.join(directory, f'{user.username}.vcf'), 'w') as f:
        f.write(v.serialize())


def generate_apple_pass(user, url, directory):
    ORANGE_LOGO_FILE = CURRENT_WORKING_DIR / 'orange_logo.png'
    CERTS_DIR = os.getenv('CERTS_DIR')
    
    card_info = Generic()
    card_info.add_primary_field('name', f'{user.first_name} {user.last_name}', '')
    card_info.add_secondary_field('title', f'{json.loads(user.card.job_title)[0]}', 'Title')
    if user.card.phone:
        card_info.add_secondary_field('phone', f'{user.card.phone}', 'Phone')
    card_info.add_auxiliary_field('email', f'{user.email}', 'Email')
    if user.card.linkedin:
        card_info.add_auxiliary_field('linkedin', f'{unquote(user.card.linkedin.split("com/in/")[1].split("/")[0])}', 'LinkedIn')

    team_identifier = os.getenv('TEAM_ID')
    pass_type_identifier = os.getenv('PASS_TYPE_ID')
    organization_name = "Orange Business"

    applepassgenerator_client = ApplePassGeneratorClient(team_identifier, pass_type_identifier, organization_name)
    apple_pass = applepassgenerator_client.get_pass(card_info)

    apple_pass.logo_text = 'Business'
    apple_pass.barcode = Barcode(url, BarcodeFormat.QR, 'www.orange-business.com')

    apple_pass.add_file("logo.png", open(ORANGE_LOGO_FILE, "rb"))
    apple_pass.add_file("icon.png", open(ORANGE_LOGO_FILE, "rb"))

    CERTIFICATE_PATH = CERTS_DIR + "/pass.pem"
    PASSWORD_KEY = CERTS_DIR + "/private.key"
    WWDR_CERTIFICATE_PATH = CERTS_DIR + "/AppleWWDRCAG3.pem"
    CERTIFICATE_PASSWORD = os.getenv('CERT_PASS')
    OUTPUT_PASS_NAME = os.path.join(directory, f"{user.username}.pkpass")

    apple_pass.create(CERTIFICATE_PATH, PASSWORD_KEY, WWDR_CERTIFICATE_PATH, CERTIFICATE_PASSWORD, OUTPUT_PASS_NAME)


def generate_qrcode(username, url, directory):
    LOGO_IMAGE_FILE = CURRENT_WORKING_DIR / 'orange_logo.png'
    filename = os.path.join(directory, username + '.jpg')

    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(), embeded_image_path=LOGO_IMAGE_FILE)
    img.save(filename)


def encode_image(username):
    filename = IMAGES_DIR / f"{username}.jpg"
    if not filename.is_file():
        return None
    with open(filename , 'rb') as f:
        r = base64.b64encode(f.read()).decode('ascii')
    return r


ATTENDEES_FILE = CURRENT_WORKING_DIR.parent / 'GSLT - BusinessCardsData - 12 Sep 2024.xlsx'
IMAGES_DIR = CURRENT_WORKING_DIR.parent.parent / 'images'
REGION = 'APAC'


df = pd.read_excel(ATTENDEES_FILE, dtype=str)

print('read attendees') 
print(df.shape)

sales = []

for i, user in df.iterrows():
    details = {
        'first_name': user.iloc[0],
        'last_name': user.iloc[1],
        'email': user.iloc[3].lower(),
        'phone': '+' + str(user.iloc[4]).strip().strip("'").strip('+'),
        'linkedin': (user.iloc[5] if 'linkedin.com' in str(user.iloc[5]) else None),
        'job_title': [
            user.iloc[2],
        ],
    }
    sales.append(details)

print('fetched users to dict')

for employee in sales:
    employee['username'] = employee['email'].split('@')[0]
    employee['job_title']

    if (IMAGES_DIR / f"{employee['username']}.jpg").is_file():
        employee['image'] = IMAGES_DIR + employee['username'] + '.jpg'
    else:
        employee['image'] = None
    
print('added extra details to dict')

for employee in sales:
    is_user = User.objects.filter(username=employee['username'])
    is_card = Card.objects.filter(owner__username=employee['username'])

    if is_user and is_card:
        print(f'!! user {employee["username"]} and card already exist. SKIPPING\n------------')
        continue

    if not is_user:
        user = User.objects.create_user(
            username=employee['username'],
            email=employee['email'],
            first_name=employee['first_name'],
            last_name=employee['last_name']
        )
        user.save()
        print(f'added {user.username} to db')
    else:
        user = User.objects.get(username=employee['username'])

    if not is_card:
        card = Card.objects.create(
            owner=user,
            linkedin=employee['linkedin'],
            phone=employee['phone'],
            job_title=json.dumps(employee['job_title']),
            photo_b64=encode_image(user.username),
            region=REGION
        )
        card.save()
        print(f'added card {card.owner.username} to db')

        url = f'{HOST_URL}/cards/' + user.username

        media_dir = CURRENT_WORKING_DIR.parent / 'media'
        generate_qrcode(user.username, url, os.path.join(media_dir, 'qrcode'))
        print('generated qrcode')
        generate_vcard(user, os.path.join(media_dir, 'contacts'))
        print('generated vcard')
        # generate_apple_pass(user, url, os.path.join(media_dir, 'pass'))
        # print('generated pkpass')
        print(f'{user.username} ADDED\n------------')
