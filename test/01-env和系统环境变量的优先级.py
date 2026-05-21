# test/01-env鍜岀郴缁熺幆澧冨彉閲忕殑浼樺厛绾?py

import os
from dotenv import load_dotenv

# 鍔犺浇.env鏂囦欢
load_dotenv(override=True)

def _mask(value):
    if not value:
        return '<unset>'
    if len(value) <= 8:
        return '<set>'
    return f'{value[:4]}...{value[-4:]}'

print(_mask(os.getenv('OPENAI_API_KEY')))

# 瀹為檯榛樿閫昏緫锛歰verride=False
# - 濡傛灉绯荤粺鐜鍙橀噺涓嶅瓨鍦?鈫?鐢?env閲岀殑鍊?
# - 濡傛灉绯荤粺鐜鍙橀噺宸插瓨鍦?鈫?绯荤粺鍙橀噺浼樺厛绾ф洿楂?
# 鎯宠.env瑕嗙洊绯荤粺鍙橀噺锛岄渶鏄惧紡浼?override=True
# load_dotenv(override=True)

# 绀轰緥锛氬亣璁剧郴缁熸湁鐜鍙橀噺 MY_KEY=system_val锛?env閲?MY_KEY=dotenv_val
print(os.getenv("MY_KEY"))
# load_dotenv() 鈫?杈撳嚭 system_val锛堢郴缁熶紭鍏堢骇楂橈級
# load_dotenv(override=True) 鈫?杈撳嚭 dotenv_val锛?env瑕嗙洊绯荤粺锛
