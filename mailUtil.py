# coding=UTF-8
import smtplib
import chrono
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mailNewMasterRealease(target,me="notification@hids.com"):

	targetNumber = len(target)
	now = chrono.getTime()

	for i in range(targetNumber):
		you = target[i]
		# Create message container - the correct MIME type is multipart/alternative.
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Link"
		msg['From'] = me
		msg['To'] = you

		# Create the body of the message (a plain-text and an HTML version).
		text = "Bonjour !\nUne nouvelle version de référence a été crée à "+now+".\nElle sera utilisée pour les vérifications ultérieures. !\n"
		html = """\
		<html>
		  <head></head>
		  <body>
		    <p>Bonjour !<br>
		       Une nouvelle version de référence a été crée à """+now+""".<br>
		       Elle sera utilisée pour les vérifications ultérieures.
		    </p>
		  </body>
		</html>
		"""

		# Record the MIME types of both parts - text/plain and text/html.
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')

		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)
		msg.attach(part2)

		# Send the message via local SMTP server.
		s = smtplib.SMTP('localhost')
		# sendmail function takes 3 arguments: sender's address, recipient's address
		# and message to send - here it is sent as one string.
		s.sendmail(me, you, msg.as_string())
		s.quit()

def mailScanFailed(target,me="notification@hids.com"):
	# me == my email address
	# you == recipient's email address

	targetNumber = len(target)

	for i in range(targetNumber):
		you = target[i]
		# Create message container - the correct MIME type is multipart/alternative.
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Link"
		msg['From'] = me
		msg['To'] = you

		# Create the body of the message (a plain-text and an HTML version).
		text = "Bonjour !\nLe robot de sécurité a détécté une faille dans le système !\nDes fichiers ont été alterés !\n"
		html = """\
		<html>
		  <head></head>
		  <body>
		    <p>Bonjour !<br>
		       Le robot de sécurité a détécté une faille dans le système !<br>
		       Des fichiers ont été alterés !
		    </p>
		  </body>
		</html>
		"""

		# Record the MIME types of both parts - text/plain and text/html.
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')

		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)
		msg.attach(part2)

		# Send the message via local SMTP server.
		s = smtplib.SMTP('localhost')
		# sendmail function takes 3 arguments: sender's address, recipient's address
		# and message to send - here it is sent as one string.
		s.sendmail(me, you, msg.as_string())
		s.quit()
def mailDeepScan(target,corruptedFiles,me="notification@hids.com"):
	# me == my email address
	# you == recipient's email address

	targetNumber = len(target)

	for i in range(targetNumber):
		you = target[i]
		# Create message container - the correct MIME type is multipart/alternative.
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Link"
		msg['From'] = me
		msg['To'] = you
		dataText = []
		for i in range(len(corruptedFiles)):
			temp = corruptedFiles[i]+"<br>"
			dataText.append(temp)

		# Create the body of the message (a plain-text and an HTML version).
		text = "Bonjour !\nVoici le détail des fichiers altérés dans le système !\n"
		html = str("""\
		<html>
		  <head></head>
		  <body>
		    <p>Bonjour !<br>
		       Voici le détail des fichiers altérés dans le système ! !<br>
		       Des fichiers ont été alterés ! :<br>"""+str(dataText)+""""
		    </p>
		  </body>
		</html>
		""")

		# Record the MIME types of both parts - text/plain and text/html.
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')

		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)
		msg.attach(part2)

		# Send the message via local SMTP server.
		s = smtplib.SMTP('localhost')
		# sendmail function takes 3 arguments: sender's address, recipient's address
		# and message to send - here it is sent as one string.
		s.sendmail(me, you, msg.as_string())
		s.quit()