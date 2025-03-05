import pandas as pd
import streamlit as st
           
st.title("知识库")
user_id = st.session_state.user_id
manager = st.session_state.manager
conn = st.session_state.conn

cursor = conn.cursor()
cursor.execute('SELECT file_name FROM repository_data WHERE user_id = ?',(user_id,))
result = cursor.fetchall()
file_names = (item[0] for item in result)
col0,col1 = st.columns([2,1],vertical_alignment='bottom')
with col0:
    option = st.selectbox(
        label="",
        options=file_names,
        index=None,
        placeholder="选择知识库中的文件以浏览文档..."
    )
with col1:
    if st.button(label='删除文件',use_container_width=True):
        pass

ret_list = []
if option:
    key_doc_zip, tip_zip = manager.get_repository(user_id=user_id,file_name=option)
    if key_doc_zip:
        for item in key_doc_zip:
            ret_list.append(
                {"file_name":item[0], "key_id":item[1],"key":item[2],"doc_id":item[3],"doc":item[4],"is_sel":True}
            )
    if tip_zip:
        for item in tip_zip:
            ret_list.append(
                {"file_name":item[0], "key_id":None,"key":None,"doc_id":item[1],"doc":item[2],"is_sel":True}
            )
    if not key_doc_zip and not tip_zip:
        ret_list = [
            {"file_name":None, "key_id":None,"key":None,"doc_id":None,"doc":None}
        ]
else:
    ret_list = [
        {"file_name":None, "key_id":None,"key":None,"doc_id":None,"doc":None}
    ]
    
df = pd.DataFrame(ret_list)
st.data_editor(
    data=df,
    column_config={
        "file_name": st.column_config.TextColumn(
            label="来自文件",
        ),
        "key_id": st.column_config.TextColumn(
            label="关键字ID",
        ),
        "key": st.column_config.TextColumn(
            label="关键字",
        ),
        "doc_id": st.column_config.TextColumn(
            label="文档ID",
        ),
        "doc": st.column_config.TextColumn(
            label="文档",
        ),
        "is_sel": st.column_config.CheckboxColumn(
            label="是否启用",
        ),
    },
    disabled=["file_name","key_id","key","doc_id","doc"],
    hide_index=True,
    use_container_width=True
)

@st.dialog("上传文件到知识库",width="large")
def upload():
    uploaded_files = st.file_uploader(
        "文件类型限制为txt文件，支持同时上传多个文件", accept_multiple_files=True
    )
    if st.button(label="上传",use_container_width=True):
        cursor = conn.cursor()
        cursor.execute('SELECT file_name FROM repository_data WHERE user_id = ?',(user_id,))
        result = cursor.fetchall()
        stored_file_names = [item[0] for item in result]
        with st.container(height=300):
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                st.write(f'解析文件{file_name}...')
                if file_name in stored_file_names:
                    st.write(f'知识库已有文件名为{file_name}的文件，请更换该文件的文件名重试')
                    continue
                file_content = uploaded_file.read().decode("utf-8")
                lines = file_content.splitlines()
                for line in lines:
                    line = line.rstrip()
                    st.write(line)
                    manager.add_doc_to_vectordb(doc=line,user_id=user_id,file_name=file_name)   
                cursor.execute('INSERT INTO repository_data(user_id, file_name) VALUES(?,?)',(user_id, file_name))
                conn.commit()
                st.write(f'解析文件{file_name}完毕')
            st.write("所有文件解析完毕")
    if st.button("返回",use_container_width=True):
        st.rerun()

if st.button("上传文件到知识库",use_container_width=True):
    upload()