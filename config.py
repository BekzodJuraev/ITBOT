import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()
DOMAIN=env('DOMAIN')
ADMIN=env('ADMIN')
CHANEL_ADS=env('CHANEL_ADS')
CHANEL_SUPPORT=env('CHANEL_SUPPORT')
CHANEL_MAIN=env('CHANEL_MAIN')
TOKEN_BOT=env('TOKEN_BOT')
DEBUG = env.bool('DEBUG', default=False)