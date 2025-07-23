# Module for reading DataWave Files

meta_list = ["title", "description", "author", "lines", "columns", "created", "modifed", "size"]

title_checked = False
description_checked = False
author_checked = False
lines_checked = False
columns_checked = False
created_checked = False
modifed_checked = False
size_checked = False

database_meta_data = []


def read_datafile(file):
    meta_data = []
    db_data = []
    columns = []
    
    try:
        f = open(file, 'r')

        file_data = [line.rstrip() for line in f]
        for line in file_data:
            element_array = []
        #print(line)
            try:

                if "{h/" in line:
                    line = line.replace("{h/", "")
                    line = line.replace("/h}", "")
                    type, columns_names = line.split(":")
            
                    columns_names = columns_names.replace("{", "")
                    columns_names = columns_names.replace("}", "")
                    columns_names = columns_names.replace(" ", "")
                    for name in columns_names.split(","):
                        columns.append(name)

                elif "{/" in line:
                    line = line.replace("{/", "")
                    line = line.replace("/}", "")
                    meta_type, value = line.split(":")
                    meta_data.append([meta_type, value])
                elif "{l/" in line:
            
                    line = line.replace("{l/", "")
                    line = line.replace("/l}", "")

                    elements_in_rows = line.split(";")
                    element_array = []
                    for element in elements_in_rows:
                
                
                        element = element.replace("[", "")
                        element = element.replace("}", "")
                        value_type, value = element.split("]{")
                        element_array.append([value_type, value])
                
                    db_data.append(element_array)
        
                else:
                    pass

            except:
                pass

        f.close()
        return db_data, meta_data, columns
    except:
        pass

def check_metadata(meta):
    for meta_type, value in meta_data:
        if meta_type == "title":
            title_checked = True
        elif meta_type == "description":
            description_checked = True
        elif meta_type == "author":
            author_checked = True
        elif meta_type == "lines":
            lines_checked = True
        elif meta_type == "columns":
            columns_checked = True
        elif meta_type == "created":
            created_checked = True
        elif meta_type == "modifed":
            modifed_checked = True
        elif meta_type == "size":
            size_checked = True

def set_not_finded_metadata():
    if title_checked == False:
        meta_data.append(["title", "untitled"])
    if description_checked == False:
        meta_data.append(["description", "without a description"])
    if author_checked == False:
        meta_data.append(["author", "unknown"])
    if lines_checked == False:
        meta_data.append(["lines", "noinfo"])
    if columns_checked == False:
        meta_data.append(["columns", "noinfo"])
    if created_checked == False:
        meta_data.append(["created", "noinfo"])
    if modifed_checked == False:
        meta_data.append(["modifed", "noinfo"])
    if size_checked == False:
        meta_data.append(["size", "noinfo"])


# read data

def get_elements_in_row():
    count_elements_in_row = len(db_data[0])

    for row in range(0, len(db_data)):
    
        if count_elements_in_row < len(db_data[row]):
            count_elements_in_row = len(db_data[row])

def set_not_finded_data(count_elements_in_row):
    for row in range(0, len(db_data)):
        try:
            for element in range(0, count_elements_in_row):
            #print(f"ROW №: {row}. TYPE: {db_data[row][element][0]}, VALUE: {db_data[row][element][1]}")
                pass
        except:
            db_data[row].append(["NONE", "NULL"])
        #print(f"ROW №: {row}. TYPE: NONE, VALUE: NULL")

# read db

def read_database_file(database):
    for line in database.splitlines():
        if "{t/" in line:
            line = line.replace("{t/", "")
            line = line.replace("/t}", "")
            array = line.split("/")
        #print(array[len(array)-1])

            table_name, ex = array[len(array)-1].split(".")
        #print(table_name)
        #print(ex)
        elif "{/" in line:
            line = line.replace("{/", "")
            line = line.replace("/}", "")
            meta_type, value = line.split(":")
            database_meta_data.append([meta_type, value])
        else:
        #print("bad line")
            pass



