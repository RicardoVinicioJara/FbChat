import json
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticatorT = IAMAuthenticator('0Iobj63HD2qz6ChKXOCkc1kARMJ8E9-Gkq1045FQIGf7')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticatorT)
language_translator.set_service_url('https://gateway.watsonplatform.net/language-translator/api')


def traducir(text,language_translator):
    translation = language_translator.translate(
        text=text, model_id='en-es').get_result()
    print(translation['translations'][0]['translation'])
    print(json.dumps(translation, indent=2, ensure_ascii=False))

traducir("How much",language_translator)