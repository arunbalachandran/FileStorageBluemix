import swiftclient
import os, json
from flask import Flask, render_template, request, url_for, redirect

if os.getenv('VCAP_SERVICES'):
    credentials = json.loads(os.getenv('VCAP_SERVICES'))
else:
    with open('VCAP_SERVICES.json') as fp:
        credentials = json.load(fp)['VCAP_SERVICES']
objectstorage_cred = credentials['Object-Storage'][0]['credentials']
auth_url = objectstorage_cred['auth_url']
projectId = objectstorage_cred['projectId']
region = objectstorage_cred['region']
userId = objectstorage_cred['userId']
username = objectstorage_cred['username']
password = objectstorage_cred['password']

conn = swiftclient.Connection(
    key=password,
    authurl=auth_url+'/v3',
    auth_version='3',
    os_options={
        'project_id': projectId,
        'user_id': userId,
        'region_name': region
    }
)

container_name = 'defaultcontainer'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def Welcome():
    if request.method == 'GET':
        files_data = []
        for data in conn.get_container(container_name)[1]:
            files_data.append(data)
        print (files_data)
        return render_template('index.html', files_data=files_data, containername=container_name)
    elif request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            return json.dumps({'error': 'Invalid file'}), 400, {'ContentType': 'application/json'}
        else:
            filename = f.filename
            filecontent = f.stream.read()
            conn.put_object(container_name, filename, filecontent, 'text/plain')
            return json.dumps({'success': 'Successful upload of file'}), 200, {'contentType': 'application/json'}

@app.route('/fileOperation', methods=['POST'])
def DownloadDeleteFiles():
    if request.method == 'POST':
        operation_keys = request.form.keys()
        selected_operation = [i for i in operation_keys]
        print ('Selected operations are', selected_operation)
        list_of_files = request.form.getlist('selectedfiles')
        print ('Selected files are', list_of_files)
        file_to_download = list_of_files[0]
        if 'Delete' in selected_operation:
            conn.delete_object(container_name, file_to_download)
            return redirect(url_for('Welcome'))
        elif 'Download' in selected_operation:
            file_content = conn.get_object(container_name, file_to_download)[1]
            response = make_response(file_content)
            response.headers['Content-Disposition'] = 'attachment; filename=' + file_to_download
            return response

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
