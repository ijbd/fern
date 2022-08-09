from flask import Flask, render_doc

app = Flask()

@route('/')
def index(self):
	return render_doc('index.html')



if __name__ == "__main__":
	app.run()