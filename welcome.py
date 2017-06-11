# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import swiftclient
import os, json
from flask import Flask, render_template, request, url_for, redirect

auth_url = "https://identity.open.softlayer.com"
projectId = "ddbc77ad4d0343e789ab90902de1b129"
region = "dallas"
userId = "d2f34e1374b64c3ca8e29319e8907635"
username = "admin_d1c1eac7b5f54e62cc63095d148e77d8c1989516"
password = "RSsVnN6OBh]c8^)F"

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
