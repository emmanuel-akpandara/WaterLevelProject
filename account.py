import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
from config import FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL, FIREBASE_CLIENT_ID, FIREBASE_AUTH_URI, FIREBASE_TOKEN_URI, FIREBASE_AUTH_PROVIDER_CERT_URL, FIREBASE_CLIENT_CERT_URL, FIREBASE_UNIVERSE_DOMAIN


# cred = credentials.Certificate({
#     "type": "service_account",
#     "project_id": FIREBASE_PROJECT_ID,
#     "private_key_id": FIREBASE_PRIVATE_KEY_ID,
#     "private_key": FIREBASE_PRIVATE_KEY,
#     "client_email": FIREBASE_CLIENT_EMAIL,
#     "client_id": FIREBASE_CLIENT_ID,
#     "auth_uri": FIREBASE_AUTH_URI,
#     "token_uri": FIREBASE_TOKEN_URI,
#     "auth_provider_x509_cert_url": FIREBASE_AUTH_PROVIDER_CERT_URL,
#     "client_x509_cert_url": FIREBASE_CLIENT_CERT_URL,
#     "universe_domain": FIREBASE_UNIVERSE_DOMAIN
# })
cred = credentials.Certificate('gitguardians-app-2e4d25999060.json')
firebase_admin.initialize_app(cred)
def app():
# Usernm = []
    st.title('Welcome to the :violet[Water Guardian] portal :sunglasses:')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''



    def f(): 
        try:
            user = auth.get_user_by_email(email)
            print(user.uid)
            st.session_state.username = user.uid
            st.session_state.useremail = user.email
            
            global Usernm
            Usernm=(user.uid)
            
            st.session_state.signedout = True
            st.session_state.signout = True    
  
            
        except: 
            st.warning('Login Failed')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False   
        st.session_state.username = ''


        
    
        
    if "signedout"  not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False    
        

        
    
    if  not st.session_state["signedout"]: # only show if the state is False, hence the button has never been clicked
        choice = st.selectbox('Login/Signup',['Login','Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password',type='password')
        

        
        if choice == 'Sign up':
            username = st.text_input("Enter  your unique username")
            
            if st.button('Create my account'):
                user = auth.create_user(email = email, password = password,uid=username)
                
                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')
                st.balloons()
        else:
            # st.button('Login', on_click=f)          
            st.button('Login', on_click=f)
            
            
    if st.session_state.signout:
                st.text('Name '+st.session_state.username)
                st.text('Email id: '+st.session_state.useremail)
                st.button('Sign out', on_click=t) 
            
                
    

                            
    def ap():
        st.write('Posts')
