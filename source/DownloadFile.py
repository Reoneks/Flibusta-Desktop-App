import requests
import easygui
def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value;
def DownloadStart(url,filename,extension):
    downloaded = True
    for i in range(5):
        try:
            url_path = extension
            if extension == "pdf":
                url_path = "download"
            r = requests.get(url + "/" + url_path, stream=True)
            break
        except requests.exceptions.ConnectionError:
            if i == 4:
                #!Error="Невозможно подключится к серверу. Отмена подключения."
                downloaded = False
        except Exception as e:
            #!Error=str(e)
            downloaded = False
    if downloaded:
        if extension == "fb2":
            extension = "fb2.zip"
        filename = remove(filename, '\/:*?"<>|.')
        save_path = easygui.filesavebox(default = "C:\\Users\\User\\Downloads\\" + filename)
        if save_path != None:
            save_path += "." + extension
        else:
            return
        try:
            with open(save_path, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size = 128):
                        fd.write(chunk)
            #!Error="Файл успешно скачан."
        except Exception as e:
            #!Error=str(e)
            pass
