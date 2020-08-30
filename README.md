# dir_watcher


#### driver.py
*   Driver file to run and start monitoring specific directory.

#### watcher.py
*   Monitors the given directory continuously. It will detect the new file and takes appropriate action.

#### zipper.py
*   Creates the password protected zip file of newly detected file from watcher.py
*   After creating the zip file, it will store the file in **todecode** folder under current directory.

#### pii_filter.py
*   Extracts the newly detected zip file from watcher.py and performs pii filtering on the content of file.
*   After performing pii filtering, it will be stored in **filtered** folder under current directory


### How to run the Application.

#### Python3 should be installed to run this application.

*   run the driver.py file by **python driver.py** (it will create two threads. one will monitor provided dir for txt file and another will monitor todecode dir for new zi file).
*   It will ask for directory path to monitor for txt files. provide the full path.
    e.g. D:\\Bharat - Cisco DCN\\Bharat\\Assign (escape \ in windows)
*   As new file detected in the provided dir, it will create **todecode** folder in current dir and will store the zip file in it.
*   As new zip detected in todecode dir, second thread will read it and performs pii filtering on it.
*   After performing pii filtering, it will store the filtered file in **filtered** under current folder with filtered_<original_file>.txt

[still there are lots of points of improvement...:)]