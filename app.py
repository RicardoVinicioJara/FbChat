from fbchat import log, Client, Message
from ibm_watson import AssistantV2, LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

correo = "ups_uclqlhf_chatt@tfbnw.net"
contra = "***123456789"
#Envia = chat_hkaepat_ups@tfbnw.net
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


def mensaje(text, session):
    message = assistant.message("633359aa-4a7e-4cfa-8ebe-78113a86ad21",
        session["session_id"],
        input={'message_type': 'text','text': text}).get_result()
    return (message['output']['generic'][0]['text'])

def traducir(text,language_translator):
    translation = language_translator.translate(
        text=text, model_id='en-es').get_result()
    return translation['translations'][0]['translation']

class EchoBot(Client):
   def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
       self.markAsDelivered(thread_id, message_object.uid)
       self.markAsRead(thread_id)
       if author_id != self.uid:
           msg = message_object.text
           print(msg)
           msg = traducir(msg, language_translator)
           print(msg)
           repuesta = mensaje(msg,session)
           print(repuesta)
           self.send(Message(text=repuesta), thread_id=thread_id, thread_type=thread_type)

client = EchoBot(correo,contra)
client.listen()

