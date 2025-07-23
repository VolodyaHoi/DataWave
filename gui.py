import dearpygui.dearpygui as dpg
from pathlib import Path
from modules import dbconnector as dbread
import hashlib
from datetime import datetime
import os
import configparser

global count, profiles, opened_files, work_directory, work_database_name, work_author, rows_count, columns_count
count = 0
rows_count = []
columns_count = []
profiles = []
opened_files = []

def read_config():
    config = configparser.ConfigParser()

    config.read("resources\\settings.ini")  
    config_lang = config["CONFIG"]["lang"]
    config_theme = config["CONFIG"]["theme"]

    if config_lang == "eng":
        dpg.set_value(item="combo_settings_lang", value="English")
    else:
        dpg.set_value(item="combo_settings_lang", value="Russian")

    if config_theme == "light":
        dpg.set_value(item="combo_settings_theme", value="Light")
    else:
        dpg.set_value(item="combo_settings_theme", value="Dark")


def create_database():
    pass

def auth_user():
    global work_author
    user = dpg.get_value("combo_box_auth_user")
    for profile in profiles:
        if profile[0] == user:
            hash = hashlib.sha256()
            hash.update((dpg.get_value("input_text_auth_password")).encode())
            hashed = hash.hexdigest()
            password = profile[1].replace("\n", "")
            if password == hashed:
                dpg.set_value(item="input_text_auth_password", value="")
                dpg.set_value(item="combo_box_auth_user", value="")
                dpg.configure_item(item="main_window", show=True)
                dpg.configure_item(item="auth_window", show=False)
                dpg.set_viewport_title("DataWave | " + user)
                work_author = user
                break
            else:
                dpg.set_value(item="error_text", value="Wrong password!")
                dpg.configure_item(item="error_window", show=True)

def read_users():
    global profiles
    f = open("users\\userslist.txt", 'r')
    users = []
    profiles = []
    for line in f:
        username, password_hash = line.split(";")
        users.append(username)
        profiles.append([username, password_hash])
    dpg.configure_item(item="combo_box_auth_user", items=users)

    return users

def create_new_user():

    user_already_created = False
    users = read_users()
    for user in users:
        if user == dpg.get_value("input_text_create_profile"):
            user_already_created = True
            break

    if user_already_created != True:
        hash = hashlib.sha256()
        hash.update((dpg.get_value("input_text_create_password")).encode())
        hashed = hash.hexdigest()

        f = open("users\\userslist.txt", 'a')
        f.write(f"{dpg.get_value("input_text_create_profile")};{hashed}\n")
        f.close()

        dpg.set_viewport_title("DataWave | " + dpg.get_value("input_text_create_profile"))
        dpg.set_value(item="input_text_create_password", value="")
        dpg.set_value(item="input_text_create_profile", value="")
        dpg.configure_item(item="create_profile_window", show=False)
        dpg.configure_item(item="auth_window", show=False)
        dpg.configure_item(item="main_window", show=True)
    else:
        dpg.set_value(item="error_text", value="User already exist!")
        dpg.configure_item(item="error_window", show=True)
    
    

def set_windows_pos():
    dpg.configure_item(item="auth_window", pos=(1200 / 2 - 200 / 2, 600 / 2 - 220 / 2))
    dpg.configure_item(item="create_profile_window", pos=(1200 / 2 - 150 / 2, 600 / 2 - 170 / 2))
    dpg.configure_item(item="settings_window", pos=(1200 / 2 - 400 / 2, 600 / 2 - 300 / 2))
    dpg.configure_item(item="about_window", pos=(1200 / 2 - 600 / 2, 600 / 2 - 450 / 2))
    dpg.configure_item(item="author_window", pos=(1200 / 2 - 320 / 2, 600 / 2 - 120 / 2))
    dpg.configure_item(item="create_database_window", pos=(1200 / 2 - 500 / 2, 600 / 2 - 165 / 2))
    dpg.configure_item(item="create_table_window", pos=(1200 / 2 - 200 / 2, 600 / 2 - 115 / 2))
    dpg.configure_item(item="metadata_window", pos=(1200 / 2 - 200 / 2, 600 / 2 - 270 / 2))
    dpg.configure_item(item="error_window", pos=(1200 / 2 - 110 / 2, 600 / 2 - 30 / 2))
    dpg.configure_item(item="add_column_window", pos=(1200 / 2 - 200 / 2, 600 / 2 - 115 / 2))
    

def close_tab(tab_tag, button_tag):
    dpg.delete_item(tab_tag)
    dpg.delete_item(button_tag)

def read_datawave_file(file_path, reopen):
    global count, opened_files, columns_count
    columns_count = []
    visual_count = 0

    try:
        data, metadata, columns = dbread.read_datafile(file_path)
        file_name = Path(file_path).stem
        print(columns)
        if columns == ['']:
            columns_count.append([file_name, -1])
        else:
            columns_count.append([file_name, len(columns)])

        if not dpg.does_item_exist("tab" + file_name):

            opened_files.append(file_name)

            dpg.add_tab(label=file_name + ".dw", parent="main_tab_bar", tag="tab" + file_name)
            dpg.add_tab_button(label="X", parent="main_tab_bar", tag="close" + file_name, callback=lambda: close_tab("tab" + file_name, "close" + file_name))
            dpg.add_table(parent="tab" + file_name, tag="table" + file_name, header_row=True, borders_innerH=True, borders_innerV=True, borders_outerH=True, borders_outerV=True, policy=dpg.mvTable_SizingFixedFit)
            dpg.add_table_column(label="ID", parent="table" + file_name)
            for column in columns:
                if column != "":
                    dpg.add_table_column(label=column, parent="table" + file_name)

            dpg.add_table_column(label="+", parent="table" + file_name, tag="plus" + file_name)

    
            rows = 0
            for line in data:
                dpg.add_table_row(parent="table" + file_name, tag="row" + str(count))
        
                dpg.add_button(label=str(visual_count), parent="row" + str(count), callback=delete_row)

                for element in line:
                    dpg.add_text(element[1], parent="row" + str(count))
                rows+=1
                count+=1
                visual_count+=1

            dpg.add_table_row(parent="table" + file_name, tag="add_row" + file_name)
            dpg.add_button(label="+", parent="add_row" + file_name, callback=add_row)

            rows_count.append([file_name, rows])
            print(rows_count)
            if reopen == False:
                dpg.add_button(label=file_name + ".dw", width=-1, parent="opened_database", tag="new_opened_db" + file_name, callback=lambda: read_datawave_file(file_path, True))

                dpg.add_tooltip(parent="new_opened_db" + file_name, tag="tt_filename" + file_name)
                dpg.add_group(parent="tt_filename" + file_name, tag="tt_group" + file_name)
                dpg.add_text("Metadata", parent="tt_group" + file_name)
                dpg.add_separator(parent="tt_group" + file_name)
                dpg.add_text(f"Title: {metadata[0][1]}\nAuthor: {metadata[2][1]}\nDescription: {metadata[1][1]}\nCreated: {metadata[5][1]}\nModifed: {metadata[6][1]}\nSize: {metadata[7][1]}", parent="tt_group" + file_name)
        else:
            dpg.set_value("main_tab_bar", "tab"+file_name)
    except:
        pass

def read_database(database_path):
    database_name = Path(database_path).stem
    f = open(database_path, 'r')
    dpg.configure_item(item="opened_database", label=database_name + ".dwdb")
    f = [line.rstrip() for line in f]
    for table in f:
        read_datawave_file(table, False)

dpg.create_context()
dpg.create_viewport(title='DataWave', width=1200, height=600, small_icon="resources\\icon.ico", large_icon="resources\\bigicon.ico")

with dpg.font_registry():
    app_font = dpg.add_font("resources\\Nunito.ttf", 15)
    table_font = dpg.add_font("resources\\Nunito.ttf", 18)

width, height, channels, wave_texture = dpg.load_image("resources\\wave.png")

with dpg.texture_registry(show=False):
    dpg.add_static_texture(width=500, height=430, default_value=wave_texture, tag="wave_texture")


def open_database_file(sender, app_data, user_data):
    global opened_files, work_directory, work_database_name

    file_name = app_data['file_name']
    file_path = app_data['selections'][file_name.replace("*", "dwdb")]
    if file_path != "\n":
        work_directory = file_path.rsplit("\\", 1)[0]
        work_database_name = file_name.replace(".*", "")

        dpg.delete_item("opened_database")
        dpg.add_collapsing_header(label="Not opened any database", default_open=True, leaf=True, bullet=True, tag="opened_database", parent="child_explorer")

        for file in opened_files:
            dpg.delete_item("tab"+file)
            dpg.delete_item("close"+file)

        read_database(file_path)

        dpg.configure_item(item="menu_database", enabled=True)
        #dpg.configure_item(item="menu_request_constructor", enabled=True)
        dpg.configure_item(item="button_work_add_column", enabled=True)
        dpg.configure_item(item="button_work_edit_column", enabled=True)
        dpg.configure_item(item="button_work_delete_column", enabled=True)

def open_table_file(sender, app_data, user_data):

    file_name = app_data['file_name']
    file_path = app_data['selections'][file_name.replace("*", "dw")]

    dpg.delete_item("opened_database")
    dpg.add_collapsing_header(label="Not opened any database", default_open=True, leaf=True, bullet=True, tag="opened_database", parent="child_explorer")

    for file in opened_files:
        dpg.delete_item("tab"+file)
        dpg.delete_item("close"+file)

    read_datawave_file(file_path, False)


def create_path_selected(sender, app_data, user_data):
    global work_directory
    
    create_directory = app_data['file_path_name']
    work_directory = create_directory
    print(create_directory)
    
    dpg.set_value(item="input_text_create_directory", value=create_directory)

def create_database():
    global work_directory, work_database_name

    database_name = dpg.get_value(item="input_text_create_db_name")
    work_database_name = database_name

    f = open(str(work_directory) + "\\" + str(database_name) + ".dwdb", "a")
    f.write("")
    f.close()

    dpg.configure_item(item="create_database_window", show=False)

    read_database(str(work_directory) + "\\" + str(database_name) + ".dwdb")

    dpg.configure_item(item="menu_database", enabled=True)
    dpg.configure_item(item="button_work_add_column", enabled=True)
    dpg.configure_item(item="button_work_edit_column", enabled=True)
    dpg.configure_item(item="button_work_delete_column", enabled=True)
    

def create_table():
    global work_directory, work_database_name

    table_name = dpg.get_value(item="input_text_create_table_name")

    db = open(str(work_directory) + "\\" + str(work_database_name) + ".dwdb", "a")
    db.write(str(work_directory) + "\\" + str(table_name) + ".dw" + "\n")
    db.close()

    dpg.configure_item(item="metadata_window", show=True)
    dpg.configure_item(item="create_table_window", show=False)


def set_metadata():
    global work_author

    table_name = dpg.get_value(item="input_text_create_table_name")

    table_title = dpg.get_value(item="input_text_metadata_title")
    table_description = dpg.get_value(item="input_text_metadata_description")
    table_author = work_author
    table_date = datetime.now()

    date_obj = datetime.strptime(str(table_date), '%Y-%m-%d %H:%M:%S.%f')

    formatted_date = date_obj.strftime('%Y.%m.%d')

    f = open(str(work_directory) + "\\" + str(table_name) + ".dw", "w")
    
    f.write("{/title:" + table_title + "/}\n")
    f.write("{/description:" + table_description.strip() + "/}\n")
    f.write("{/author:" + table_author + "/}\n")
    f.write("{/lines:" + str(0) + "/}\n")
    f.write("{/columns:" + str(0) + "/}\n")
    f.write("{/created:" + str(formatted_date) + "/}\n")
    f.write("{/modifed:" + str(formatted_date) + "/}\n")

    f.close()

    table_size = os.path.getsize(str(work_directory) + "\\" + str(table_name) + ".dw")

    f = open(str(work_directory) + "\\" + str(table_name) + ".dw", "a")
    f.write("{/size:" + str(table_size) + "/}\n")
    f.write("{h/columns_header:{}/h}\n")
    f.close()

    read_database(str(work_directory) + "\\" + str(work_database_name) + ".dwdb")

    dpg.configure_item(item="metadata_window", show=False)

def add_column():

    current_table_rows_count = 0
    current_table_columns_count = 0
    column_name = dpg.get_value(item="input_text_column_name")


    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)
    
    table = table.replace(".dw", "")
    table_tag = "table" + table
    
    dpg.delete_item(item="plus" + table)
    dpg.add_table_column(parent=table_tag, label=column_name)
    dpg.add_table_column(parent=table_tag, label="+", tag="plus" + table)

    dpg.configure_item(item="add_column_window", show=False)
    
    for val in columns_count:
        if val[0] == table:
            current_table_columns_count = val[1]
            break

    for val in rows_count:
        if val[0] == table:
            current_table_rows_count = val[1]
            break

    updated_table = []

    f  = open(work_directory + "\\" + table + ".dw", 'r')
    data = [line.rstrip() for line in f]
    f.close()

    for line in data:
        if "{h/" in line:
            if current_table_columns_count == -1:
                line = line.replace("}/h}", column_name + "}/h}")
            else:
                line = line.replace("}/h}", ", " + column_name + "}/h}")
            updated_table.append(line)
        else:
            updated_table.append(line)
    
    f = open(work_directory + "\\" + table + ".dw", "w")
    f.write("")
    f.close()

    d = open(work_directory + "\\" + table + ".dw", "a")
    for line in updated_table:
        d.write(line + "\n")
    d.close()
    #print(updated_table)
    
    

    close_tab("tab" + table.replace(".dw", ""), "close" + table)
    
    read_datawave_file(work_directory + "\\" + table + ".dw", True)
    dpg.set_value(item="main_tab_bar", value="tab" + table)

    if current_table_rows_count != 0:
        set_values_in_new_column()



def edit_column():
    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)
    
    data, metadata, columns = dbread.read_datafile(work_directory + "\\" + table)

    with dpg.window(label="Rename column", no_collapse=True, no_move=True, no_resize=True, width=250, height=180, tag="edit_column_window"):
        dpg.configure_item(item="edit_column_window", pos=(1200 / 2 - 250 / 2, 600 / 2 - 180 / 2))
        dpg.add_text("Select column:")
        dpg.add_combo(items=columns, tag="combo_edit_column", width=-1)
        dpg.add_text("Enter new column name:")
        dpg.add_input_text(hint="Column name", tag="input_text_edit_column")
        dpg.add_separator()
        dpg.add_button(label="Accept", callback=set_new_column_name, width=-1)

def set_new_column_name():
    updated_table = []
    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)

    new_name = dpg.get_value(item="input_text_edit_column")
    column = dpg.get_value(item="combo_edit_column")

    f  = open(work_directory + "\\" + table, 'r')
    data = [line.rstrip() for line in f]
    f.close()

    for line in data:
        if "{h/" in line:
            line = line.replace(column, new_name)
            updated_table.append(line)
            break
        else:
            updated_table.append(line)
    
    f = open(work_directory + "\\" + table, "w")
    f.write("")
    f.close()

    d = open(work_directory + "\\" + table, "a")
    for line in updated_table:
        d.write(line + "\n")
    d.close()
  
    close_tab("tab" + table.replace(".dw", ""), "close" + table.replace(".dw", ""))
    
    read_datawave_file(work_directory + "\\" + table, True)
    dpg.delete_item("edit_column_window")
    dpg.set_value(item="main_tab_bar", value="tab" + table.replace(".dw", ""))

def set_values_in_new_column():
    dpg.add_window(label="Add column values", tag="add_column_values_window", no_close=True, no_move=True, no_collapse=True, width=200, height=-1)
    dpg.configure_item(item="add_column_values_window", pos=(1200 / 2 - 200 / 2, 200))
    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)
    table = table.replace(".dw", "")

    for val in rows_count:
        
        if val[0] == table:
            for i in range(0, val[1]):
                dpg.add_input_text(tag="add_value" + str(i), width=-1, parent="add_column_values_window")
            break
        
    dpg.add_button(label="Accept", width=-1, callback=set_values, parent="add_column_values_window", tag="button_add_column_values")

def set_values():
    global new_column_name

    counter = 0
    string = []

    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)

    f  = open(work_directory + "\\" + table, 'r')
    data = [line.rstrip() for line in f]
    f.close()

    for line in data:
        if "{l/" in line:
            new_element = dpg.get_value(item="add_value" + str(counter))
            line = line.replace("/l}", "")
            line = line + ";[nonetype]{" + str(new_element) + "}"
            line = line + "/l}"
            string.append(line)
            counter+=1
        else:
            string.append(line)
    

    f = open(work_directory + "\\" + table, "w")
    f.write("")
    f.close()

    d = open(work_directory + "\\" + table, "a")
    for line in string:
        d.write(line + "\n")
    d.close()
  
    close_tab("tab" + table.replace(".dw", ""), "close" + table.replace(".dw", ""))
    
    read_datawave_file(work_directory + "\\" + table, True)
    dpg.delete_item(item="add_column_values_window")
    dpg.set_value(item="main_tab_bar", value="tab" + table.replace(".dw", ""))

def add_row():
    dpg.add_window(label="Add row", tag="add_row_window", no_move=True, no_collapse=True, width=200, height=-1)
    dpg.configure_item(item="add_row_window", pos=(1200 / 2 - 200 / 2, 200))
    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)
    table = table.replace(".dw", "")
    for val in columns_count:
        if val[0] == table:
            for i in range(0, val[1]):
                dpg.add_input_text(tag="add_row_value" + str(i), width=-1, parent="add_row_window")
            count = val[1]
    dpg.add_button(label="Accept", width=-1, callback=lambda: set_row_values(count), parent="add_row_window")

def set_row_values(count):

    counter = 0

    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)

    f  = open(work_directory + "\\" + table, 'a')
    string = "{l/"
    for i in range(0, count):
        element = dpg.get_value(item="add_row_value" + str(counter))
        string = string + "[nonetype]{" + element + "};"
        counter+=1
  
    string = string[:-1]
    string = string + "/l}"

    f.write(string + "\n")
    f.close()

    close_tab("tab" + table.replace(".dw", ""), "close" + table.replace(".dw", ""))

    read_datawave_file(work_directory + "\\" + table, True)
    dpg.configure_item(item="add_row_window", show=False)
    dpg.set_value(item="main_tab_bar", value="tab" + table.replace(".dw", ""))

    dpg.delete_item(item="add_row_window")

def delete_column():
    global columns_for_delete 
    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)
    
    data, metadata, columns = dbread.read_datafile(work_directory + "\\" + table)
    
    columns_for_delete = columns

    with dpg.window(label="Delete column", no_collapse=True, no_move=True, no_resize=True, width=250, height=180, tag="delete_column_window"):
        dpg.configure_item(item="delete_column_window", pos=(1200 / 2 - 250 / 2, 600 / 2 - 180 / 2))
        dpg.add_text("Select column for delete:")
        dpg.add_combo(items=columns, tag="combo_delete_column", width=-1)
        dpg.add_separator()
        dpg.add_button(label="Accept", callback=lambda: real_delete_column(data), width=-1)

def real_delete_column(data2):
    index = -1

    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)

    column = dpg.get_value(item="combo_delete_column")
    for i in range(len(columns_for_delete)):
        if columns_for_delete[i] == column:
            index = i
            break

    with open(work_directory + "\\" + table, 'r') as f:
        data = [line.rstrip() for line in f]

    with open(work_directory + "\\" + table, "w") as f:
        for line in data:
            if "{h/" in line:
                updated_columns = columns_for_delete[:]
                updated_columns.pop(index)  
                updated_columns_str = str(updated_columns).replace("]", "}")
                updated_columns_str = updated_columns_str.replace("[", "{")
                updated_columns_str = updated_columns_str.replace("'", "")
                header_string = "{h/columns_header:" + updated_columns_str + "/h}"
                f.write(header_string + "\n")
                continue  

            elif "{l/" in line:
                break 
            else:
                f.write(line + "\n")

        for entry in data2:
            string = "{l/"
            for sub_entry in entry:
                entry_type, value = sub_entry
                if entry.index(sub_entry) == index:
                    continue 
                string += f"[{entry_type}]{{{value}}};"
            string = string[:-1] + "/l}\n"  
            f.write(string)

    columns_for_delete.pop(index)
  
    close_tab("tab" + table.replace(".dw", ""), "close" + table.replace(".dw", ""))
    
    read_datawave_file(work_directory + "\\" + table, True)
    dpg.delete_item("delete_column_window")
    dpg.set_value(item="main_tab_bar", value="tab" + table.replace(".dw", ""))

def delete_row(sender, app_data, user_data):
    
    value = dpg.get_item_label(sender)
    value = int(value)

    print(value)

    updated_table = []
    index = 0

    table = dpg.get_value(item="main_tab_bar")
    table = dpg.get_item_label(table)

    f  = open(work_directory + "\\" + table, 'r')
    data = [line.rstrip() for line in f]
    f.close()

    print(value)

    for line in data:
        if "{l/" in line:
            if index != value:
                print(index)
                print(value)
                updated_table.append(line)
            index+=1

        else:
            updated_table.append(line)
        
        
    
    f = open(work_directory + "\\" + table, "w")
    f.write("")
    f.close()

    d = open(work_directory + "\\" + table, "a")
    for line in updated_table:
        d.write(line + "\n")
    d.close()
  
    close_tab("tab" + table.replace(".dw", ""), "close" + table.replace(".dw", ""))
    
    read_datawave_file(work_directory + "\\" + table, True)
    dpg.delete_item("edit_column_window")
    dpg.set_value(item="main_tab_bar", value="tab" + table.replace(".dw", ""))

with dpg.file_dialog(label="Select DataWave db file", directory_selector=False, modal=True, show=False, callback=open_database_file, tag="database_file_open_dialog", width=500 ,height=400):
    dpg.add_file_extension(".*")
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension(".dwdb", color=(255, 0, 255, 255), custom_text="[DataWave Database]")

with dpg.file_dialog(label="Select DataWave table file", directory_selector=False, modal=True, show=False, callback=open_table_file, tag="table_file_open_dialog", width=500 ,height=400):
    dpg.add_file_extension(".*")
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension(".dw", color=(255, 0, 255, 255), custom_text="[DataWave Table]")

dpg.add_file_dialog(
    directory_selector=True, show=False, callback=create_path_selected, tag="create_database_folder_dialog",
    width=700 ,height=400)



with dpg.window(label="Add column", no_collapse=True, no_move=True, no_resize=True, width=200, height=115, show=False, modal=True, tag="add_column_window"):
    dpg.add_text("Select column name:", tag="add_select_column_name")
    dpg.add_input_text(hint="Column name", tag="input_text_column_name", width=-1)
    dpg.add_separator()
    dpg.add_button(label="Accept", callback=add_column, width=-1, tag="add_column_accept")

with dpg.window(label="* Error!", no_resize=True, no_collapse=True, no_move=True, width=110, height=30, no_close=True, tag="error_window", modal=True):
    dpg.add_text("", tag="error_text")
    dpg.add_spacer(height=13)
    dpg.add_button(label="Close", width=-1, callback=lambda: dpg.configure_item(item="error_window", show=False), tag="error_window_close")

with dpg.window(label="Write metadata", no_collapse=True, no_resize=True, width=200, height=270, no_move=True, tag="metadata_window", modal=True, show=False):
    dpg.add_text("Title:", tag="meta_title_text")
    dpg.add_input_text(hint="Any title..", width=-1, tag="input_text_metadata_title")

    dpg.add_text("Description:")
    dpg.add_input_text(hint="Any description..", multiline=True, width=-1, tag="input_text_metadata_description")
    dpg.add_separator()
    dpg.add_button(label="Accept", width=-1, callback=set_metadata)

with dpg.window(label="Create table", no_collapse=True, no_move=True, width=200, no_resize=True, height=115, tag="create_table_window", show=False):
    dpg.add_text("Enter table name")
    dpg.add_input_text(hint="Table name..", width=-1, tag="input_text_create_table_name")
    dpg.add_separator()
    dpg.add_button(label="Create", width=-1, callback=create_table)

with dpg.window(label="Create database", no_collapse=True, tag="create_database_window", no_move=True, no_resize=True, height=165, width=500, show=False):
    dpg.add_text("Select folder for database:")
    with dpg.group(horizontal=True):
        dpg.add_input_text(hint="Folder path..", readonly=True, tag="input_text_create_directory")
        dpg.add_button(label="Select", width=-1, callback=lambda: dpg.configure_item(item="create_database_folder_dialog", show=True))
    dpg.add_text("Enter database name:")
    dpg.add_input_text(hint="Database name", width=-1, tag="input_text_create_db_name")
    dpg.add_separator()
    dpg.add_button(label="Create", width=-1, callback=create_database)

with dpg.window(label="Author", width=320, height=120, no_move=True, no_resize=True, tag="author_window", no_collapse=True, show=False, modal=True):
    dpg.add_text("Created with love by VolodyaHoi [7nation] in 2025 <3")
    with dpg.group(horizontal=True):
        dpg.add_text("My github:", bullet=True)
        dpg.add_text("https://github.com/VolodyaHoi", color=(255, 255, 255))
    with dpg.group(horizontal=True):
        dpg.add_text("My telegram:", bullet=True)
        dpg.add_text("https://t.me/notavl", color=(255, 255, 255))

with dpg.window(label="About", width=600, height=450, no_move=True, no_resize=True, tag="about_window", no_collapse=True, show=False, modal=True):
    dpg.add_text("This project was created for a graduation project and is a database management system.")
    with dpg.collapsing_header(label="Possible errors `n` bugs"):
        dpg.add_button(label="1. ? instead of letters", tag="note1", width=-1)
    dpg.add_separator()
    with dpg.group(horizontal=True):
        dpg.add_text("Source code and more information:", bullet=True)
        dpg.add_text("https://github.com/DataWave", color=(255, 255, 255))
    with dpg.group(horizontal=True):
        dpg.add_text("Dear PyGui:", bullet=True)
        dpg.add_text("https://github.com/hoffstadt/DearPyGui", color=(255, 255, 255))

with dpg.window(label="Settings", width=400, height=300, no_resize=True, no_collapse=True, tag="settings_window", no_move=True, show=False, modal=True):
    with dpg.collapsing_header(label="UI"):
        dpg.add_combo(items=["Light", "Dark"], label="UI Style", tag="combo_settings_theme")
        dpg.add_combo(items=["Russian", "English"], label="UI Language", tag="combo_settings_lang")
    dpg.add_separator()
    dpg.add_button(label="Apply settings", width=-1)

#with dpg.window(label="Request constructor", no_resize=True, show=False, tag="request_constructor_window", modal=True):
    #with dpg.group(horizontal=True):
        #with dpg.group():
            #with dpg.child_window(height=150, width=450):
                #with dpg.group(horizontal=True):
                    #dpg.add_button(label="GET")
                    #dpg.add_text("->")
                    #dpg.add_button(label="tablename")
            #with dpg.child_window(height=115, width=450):
                #with dpg.group():
                    #dpg.add_button(label="GET", width=-1)
                    #dpg.add_button(label="FROM", width=-1)
                    #dpg.add_button(label="IN", width=-1)
                    #dpg.add_button(label="WHERE", width=-1)
        #with dpg.child_window(width=250, height=270, show=False):
            #dpg.add_text(label="hi")

    #dpg.add_separator()
    #dpg.add_button(label="Execute", width=-1, height=30)

with dpg.window(label="Create new profile", width=150, height=170, no_resize=True, no_collapse=True, tag="create_profile_window", no_move=True, show=False):
    dpg.add_text("Enter profile name")
    dpg.add_input_text(hint="Profile name..", width=-1, tag="input_text_create_profile")
    dpg.add_text("Enter profile password")
    dpg.add_input_text(hint="Password", width=-1, password=True, tag="input_text_create_password")
    dpg.add_separator()
    dpg.add_button(label="Create", width=-1, callback=create_new_user)

with dpg.window(label="Authorization", tag="auth_window", no_resize=True, no_close=True, no_collapse=True, width=200, height=220, no_move=True, show=True):
    dpg.add_text("          Welcome to DataWave!")
    dpg.add_text("Select profile:")
    dpg.add_combo(width=-1, tag="combo_box_auth_user")
    dpg.add_text("Enter password for selected profile:")
    dpg.add_input_text(password=True, hint="Enter password..", width=-1, tag="input_text_auth_password")
    dpg.add_separator()
    dpg.add_button(label="Enter", width=-1, callback=auth_user)
    dpg.add_separator()
    dpg.add_button(label="Create new profile", width=-1, callback=lambda: dpg.configure_item(item="create_profile_window", show=True))

with dpg.window(label="", tag="main_window", show=False):
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            with dpg.menu(label="Open"):
                dpg.add_menu_item(label="Database", callback=lambda: dpg.configure_item(item="database_file_open_dialog", show=True))
                dpg.add_menu_item(label="Table", callback=lambda: dpg.configure_item(item="table_file_open_dialog", show=True))
            dpg.add_menu_item(label="Create database", callback=lambda: dpg.configure_item(item="create_database_window", show=True))
            #dpg.add_menu_item(label="Save")
            dpg.add_separator()
            dpg.add_menu_item(label="Reset app")
        with dpg.menu(label="Database", enabled=False, tag="menu_database"):
            with dpg.menu(label="Table"):
                dpg.add_menu_item(label="Create new table", callback=lambda: dpg.configure_item(item="create_table_window", show=True))
                dpg.add_menu_item(label="Delete table")
            #with dpg.menu(label="Properties"):
                #dpg.add_menu_item(label="Open database metadata")
                #dpg.add_menu_item(label="Change password")
        #with dpg.menu(label="Request constructor", enabled=False, tag="menu_request_constructor"):
            #dpg.add_menu_item(label="Open", callback=lambda: dpg.configure_item("request_constructor_window", show=True))
        dpg.add_menu_item(label="Settings", callback=lambda: dpg.configure_item("settings_window", show=True))
        with dpg.menu(label="Help"):
            dpg.add_menu_item(label="About", callback=lambda: dpg.configure_item("about_window", show=True))
            dpg.add_menu_item(label="Author", callback=lambda: dpg.configure_item("author_window", show=True))
    with dpg.group(horizontal=True):
        with dpg.group():
            with dpg.child_window(width=250, height=350, tag="child_explorer"):
                dpg.add_text("Explorer")
                dpg.add_collapsing_header(label="Not opened any database", default_open=True, leaf=True, bullet=True, tag="opened_database")
            with dpg.child_window(width=250):
                dpg.add_text("Workbench")
                dpg.add_button(label="Add column", width=-1, callback=lambda: dpg.configure_item(item="add_column_window", show=True), enabled=False, tag="button_work_add_column")
                dpg.add_button(label="Edit column", width=-1, callback=edit_column, tag="button_work_edit_column", enabled=False)
                dpg.add_button(label="Delete column", width=-1, callback=delete_column, tag="button_work_delete_column", enabled=False)
        with dpg.child_window():
            dpg.add_image("wave_texture", tag="texture_tag", pos=(930 / 2 - 500 / 2, 525 / 2 - 430 / 2)) 
            dpg.add_tab_bar(tag="main_tab_bar")

    dpg.bind_font(app_font)


    with dpg.tooltip(parent="note1"):
        dpg.add_text("This problem may occur when entering text. Check using the English layout. [The input fields ONLY support the English layout!]")

with dpg.theme() as global_theme:

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255,255,255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (181,187,213), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (88,138,189), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (88,138,189), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (164,204,237), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Separator, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, (57,97,148), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, (42,58,83), category=dpg.mvThemeCat_Core)



        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 3, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, category=dpg.mvThemeCat_Core)

with dpg.theme() as node_item_theme:

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (42,58,83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (57,97,148), category=dpg.mvThemeCat_Core)

        dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)
dpg.bind_item_theme(item="note1", theme=node_item_theme)

set_windows_pos()
read_users()
read_config()

#rgb(181,187,213)
#rgb(42,58,83) | 2A3A53
#rgb(57,97,148) | 396194
#rgb(88,138,189) | 588ABC
#rgb(130,175,222) | 82AFDE
#rgb(164,204,237) | A4CCED


# text - A4CCED
# disabled text - 588ABC
# windowbg - 396194
# childbg - 588ABC
# popupbg - 396194
# border - 2A3A53
# framebg - 588ABC
# titleactivebg - 2A3A53
# titlebg - 2A3A53
# menubarbg - 2A3A53FF
# scrollbg - A4CCED
# scrollbargrab - 2A3A53
# scrollbaractivenhovered - 396194
# buttonNheaderNseparator - 2A3A53
#buttonhovered - 396194
# tab - 2A3A53
# tabactive - 396194
# tableheaderbg - 2A3A53
# tableborderlightNstrong - 396194
# resizegrip - 2A3A53

# window rounding - 10
#child rounding - 4
# frame rounding - 2
#scroll bar rouding - 3
# tabrounding - 5
#title alightn - 0.50
#bbutton alighn - 0.50


dpg.set_primary_window("main_window", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()