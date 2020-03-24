from pydblite import Base
from app import dice_api

dice_api.main()
db = Base("main.pdl")
db.create('game_id', mode='override')
print("hi")

