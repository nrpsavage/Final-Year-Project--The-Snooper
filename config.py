from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key)

# Key for the login system encryption.
SECRET_KEY = b'6NhVr31YvokE5C4_jFrs9caTsx19J4KTE8ArbXcFdA4='

# Secret key for the application.
app_key = "123321"

# API keys that I might potentially use in the application.
# NVD API Key - 49a35609-1545-41c4-83d4-9e5ffc4eb033  
# pdfcrowd API Key - 893659497f3f5860e596ddfef8a65375
# Serp API Key - aa4e0796efda079482a2f396a4c38455611928b4b843bf2c43a94685f564fcd5