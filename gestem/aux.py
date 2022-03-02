import uuid
from datetime import datetime
import smtplib
# import email.message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import unicodedata


def normalizar(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError:
        pass

    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore')\
        .decode("utf-8")

    return str(text)


def keygen(cod='CTS963-'):
    """
    Esta función genera un codigo del siguiente formato:
        CTS963-: codigo identificado grupo investigación +
        NN: 2 dígitos correspondientes al año +
        XXXXXX: 6 caracteres alfanumericos aleatorios únicos.
    Se puede modificar el codigo identificativo añadiendolo como parámetro a la
    función.
    """

    fecha = datetime.now()
    año = fecha.strftime("%y")
    key = str(uuid.uuid4())
    return cod + año + (key[-6:]).upper()


def mailer(tablacsv="users.csv", credenciales="credenciales.txt"):
    """
    params:
        tablacsv -> ruta a un archivo .csv con el siguiente formato:
            nombre,apellidos,email
            Juana,de Arco Rodriguez,juanadearco@revolucion.com
            [etc]
        credenciales -> ruta a un archivo .txt con el siguiente formato:
            servidor_smtp  -- Línea 1
            puerto         -- Línea 2
            usuario        -- Línea 3
            password       -- Línea 4

    Esta tabla se iterará y para cada fila de la misma, se creará un usuario
    en la base de datos con un password. Los datos de acceso serán enviados por
    e-mail al correo del usuario creado.
    """
    from django.contrib.auth.models import User
    import csv

    with open(credenciales) as c:
        textofeo = c.read()
        texto = textofeo.splitlines()

    server = texto[0]
    puerto = texto[1]
    usuario = texto[2]
    contraseña = texto[3]

    with open(tablacsv) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            nombre = row['nombre']
            apellidos = row['apellidos']
            direccion = row['email']
            nickname = nombre.replace(" ", "")
            if apellidos:
                for x in apellidos.split():
                    nickname = f'{nickname}{x[0]}'

            nickname = normalizar(nickname.lower())

            password = User.objects.make_random_password()

            user = User.objects.create_user(
                nickname,
                direccion,
                password
            )
            user.first_name = nombre
            user.last_name = apellidos
            user.save()

            email_html = """
                <!DOCTYPE html>
                <html lang="es" dir="ltr">
                  <head>
                    <meta charset="utf-8">
                    <style>
                      header {background-color: #CB2C30; height: 8vh;
                      text-align:center;
                      display: flex; justify-content: center;
                      align-items: center;color: white;
                      font-size: 3vh;font-family: Arial, serif}
                      .container {padding: 10px 40px 10px 40px;}
                      .password {background-color: #999999;text-align:center;
                      width: 50vw;}
                    </style>
                  </head>
                  <body>
                    <header>
                      REGISTRO EN PEDIDOS TERSTEM 2.0
                    </header>
                    <div class="container">
                      <p>
                        Hola $(nombre), en los próximos días estará disponible
                        una nueva versión de la aplicación web para anotar
                        pedidos del laboratorio. Podrás acceder a ella a través
                        del enlace de siempre:
                        <a href="https://terstem.ugr.es">terstem.ugr.es</a>
                      </p>
                      <p>
                        Usa los datos que se encuentran a continuación para
                        acceder. Recuerda que puedes cambiar la contraseña
                        siempre que quieras en tu tablón.
                      </p>
                      <div class="password">
                        <p>
                          <strong>Usuario: </strong>$(usuario)<br>
                          <strong>Contraseña: </strong>$(contraseña)
                        </p>
                      </div>
                    </div>
                  </body>
                </html>
            """

            email_html = email_html.replace('$(nombre)', nombre)
            email_html = email_html.replace('$(usuario)', nickname)
            email_html = email_html.replace('$(contraseña)', password)

            email_text = f"""
                Hola {nombre}, has sido registrado en la nueva aplicación de
                pedidos con éxito.\n
                Tus datos de acceso son:\n
                usuario: f{nickname}\n
                pass: f{password}
            """

            # me == my email address
            # you == recipient's email address
            me = "pedidosterstem@ugr.es"
            you = direccion

            # Create message container - the correct MIME type is
            # multipart/alternative.
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "DATOS ACCESO WEB PEDIDOS TERSTEM"
            msg['From'] = me
            msg['To'] = direccion

            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(email_text, 'plain')
            part2 = MIMEText(email_html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in
            # this case the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)
            # Send the message via local SMTP server.
            mail = smtplib.SMTP(server, puerto)

            mail.ehlo()

            mail.starttls()

            mail.login(usuario, contraseña)
            mail.sendmail(me, you, msg.as_string())
            mail.quit()
