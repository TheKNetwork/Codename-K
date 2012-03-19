import oauth2
import time
import os
import base64

def get_whiteboard_url(url, script_name, whiteboard_title, whiteboard_hash, user_type, user_name, user_id):
    url = 'https://knetwork.tutortrove.com/api_v1/SSO/whiteboard'
    method='GET'
    params = {                                            
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        "user_id": base64.urlsafe_b64encode(os.urandom(30)),
        "user_name": user_name, 
        "user_type": user_type,
        "whiteboard_hash": whiteboard_hash,
        "whiteboard_title": whiteboard_title
        }       
    
    
    consumer = oauth2.Consumer(key='152',secret='9b578551e3509fb425fab9f6c501af87')
    params['oauth_consumer_key'] = consumer.key
 
    req = oauth2.Request(method=method, url=url, parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)
    return req.to_url()
