
from flask import Flask, render_template, request
from fbchat import log, Client, Message
from os.path import join, dirname
from ibm_watson import AssistantV2, LanguageTranslatorV3, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pymysql
from easyAI import TwoPlayersGame, Human_Player, AI_Player, Negamax
import numpy as np
class TresEnRaya(TwoPlayersGame):
    def __init__(self, nplayers):
        self.tablero = np.zeros((3, 3), dtype=int)
        self.nplayer = 1
        self.mapa = {}
        cont = 1
        for i in range(len(self.tablero)):
            for j in range(len(self.tablero)):
                self.mapa[cont] = (i, j)
                cont += 1

        # print(self.mapa)
        self.players = nplayers

    def possible_moves(self):
        moves = []
        cont = 1
        for i in range(len(self.tablero)):
            for j in range(len(self.tablero)):
                if self.tablero[i][j] == 0:
                    moves.append(cont)
                cont += 1

        # print(moves)
        return moves

    def make_move(self, casillero):
        pos = self.mapa[casillero]
        self.tablero[pos[0]][pos[1]] = self.nplayer

    def unmake_move(self, casillero):
        pos = self.mapa[casillero]
        self.tablero[pos[0]][pos[1]] = 0

    def lose(self):
        for i in range(len(self.tablero)):
            if np.all(self.tablero[i, :] == self.nopponent, axis=0) or np.all(self.tablero[:, i] == self.nopponent,
                                                                              axis=0):
                return True
        if self.tablero[0][0] == self.nopponent and self.tablero[1][1] == self.nopponent and self.tablero[2][
            2] == self.nopponent:
            return True
        if self.tablero[2][0] == self.nopponent and self.tablero[1][1] == self.nopponent and self.tablero[0][
            2] == self.nopponent:
            return True
        return False

    def show(self):
        print(self.tablero)

    def scoring(self):
        return -100 if self.lose() else 0

    def is_over(self):
        return (self.possible_moves() == [] or self.lose())

con = pymysql.connect( host="localhost", user="root", passwd="", db="preguntas")
cursor = con.cursor(pymysql.cursors.DictCursor)

correo = "ups_uclqlhf_chatt@tfbnw.net"
contra = "***123456789"

authenticator = IAMAuthenticator('U4IKxuhQ4XBIrskFYSLLqrB29b_A2fch9uL4gWQUZ-f4')
assistant = AssistantV2(
    version='2018-09-20',
    authenticator=authenticator)
assistant.set_service_url('https://api.us-south.assistant.watson.cloud.ibm.com/instances/20d0e70b-3f11-4c02-9137-205d38b948a9')
assistant.set_disable_ssl_verification(False)
session = assistant.create_session("633359aa-4a7e-4cfa-8ebe-78113a86ad21").get_result()

authenticatorT = IAMAuthenticator('0Iobj63HD2qz6ChKXOCkc1kARMJ8E9-Gkq1045FQIGf7')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticatorT)
language_translator.set_service_url('https://gateway.watsonplatform.net/language-translator/api')

authenticatorV = IAMAuthenticator('rQkJz0iTpTyboZqk6SymQ2hh6zfG7sfmxdZBD9V9qQIV')
service = TextToSpeechV1(authenticator=authenticatorV)
service.set_service_url('https://stream.watsonplatform.net/text-to-speech/api')

def guardarPregunta(con, pregunta, respuesta, traducion):
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("INSERT INTO preguntas(id, pregunta, respuesta, traducion) VALUES (0,%s,%s,%s)",
                   (pregunta, respuesta, traducion))
    cursor.fetchall()
    con.commit()

def buscarRespuesta(con, pregunta):
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT p.respuesta FROM preguntas p WHERE p.pregunta = %s",(pregunta))
    res = cursor.fetchall()
    ress = res[0]
    con.commit()
    return (ress['respuesta'])


def mensaje(text, session):
    message = assistant.message("633359aa-4a7e-4cfa-8ebe-78113a86ad21",
        session["session_id"],
        input={'message_type': 'text','text': text}).get_result()
    return (message['output']['generic'][0]['text'])

def traducir(text,language_translator):
    translation = language_translator.translate(
        text=text, model_id='en-es').get_result()
    return translation['translations'][0]['translation']

def voz(text, service):
    with open(join(dirname(__file__), 'output.mp3'),
              'wb') as audio_file:
        response = service.synthesize(
            text, accept='audio/mp3',
            voice="es-LA_SofiaV3Voice").get_result()
        audio_file.write(response.content)



class EchoBot(Client):
   def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
           self.markAsDelivered(thread_id, message_object.uid)
           self.markAsRead(thread_id)

           if author_id != self.uid:
               messenger = message_object.text
               if messenger == 'inicio':
                   self.send(Message(text="Comiensa el juego"), thread_id=thread_id, thread_type=thread_type)
                   ai_algo = Negamax(6)
                   tresenraya = TresEnRaya([Human_Player(), AI_Player(ai_algo)])
                   tresenraya.play()
               else:
                   print(messenger)
                   traduccion = traducir(messenger, language_translator)
                   print(traduccion)
                   respuesta = mensaje(traduccion,session)
                   print(respuesta)
                   voz(respuesta, service)
                   guardarPregunta(con,messenger,respuesta,traduccion)
                   #self.send(Message(text=respuesta), thread_id=thread_id, thread_type=thread_type)
                   self.sendLocalVoiceClips('output.mp3',Message(text=respuesta),thread_id=thread_id, thread_type=thread_type)


app = Flask(__name__)
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/msg', methods=['POST'])
def mensje():
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        mensaje = buscarRespuesta(con, mensaje)
        return render_template('index.html', msg=mensaje)


if __name__ == '__main__':
    bandera = False;
    #app.run()
    client = EchoBot(correo, contra)
    client.listen()


