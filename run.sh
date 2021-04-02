
if [ $(which python3)  !=  $(pwd)/server-env/bin/python3 ]; then
  ./server-env/bin/activate
fi

cd src
uvicorn main:app --reload