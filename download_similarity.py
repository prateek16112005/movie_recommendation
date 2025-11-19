import gdown

url = "https://drive.google.com/file/d/1aPl5edtqHvg9mAYIBpqlSYQV8Y8LjY3H/view?usp=sharing"
output = "similarity.pkl"

gdown.download(url, output, quiet=False)
